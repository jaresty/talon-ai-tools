import threading
import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.GPT import gpt as gpt_module
    from talon_user.lib import modelHelpers, promptPipeline, promptSession, requestAsync
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.requestBus import emit_reset, set_controller
    from talon_user.lib.requestController import RequestUIController


class SuggestParallelRequestsTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        # Reset request bus/UI to a clean state for each run.
        set_controller(RequestUIController())
        emit_reset()
        GPTState.clear_all()
        actions.user.calls.clear()
        actions.app.calls.clear()

    def test_suggest_timeout_triggers_parallel_requests(self):
        """End-to-end: async suggest timeout falls back and double-dispatches the request."""
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        suggestion_json = (
            '{"suggestions": [{"name": "One", "recipe": "describe · gist · edges · fog"}]}'
        )
        calls: list[str] = []
        first_blocked = threading.Event()
        release_first = threading.Event()

        def fake_send_request(*args, **kwargs):
            # Simulate a slow first request so the async handle remains in-flight.
            calls.append("call")
            if len(calls) == 1:
                first_blocked.set()
                release_first.wait(timeout=1.0)
            return {"type": "text", "text": suggestion_json}

        def start_async_stub(fn, *args, **kwargs):
            """Return a handle that finishes only after release_first."""

            done_event = threading.Event()

            class Handle:
                result = None
                error = None

                @property
                def done(self):
                    return done_event.is_set()

                def wait(self, timeout=None):
                    return done_event.wait(timeout)

            handle = Handle()

            def _runner():
                try:
                    handle.result = fn(*args, **kwargs)
                finally:
                    done_event.set()

            thread = threading.Thread(target=_runner, daemon=True)
            thread.start()
            return handle

        # Minimal source stub so suggest has content to run against.
        source = SimpleNamespace(get_text=lambda: "content", modelSimpleSource="clip")

        with (
            patch.object(gpt_module, "create_model_source", return_value=source),
            patch.object(modelHelpers, "send_request", side_effect=fake_send_request),
            patch.object(promptSession, "send_request", side_effect=fake_send_request),
            patch.object(requestAsync, "start_async", side_effect=start_async_stub),
            patch.object(promptPipeline, "start_async", side_effect=start_async_stub),
        ):
            try:
                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")
            finally:
                release_first.set()

        self.assertTrue(
            first_blocked.is_set(),
            "First suggest request should still be in-flight when fallback begins.",
        )
        # Regression: the fallback path dispatches a second request while the first is still running.
        self.assertEqual(
            len(calls),
            1,
            "model run suggest should not issue multiple model requests in parallel",
        )


if __name__ == "__main__":
    unittest.main()
