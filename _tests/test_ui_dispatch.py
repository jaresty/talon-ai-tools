import unittest
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import uiDispatch
    from talon import cron

    class UIDispatchTests(unittest.TestCase):
        def setUp(self):
            cron.after_calls = []

        def test_dispatch_uses_cron_after(self):
            called = []

            def fn():
                called.append(True)

            with patch.object(uiDispatch.cron, "after") as after:
                after.side_effect = lambda delay, cb: cb()
                uiDispatch.run_on_ui_thread(fn, delay_ms=15)
                uiDispatch._drain_for_tests()

            self.assertTrue(called)

        def test_dispatch_falls_back_on_cron_failure(self):
            called = []

            def fn():
                called.append(True)

            with patch.object(
                uiDispatch.cron, "after", side_effect=Exception("boom")
            ):
                uiDispatch.run_on_ui_thread(fn)
                uiDispatch._drain_for_tests()

            self.assertTrue(called)

        def test_dispatch_swallows_fn_exceptions(self):
            # Should not raise when fn errors.
            uiDispatch.run_on_ui_thread(lambda: (_ for _ in ()).throw(Exception("kaboom")))
            uiDispatch._drain_for_tests()
else:
    class UIDispatchTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
