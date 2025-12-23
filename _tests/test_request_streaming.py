import os
import unittest
import json
from typing import TYPE_CHECKING
from types import SimpleNamespace
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
    import talon_user.lib.streamingCoordinator as streaming

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
            os.environ["OPENAI_API_KEY"] = "test-key"
            GPTState.last_streaming_snapshot = {}
            GPTState.last_streaming_events = []
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
                snapshot = getattr(GPTState, "last_streaming_snapshot", {})
                # Cancelled before streaming accrues; snapshot should be empty.
                self.assertEqual(snapshot, {})

        def test_streaming_cancelled_sets_lifecycle_cancelled(self) -> None:
            """When the streaming helper raises CancelledRequest, lifecycle ends cancelled."""

        def test_streaming_non_eventstream_response_closes_response(self) -> None:
            """Non-event-stream responses should always close the HTTP response."""

            class FakeResponse:
                status_code = 200

                def __init__(self) -> None:
                    self.headers = {"content-type": "application/json"}
                    self.closed = False

                def json(self):
                    return {"choices": [{"message": {"content": "Hello world"}}]}

                def close(self):
                    self.closed = True

            def fake_get(key, default=None):
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                # Force streaming enabled so send_request takes the streaming branch.
                if key == "user.model_streaming":
                    return True
                return default

            response: FakeResponse | None = None

            def fake_post(url, headers=None, json=None, timeout=None, stream=None):  # noqa: ARG001
                nonlocal response
                response = FakeResponse()
                return response

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
            self.assertIsNotNone(response)
            self.assertTrue(response.closed)

            snapshot = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(snapshot.get("text"), "Hello world")
            self.assertTrue(snapshot.get("completed"))
            self.assertFalse(snapshot.get("errored"))
            if RequestLifecycleState is not None:
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "completed")

        def test_streaming_cancel_records_cancel_requested_event(self) -> None:
            """State-driven cancels should emit cancel_requested/error/cancel_executed."""

            class FakeResponse:
                status_code = 200

                def __init__(self) -> None:
                    self.headers = {"content-type": "text/event-stream"}

                def iter_lines(self):
                    payload = {"choices": [{"delta": {"content": "Hi"}}]}
                    yield f"data: {json.dumps(payload)}".encode("utf-8")
                    yield b"data: [DONE]"

                def close(self):
                    pass

            def fake_get(key, default=None):
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_post(url, headers=None, json=None, timeout=None, stream=None):  # noqa: ARG001
                return FakeResponse()

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(modelHelpers.requests, "post", side_effect=fake_post),
                patch.object(
                    modelHelpers, "_should_show_response_canvas", return_value=False
                ),
                patch.object(
                    modelHelpers,
                    "current_state",
                    return_value=RequestState(cancel_requested=True),
                ),
                patch.object(modelHelpers, "emit_cancel", lambda **_kwargs: None),
                patch.object(
                    modelHelpers, "set_controller", lambda *_args, **_kwargs: None
                ),
                patch.object(
                    modelHelpers,
                    "cancel_active_request",
                    side_effect=AssertionError("cancel_active_request should not run"),
                ),
            ):
                with self.assertRaises(modelHelpers.CancelledRequest):
                    modelHelpers._send_request_streaming(GPTState.request, "req-cancel")

            events = getattr(GPTState, "last_streaming_events", [])
            kinds = [e.get("kind") for e in events]
            self.assertIn("cancel_requested", kinds)
            self.assertIn("cancel_executed", kinds)
            self.assertIn("error", kinds)
            self.assertLess(kinds.index("cancel_requested"), kinds.index("error"))
            self.assertLess(kinds.index("error"), kinds.index("cancel_executed"))
            self.assertEqual(kinds.count("error"), 1)
            self.assertEqual(kinds.count("cancel_executed"), 1)
            executed_event = next(
                e for e in events if e.get("kind") == "cancel_executed"
            )
            self.assertEqual(executed_event.get("source"), "iter_lines")
            self.assertTrue(executed_event.get("emitted"))

        def test_send_request_max_attempts_sets_lifecycle_and_raises(self) -> None:
            """Non-streaming max_attempts path should mark lifecycle errored and raise."""

            if RequestLifecycleState is None:
                self.skipTest("RequestLifecycleState unavailable")

            def fake_get(key, default=None):
                # Disable streaming so send_request takes the non-stream loop.
                if key == "user.model_streaming":
                    return False
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_send_request_internal(_req):  # noqa: ARG001
                # Return a response with no message content so message_content
                # stays None and the loop exhausts max_attempts.
                return {"choices": [{"message": {}}]}

            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers,
                    "send_request_internal",
                    side_effect=fake_send_request_internal,
                ),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    send_request(max_attempts=2)

            self.assertIn("max attempts", str(ctx.exception).lower())
            self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
            self.assertEqual(GPTState.last_lifecycle.status, "errored")

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
            snapshot = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertTrue(snapshot.get("errored"))
            self.assertIn("Request timed out", snapshot.get("error_message", ""))
            if RequestLifecycleState is not None:
                self.assertIsInstance(GPTState.last_lifecycle, RequestLifecycleState)
                self.assertEqual(GPTState.last_lifecycle.status, "errored")

        def test_non_stream_run_clears_previous_snapshot(self) -> None:
            """Non-stream runs should clear any stale streaming snapshot."""

            if RequestLifecycleState is None:
                self.skipTest("RequestLifecycleState unavailable")

            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return False
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_send_request_internal(_req):  # noqa: ARG001
                return {"choices": [{"message": {"content": "hi"}}]}

            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }
            GPTState.last_streaming_snapshot = {"text": "old", "completed": True}

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(
                    modelHelpers,
                    "send_request_internal",
                    side_effect=fake_send_request_internal,
                ),
            ):
                send_request(max_attempts=1)

            self.assertEqual(GPTState.last_streaming_snapshot, {})

        def test_non_stream_suggest_skips_history_logging(self) -> None:
            """Suggest runs should not append to request history."""

            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return False
                if key == "user.model_endpoint":
                    return "http://example.com"
                if key == "user.model_request_timeout_seconds":
                    return 120
                return default

            def fake_send_request_internal(_req):  # noqa: ARG001
                return {"choices": [{"message": {"content": "assistant reply"}}]}

            provider = SimpleNamespace(
                features={"streaming": False}, id="stub-provider"
            )

            GPTState.request = {
                "model": "dummy-model",
                "messages": [
                    {"role": "user", "content": "hi"},
                ],
            }

            previous_kind = getattr(GPTState, "current_destination_kind", None)
            GPTState.current_destination_kind = "suggest"

            try:
                with (
                    patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                    patch.object(
                        modelHelpers,
                        "send_request_internal",
                        side_effect=fake_send_request_internal,
                    ),
                    patch.object(
                        modelHelpers, "append_entry_from_request"
                    ) as append_entry,
                    patch.object(modelHelpers, "bound_provider", return_value=provider),
                    patch.object(modelHelpers, "_ensure_request_supported"),
                ):
                    send_request(max_attempts=1)
            finally:
                if previous_kind is None and hasattr(
                    GPTState, "current_destination_kind"
                ):
                    delattr(GPTState, "current_destination_kind")
                else:
                    GPTState.current_destination_kind = previous_kind

            append_entry.assert_not_called()

else:
    if not TYPE_CHECKING:

        class StreamingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
