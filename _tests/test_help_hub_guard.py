import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import helpHub as help_module
    from talon_user.lib.helpHub import UserActions as HelpActions, HelpHubState
    import talon_user.lib.dropReasonUtils as drop_reason_module


class HelpHubGuardTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        HelpHubState.showing = False
        HelpHubState.filter_text = ""
        HelpHubState.show_onboarding = False

    def test_help_hub_actions_respect_in_flight_guard(self):
        with patch.object(
            help_module, "_reject_if_request_in_flight", return_value=True
        ):
            HelpActions.help_hub_open()
            HelpActions.help_hub_close()
            HelpActions.help_hub_toggle()
            HelpActions.help_hub_onboarding()
            HelpActions.help_hub_set_filter("foo")
            HelpActions.help_hub_pick_result(1)
            HelpActions.help_hub_copy_cheat_sheet()
            HelpActions.help_hub_test_click("foo")

        self.assertFalse(HelpHubState.showing)
        self.assertEqual(HelpHubState.filter_text, "")
        self.assertFalse(HelpHubState.show_onboarding)

    def test_request_is_in_flight_delegates_to_request_gating(self):
        with patch.object(
            help_module, "request_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(help_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            help_module, "request_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(help_module._request_is_in_flight())
        helper.assert_called_once_with()

    def test_reject_if_request_in_flight_notifies_with_drop_message(self):
        with (
            patch.object(
                help_module,
                "try_begin_request",
                return_value=(False, "in_flight"),
            ) as try_begin,
            patch.object(
                help_module,
                "render_drop_reason",
                return_value="Request running",
                create=True,
            ) as render_message,
            patch.object(help_module, "set_drop_reason") as set_reason,
            patch.object(help_module, "notify") as notify_mock,
        ):
            self.assertTrue(help_module._reject_if_request_in_flight())
        try_begin.assert_called_once_with(source="helpHub")
        render_message.assert_called_once_with("in_flight")
        set_reason.assert_called_once_with("in_flight", "Request running")
        notify_mock.assert_called_once_with("Request running")

        with (
            patch.object(
                help_module,
                "try_begin_request",
                return_value=(False, "unknown_reason"),
            ),
            patch.object(
                drop_reason_module,
                "drop_reason_message",
                return_value="",
            ),
            patch.object(
                help_module,
                "render_drop_reason",
                return_value="Rendered fallback",
                create=True,
            ) as render_message,
            patch.object(help_module, "set_drop_reason") as set_reason,
            patch.object(help_module, "notify") as notify_mock,
        ):
            self.assertTrue(help_module._reject_if_request_in_flight())
        render_message.assert_called_once_with("unknown_reason")
        set_reason.assert_called_once_with("unknown_reason", "Rendered fallback")
        notify_mock.assert_called_once_with("Rendered fallback")

        with (
            patch.object(help_module, "try_begin_request", return_value=(True, "")),
            patch.object(help_module, "last_drop_reason", return_value="", create=True),
            patch.object(help_module, "set_drop_reason") as set_reason,
            patch.object(help_module, "notify") as notify_mock,
        ):
            self.assertFalse(help_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("")
        notify_mock.assert_not_called()

        with (
            patch.object(help_module, "try_begin_request", return_value=(True, "")),
            patch.object(
                help_module,
                "last_drop_reason",
                return_value="drop_pending",
                create=True,
            ),
            patch.object(help_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(help_module._reject_if_request_in_flight())
        set_reason.assert_not_called()


if __name__ == "__main__":
    unittest.main()
