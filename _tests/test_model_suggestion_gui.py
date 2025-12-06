import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelSuggestionGUI import (
        UserActions,
        SuggestionGUIState,
        SuggestionCanvasState,
    )

    class ModelSuggestionGUITests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            SuggestionGUIState.suggestions = []
            SuggestionCanvasState.showing = False
            actions.app.notify = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            actions.user.model_prompt_recipe_suggestions_gui_close = MagicMock()

        def test_run_index_executes_suggestion_and_closes_gui(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Deep map",
                    "recipe": "describe · full · relations · cluster · bullets · fog",
                },
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(2)

            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

        def test_run_index_out_of_range_notifies_and_does_not_run(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Only one",
                    "recipe": "describe · gist · focus · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(0)
            UserActions.model_prompt_recipe_suggestions_run_index(3)

            self.assertGreaterEqual(actions.app.notify.call_count, 1)
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_run_index_with_no_suggestions_notifies(self):
            GPTState.last_suggested_recipes = []

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.app.notify.assert_called_once()
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_open_uses_cached_suggestions_and_shows_canvas(self):
            """model_prompt_recipe_suggestions_gui_open populates state and opens the canvas."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]
            self.assertFalse(SuggestionCanvasState.showing)
            self.assertEqual(SuggestionGUIState.suggestions, [])

            UserActions.model_prompt_recipe_suggestions_gui_open()

            # Suggestions should be copied into GUI state and the canvas opened.
            self.assertTrue(SuggestionCanvasState.showing)
            self.assertEqual(len(SuggestionGUIState.suggestions), 1)

        def test_open_with_no_suggestions_notifies_and_does_not_show_canvas(self):
            GPTState.last_suggested_recipes = []
            self.assertFalse(SuggestionCanvasState.showing)

            UserActions.model_prompt_recipe_suggestions_gui_open()

            actions.app.notify.assert_called_once()
            self.assertFalse(SuggestionCanvasState.showing)

else:
    if not TYPE_CHECKING:
        class ModelSuggestionGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
