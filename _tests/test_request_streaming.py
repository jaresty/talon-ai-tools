import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

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

        def test_streaming_accumulates_chunks(self):
            class FakeResponse:
                status_code = 200

                def iter_lines(self):
                    yield b'data: {"choices":[{"delta":{"content":"Hello"}}]}'
                    yield b'data: {"choices":[{"delta":{"content":" \xf0\x9f\x8c\x8d"}}]}'
                    yield b"data: [DONE]"

            def json(self):
                return {"choices": [{"message": {"content": "Hello 🌍"}}]}

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
                patch.object(modelHelpers, "_send_request_streaming", side_effect=fake_stream),
                patch.object(modelHelpers, "send_request_internal", side_effect=AssertionError("should not call sync")),
            ):
                result = send_request(max_attempts=1)
                self.assertEqual(result["text"], "Hello 🌍")
                self.assertEqual(GPTState.text_to_confirm, "Hello 🌍")
                self.assertEqual(GPTState.last_response, "Hello 🌍")

        def test_streaming_honours_cancel(self):
            class FakeResponse:
                status_code = 200

                def iter_lines(self):
                    yield b'data: {"choices":[{"delta":{"content":"Hello"}}]}'
                    yield b"data: [DONE]"

                def json(self):
                    return {"choices": [{"message": {"content": "Hello"}}]}

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
                patch.object(modelHelpers, "_send_request_streaming", side_effect=fake_stream),
                patch.object(modelHelpers, "current_state", side_effect=fake_state),
                patch.object(modelHelpers, "send_request_internal", side_effect=AssertionError("should not call sync")),
            ):
                result = send_request(max_attempts=1)
                self.assertEqual(result.get("text"), "")
else:
    if not TYPE_CHECKING:
        class StreamingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
