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
            patch.object(prompt_pattern_module, "_open_prompt_pattern_canvas") as open_canvas,
            patch.object(prompt_pattern_module, "_close_prompt_pattern_canvas") as close_canvas,
        ):
            PromptPatternActions.prompt_pattern_gui_open_for_static_prompt("describe")
            PromptPatternActions.prompt_pattern_gui_close()
            PromptPatternActions.prompt_pattern_run_preset("analysis")
            PromptPatternActions.prompt_pattern_save_source_to_file()
        open_canvas.assert_not_called()
        close_canvas.assert_not_called()


if __name__ == "__main__":
    unittest.main()
