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
    from talon_user.lib.requestBus import emit_cancel, emit_reset, set_controller
    from talon_user.lib.requestController import RequestUIController

    class RequestCancelTests(unittest.TestCase):
        def setUp(self):
            set_controller(RequestUIController())
            emit_reset()
            # Ensure any notifications do not interfere with test output.
            modelHelpers.actions.user.calls.clear()
            modelHelpers.actions.app.calls.clear()
            # Provide a minimal request so send_request can access messages.
            modelHelpers.GPTState.request = {"messages": []}

        def test_send_request_aborts_on_cancel(self):
            # Arrange: force current_state to report cancel_requested=True
            with patch.object(
                modelHelpers, "current_state", return_value=modelHelpers.RequestState(cancel_requested=True)
            ), patch.object(modelHelpers, "send_request_internal") as sri:
                result = modelHelpers.send_request(max_attempts=1)
                sri.assert_not_called()
                self.assertEqual(result.get("text"), "")

        def test_cancel_after_completion_drops_response(self):
            # current_state reports no cancel initially, then cancelled after the HTTP call.
            states = [
                modelHelpers.RequestState(cancel_requested=False),
                modelHelpers.RequestState(cancel_requested=True),
            ]

            def fake_current_state():
                return states.pop(0) if states else modelHelpers.RequestState(cancel_requested=True)

            with (
                patch.object(modelHelpers, "current_state", side_effect=fake_current_state),
                patch.object(modelHelpers, "send_request_internal") as sri,
            ):
                sri.return_value = {"choices": [{"message": {"content": "ok", "tool_calls": []}}]}
                result = modelHelpers.send_request(max_attempts=1)
                self.assertEqual(result.get("text"), "")
else:
    if not TYPE_CHECKING:
        class RequestCancelTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
