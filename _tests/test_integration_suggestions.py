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
                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Now, run the first suggestion by index through the suggestion GUI helper.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Expect that gpt_apply_prompt was invoked and last_recipe reflects the recipe.
            actions.user.gpt_apply_prompt.assert_called_once()
            self.assertIn("describe", GPTState.last_recipe)
            self.assertIn("full", GPTState.last_recipe)

        def test_suggest_then_again_merges_overrides(self):
            # Arrange suggestion text returned from the pipeline.
            suggestion_text = (
                "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
            )
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # First, run `model suggest` to populate GPTState.last_suggested_recipes.
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

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Next, run the first suggestion so it executes a concrete recipe and
            # seeds the structured last-recipe state.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)
            first_call_count = actions.user.gpt_apply_prompt.call_count
            self.assertGreaterEqual(first_call_count, 1)

            # Now call gpt_rerun_last_recipe with overrides on top of the stored
            # last recipe: keep the same static prompt/scope/method/style but
            # change completeness and directional lens.
            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ),
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source_again,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_dest_again,
            ):
                source_again = MagicMock()
                dest_again = MagicMock()
                create_source_again.return_value = source_again
                create_dest_again.return_value = dest_again
                model_prompt.return_value = "PROMPT-AGAIN"

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "", "gist", "", "", "", "rog"
                )

                # gpt_apply_prompt should have been called again with a config
                # built from modelPrompt and the default source/destination.
                self.assertEqual(
                    actions.user.gpt_apply_prompt.call_count, first_call_count + 1
                )
                config = actions.user.gpt_apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-AGAIN")
                self.assertIs(config.model_source, source_again)
                self.assertIs(config.model_destination, dest_again)

                # Structured last-recipe state should now reflect the overrides.
                self.assertEqual(GPTState.last_completeness, "gist")
                self.assertEqual(GPTState.last_directional, "rog")
else:
    if not TYPE_CHECKING:
        class SuggestionIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
