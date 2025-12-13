import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelSuggestionGUI as suggestion_module
    from talon_user.lib.modelSuggestionGUI import UserActions as SuggestionActions


class ModelSuggestionGUIGuardTests(unittest.TestCase):
    def test_suggestion_gui_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                suggestion_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(suggestion_module, "_open_suggestion_canvas") as open_canvas,
            patch.object(suggestion_module, "actions") as actions_mock,
        ):
            SuggestionActions.model_prompt_recipe_suggestions_gui_open()
            SuggestionActions.model_prompt_recipe_suggestions_gui_close()
            SuggestionActions.model_prompt_recipe_suggestions_run_index(1)
        open_canvas.assert_not_called()
        # No notifications or GUI actions should be emitted when guarded.
        self.assertFalse(actions_mock.app.notify.called)


if __name__ == "__main__":
    unittest.main()
