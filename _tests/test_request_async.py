import unittest
from typing import TYPE_CHECKING
from time import sleep

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestAsync import start_async
    from talon_user.lib.requestBus import current_state, set_controller, emit_reset
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import RequestPhase

    class RequestAsyncTests(unittest.TestCase):
        def setUp(self):
            set_controller(RequestUIController())
            emit_reset()

        def test_start_async_returns_result(self):
            handle = start_async(lambda x, y: x + y, 2, 3)
            handle.wait(timeout=1.0)
            self.assertTrue(handle.done)
            self.assertEqual(handle.result, 5)
            self.assertIsNone(handle.error)

        def test_cancel_emits_cancel(self):
            # Use a slow function to allow cancel before completion.
            handle = start_async(lambda: sleep(0.2))
            handle.cancel()
            handle.wait(timeout=1.0)
            self.assertEqual(current_state().phase, RequestPhase.CANCELLED)
else:
    if not TYPE_CHECKING:
        class RequestAsyncTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
