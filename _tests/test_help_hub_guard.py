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

    def test_reject_if_request_in_flight_delegates_to_surface_guard(self):
        captured_kwargs: dict[str, object] = {}

        def fake_guard(**kwargs):
            captured_kwargs.update(kwargs)
            return True

        with patch(
            "talon_user.lib.helpHub.guard_surface_request",
            side_effect=fake_guard,
        ) as guard:
            self.assertTrue(help_module._reject_if_request_in_flight())

        guard.assert_called_once()
        self.assertEqual(captured_kwargs["surface"], "help_hub")
        self.assertEqual(captured_kwargs["source"], "helpHub")
        self.assertEqual(
            captured_kwargs["suppress_attr"], "suppress_overlay_inflight_guard"
        )

    def test_reject_if_request_in_flight_propagates_guard_result(self):
        with patch(
            "talon_user.lib.helpHub.guard_surface_request",
            return_value=False,
        ) as guard:
            self.assertFalse(help_module._reject_if_request_in_flight())
        guard.assert_called_once()


if __name__ == "__main__":
    unittest.main()
