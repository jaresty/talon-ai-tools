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
    from talon_user.lib.requestBus import set_controller, emit_reset
    from talon_user.lib.requestController import RequestUIController

    class RequestAsyncWrapperTests(unittest.TestCase):
        def setUp(self):
            set_controller(RequestUIController())
            emit_reset()
            modelHelpers.GPTState.request = {"messages": []}

        def test_send_request_async_runs_in_background(self):
            with patch.object(modelHelpers, "send_request") as sr:
                sr.return_value = {"type": "text", "text": "ok"}
                handle = modelHelpers.send_request_async()
                handle.wait(timeout=1.0)
                self.assertTrue(handle.done)
                self.assertIsNone(handle.error)
                self.assertEqual(handle.result, {"type": "text", "text": "ok"})
                sr.assert_called_once()
else:
    if not TYPE_CHECKING:
        class RequestAsyncWrapperTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
