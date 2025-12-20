import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelPromptPatternGUI as prompt_pattern_module
    from talon_user.lib.modelPromptPatternGUI import UserActions as PromptPatternActions


class PromptPatternGUIGuardTests(unittest.TestCase):
    def test_prompt_pattern_gui_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                prompt_pattern_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(
                prompt_pattern_module, "_open_prompt_pattern_canvas"
            ) as open_canvas,
            patch.object(
                prompt_pattern_module, "_close_prompt_pattern_canvas"
            ) as close_canvas,
        ):
            PromptPatternActions.prompt_pattern_gui_open_for_static_prompt("describe")
            PromptPatternActions.prompt_pattern_gui_close()
            PromptPatternActions.prompt_pattern_run_preset("analysis")
            PromptPatternActions.prompt_pattern_save_source_to_file()
        open_canvas.assert_not_called()
        close_canvas.assert_not_called()

    def test_request_is_in_flight_delegates_to_request_bus(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with patch.object(
            prompt_pattern_module, "bus_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(prompt_pattern_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            prompt_pattern_module, "bus_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(prompt_pattern_module._request_is_in_flight())
        helper.assert_called_once_with()

    def test_reject_if_request_in_flight_records_drop_reason(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with (
            patch.object(
                prompt_pattern_module,
                "try_begin_request",
                return_value=(False, "in_flight"),
            ),
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
            patch.object(prompt_pattern_module, "notify") as notify_mock,
        ):
            self.assertTrue(prompt_pattern_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(
                prompt_pattern_module, "try_begin_request", return_value=(True, "")
            ),
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
            patch.object(prompt_pattern_module, "notify") as notify_mock,
        ):
            self.assertFalse(prompt_pattern_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
