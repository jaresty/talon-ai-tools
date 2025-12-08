import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import requestUI  # registers default controller
    from talon_user.lib.requestBus import (
        emit_begin_send,
        emit_complete,
        emit_fail,
        emit_reset,
    )
    from talon_user.lib.requestState import RequestPhase
    from talon import actions

    class RequestUITests(unittest.TestCase):
        def setUp(self):
            actions.app.calls.clear()
            actions.user.calls.clear()
            requestUI.register_default_request_ui()
            emit_reset()

        def test_toast_notifications_on_send_and_complete(self):
            emit_begin_send()
            emit_complete()
            # Expect at least two notifications: sending and done hint.
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            user_notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(app_notify_calls) + len(user_notify_calls), 2)
            messages = " ".join(
                str(args[0])
                for _, args, _ in app_notify_calls + user_notify_calls
                if args
            )
            self.assertIn("sending", messages.lower())
            self.assertIn("done", messages.lower())

        def test_state_advances_via_bus(self):
            emit_begin_send()
            self.assertEqual(requestUI._controller.state.phase, RequestPhase.SENDING)

        def test_fail_notifies(self):
            actions.user.calls.clear()
            actions.app.calls.clear()
            emit_fail("boom")
            notifications = [c for c in actions.user.calls + actions.app.calls if c[0] == "notify"]
            self.assertTrue(any("boom" in str(args[0]) for _, args, _ in notifications))
else:
    if not TYPE_CHECKING:
        class RequestUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
