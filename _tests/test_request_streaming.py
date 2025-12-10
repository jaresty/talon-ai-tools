import unittest
import json
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from talon_user.lib.requestLifecycle import RequestLifecycleState
except ModuleNotFoundError:  # pragma: no cover - handled by bootstrap guard below
    RequestLifecycleState = None  # type: ignore[assignment]

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelHelpers
    from talon_user.lib.modelHelpers import send_request, GPTRequestError
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.requestState import RequestState

    class StreamingTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.request = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "hi"}],
                    }
                ]
            }
            GPTState.text_to_confirm = ""
            GPTState.last_response = ""
            GPTState.last_raw_response = None
            if hasattr(GPTState, "last_lifecycle"):
                delattr(GPTState, "last_lifecycle")

        def test_streaming_accumulates_chunks(self) -> None:
            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return True
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_stream(_req, _req_id):
                GPTState.text_to_confirm = "Hello 🌍"
                return "Hello 🌍"

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers,
                    "_send_request_streaming",
                    side_effect=fake_stream,
                ),
                patch.object(
                    modelHelpers,
                    "send_request_internal",
                    side_effect=AssertionError("should not call sync"),
                ),
            ):
                result = send_request(max_attempts=1)
                self.assertEqual(result["text"], "Hello 🌍")
                self.assertEqual(GPTState.text_to_confirm, "Hello 🌍")
                self.assertEqual(GPTState.last_response, "Hello 🌍")
                # Logical RequestLifecycle status should be completed for happy-path streaming.
                if RequestLifecycleState is not None:
                    self.assertIsInstance(
                        GPTState.last_lifecycle, RequestLifecycleState
                    )
                    self.assertEqual(GPTState.last_lifecycle.status, "completed")

        def test_streaming_honours_cancel(self) -> None:
            states = [
                RequestState(cancel_requested=True),
            ]

            def fake_state():
                return states.pop(0) if states else RequestState(cancel_requested=True)

            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return True
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_stream(_req, _req_id):
                # Simulate cancellation mid-stream; current_state will report
                # cancel_requested=True immediately so send_request returns empty.
                return "Hello"

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers,
                    "_send_request_streaming",
                    side_effect=fake_stream,
                ),
                patch.object(modelHelpers, "current_state", side_effect=fake_state),
                patch.object(
                    modelHelpers,
                    "send_request_internal",
                    side_effect=AssertionError("should not call sync"),
                ),
            ):
                result = send_request(max_attempts=1)
                self.assertEqual(result.get("text"), "")

        def test_streaming_cancelled_sets_lifecycle_cancelled(self) -> None:
            """When the streaming helper raises CancelledRequest, lifecycle ends cancelled."""

            if RequestLifecycleState is None:
                self.skipTest("RequestLifecycleState unavailable")

            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return True
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_stream(_req, _req_id):
                raise modelHelpers.CancelledRequest()

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers,
                    "_send_request_streaming",
                    side_effect=fake_stream,
                ),
                patch.object(
                    modelHelpers,
                    "send_request_internal",
                    side_effect=AssertionError("should not call sync"),
                ),
            ):
                result = send_request(max_attempts=1)
                self.assertEqual(result.get("text"), "")
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "cancelled")

        def test_streaming_falls_back_to_non_stream_json_response(self) -> None:
            """Characterise the non-stream JSON fallback path in _send_request_streaming."""

            class FakeResponse:
                status_code = 200

                def __init__(self) -> None:
                    self.headers = {"content-type": "application/json"}

                def json(self):
                    return {"choices": [{"message": {"content": "Hello world"}}]}

            def fake_get(key, default=None):
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                # Force streaming enabled so send_request takes the streaming branch.
                if key == "user.model_streaming":
                    return True
                return default

            def fake_post(url, headers=None, json=None, timeout=None, stream=None):  # noqa: ARG001
                return FakeResponse()

            # Start from a simple request payload.
            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(modelHelpers.requests, "post", side_effect=fake_post),
                patch.object(
                    modelHelpers,
                    "_should_show_response_canvas",
                    return_value=False,
                ),
            ):
                # Call the internal streaming helper directly so we exercise the
                # JSON fallback path.
                text = modelHelpers._send_request_streaming(
                    GPTState.request, "req-json"
                )

            self.assertEqual(text, "Hello world")
            self.assertEqual(GPTState.text_to_confirm, "Hello world")
            if RequestLifecycleState is not None:
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "completed")

        def test_streaming_sse_iter_lines_accumulates_chunks(self) -> None:
            """Characterise the core SSE streaming path in _send_request_streaming."""

            class FakeResponse:
                status_code = 200

                def __init__(self) -> None:
                    self.headers = {"content-type": "text/event-stream"}

                def iter_lines(self):
                    payloads = [
                        {"choices": [{"delta": {"content": "Hello "}}]},
                        {"choices": [{"delta": {"content": "world"}}]},
                    ]
                    for payload in payloads:
                        line = "data: " + json.dumps(payload)
                        yield line.encode("utf-8")
                    yield b"data: [DONE]"

            def fake_get(key, default=None):
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                if key == "user.model_streaming":
                    return True
                return default

            # Start from a simple request payload.
            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers.requests, "post", return_value=FakeResponse()
                ),
                patch.object(
                    modelHelpers,
                    "_should_show_response_canvas",
                    return_value=False,
                ),
            ):
                text = modelHelpers._send_request_streaming(GPTState.request, "req-sse")

            self.assertEqual(text, "Hello world")
            self.assertEqual(GPTState.text_to_confirm, "Hello world")
            if RequestLifecycleState is not None:
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "completed")

        def test_streaming_timeout_raises_gpt_request_error(self) -> None:
            """Characterise timeout handling in _send_request_streaming."""

            def fake_get(key, default=None):
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 5
                if key == "user.model_streaming":
                    return True
                return default

            # Start from a simple request payload.
            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }

            class DummyTimeout(Exception):
                pass

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers.requests,
                    "post",
                    side_effect=DummyTimeout,
                ),
            ):
                # Provide a Timeout type on the stubbed requests module so the
                # streaming helper's "except requests.exceptions.Timeout" branch
                # is exercised.
                modelHelpers.requests.exceptions = type(
                    "_Exc",
                    (),
                    {"Timeout": DummyTimeout},
                )
                with self.assertRaises(GPTRequestError) as ctx:
                    modelHelpers._send_request_streaming(
                        GPTState.request, "req-timeout"
                    )

            self.assertEqual(getattr(ctx.exception, "status_code", None), 408)
            self.assertIn("Request timed out after", str(ctx.exception))
            if RequestLifecycleState is not None:
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "errored")

else:
    if not TYPE_CHECKING:

        class StreamingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
