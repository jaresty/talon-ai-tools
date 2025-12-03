import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.GPT import gpt as gpt_module
    from talon_user.lib import modelSuggestionGUI as suggestion_module

    class SuggestionIntegrationTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            # Stub out GUI open so we can focus on data flow.
            actions.user.model_prompt_recipe_suggestions_gui_open = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            # Patch pipeline used by gpt_suggest_prompt_recipes.
            self._original_pipeline = gpt_module._prompt_pipeline
            self.pipeline = MagicMock()
            gpt_module._prompt_pipeline = self.pipeline

        def tearDown(self):
            gpt_module._prompt_pipeline = self._original_pipeline

        def test_suggest_then_run_index_executes_recipe(self):
            # Arrange suggestion text returned from the pipeline.
            suggestion_text = (
                "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
            )
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            with patch.object(
                gpt_module, "create_model_source"
            ) as create_source, patch.object(
                gpt_module, "PromptSession"
            ) as session_cls:
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                # First, run `model suggest` to populate GPTState.last_suggested_recipes.
                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

            # Now, run the first suggestion by index through the suggestion GUI helper.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Expect that gpt_apply_prompt was invoked and last_recipe reflects the recipe.
            actions.user.gpt_apply_prompt.assert_called_once()
            self.assertIn("describe", GPTState.last_recipe)
            self.assertIn("full", GPTState.last_recipe)
else:
    if not TYPE_CHECKING:
        class SuggestionIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass

