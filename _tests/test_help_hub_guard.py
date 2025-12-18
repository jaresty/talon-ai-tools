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

    def test_reject_if_request_in_flight_records_drop_reason(self):
        with (
            patch.object(
                help_module, "try_start_request", return_value=(False, "in_flight")
            ),
            patch.object(help_module, "current_state"),
            patch.object(help_module, "set_drop_reason") as set_reason,
            patch.object(help_module, "notify") as notify_mock,
        ):
            self.assertTrue(help_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(help_module, "try_start_request", return_value=(True, "")),
            patch.object(help_module, "current_state"),
            patch.object(help_module, "set_drop_reason") as set_reason,
            patch.object(help_module, "notify") as notify_mock,
        ):
            self.assertFalse(help_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
