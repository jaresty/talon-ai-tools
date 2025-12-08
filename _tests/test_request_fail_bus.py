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
    from talon_user.lib.requestBus import set_controller, emit_reset, current_state
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.modelHelpers import GPTRequestError
    from talon_user.lib.requestState import RequestPhase

    class RequestFailBusTests(unittest.TestCase):
        def setUp(self):
            from talon_user.lib import requestUI

            # Use default controller wiring (with on_state_change notifications).
            controller = requestUI.register_default_request_ui()
            set_controller(controller)
            emit_reset()
            modelHelpers.actions.user.calls.clear()
            modelHelpers.actions.app.calls.clear()
            modelHelpers.GPTState.request = {"messages": []}

        def test_send_request_emits_fail_on_exception(self):
            with patch.object(
                modelHelpers, "send_request_internal", side_effect=GPTRequestError(500, "boom")
            ):
                with self.assertRaises(GPTRequestError):
                    modelHelpers.send_request(max_attempts=1)
            self.assertEqual(current_state().phase, RequestPhase.ERROR)
            # Expect at least one notification via controller on error.
            notifications = [
                c for c in modelHelpers.actions.user.calls + modelHelpers.actions.app.calls if c[0] == "notify"
            ]
            self.assertTrue(any("fail" in str(args[0]).lower() or "boom" in str(args[0]).lower() for _, args, _ in notifications))
else:
    if not TYPE_CHECKING:
        class RequestFailBusTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
