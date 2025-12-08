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
            # Force async suggestion flow to fall back to the synchronous
            # pipeline result so the tests can control the suggestion text.
            handle = MagicMock()
            handle.wait = MagicMock(return_value=True)
            handle.result = None
            self.pipeline.complete_async.return_value = handle
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

        def test_suggest_multi_tag_then_again_resolves_style_incompatibility(self):
            """End-to-end: multi-tag suggestion followed by overrides respects style incompatibility."""
            # Arrange a multi-tag suggestion that includes both 'jira' and 'adr'
            # in the style segment; the normaliser should resolve these via
            # the style incompatibility rules when rerun.
            suggestion_text = (
                "Name: Jira/ADR ticket | Recipe: ticket · full · actions edges · structure flow · jira adr · fog"
            )
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # Run `model suggest` to populate last_suggested_recipes.
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

            # Execute the suggestion to seed last_recipe / last_* from the GUI.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # At this point, last_style is still the raw multi-tag string from
            # the suggestion recipe ("jira adr").
            self.assertIn(GPTState.last_style, ("jira adr", "adr jira"))

            # Now rerun with a style override that adds 'jira' again; the
            # canonicaliser should resolve the style set using the
            # incompatibility rules and last-wins semantics.
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
                model_prompt.return_value = "PROMPT-MULTI-AGAIN"

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "", "", "", "", "jira", "rog"
                )

                # One more apply call with the rerun config.
                config = actions.user.gpt_apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-MULTI-AGAIN")

                # After rerun, last_style should reflect the resolved style set.
                # With jira/adr marked as incompatible and jira supplied last,
                # only 'jira' should remain after canonicalisation.
                self.assertEqual(GPTState.last_style, "jira")

        def test_suggest_over_cap_axes_then_again_enforces_soft_caps(self):
            """End-to-end: over-cap multi-tag axes from suggestion respect soft caps on rerun."""
            # Arrange a suggestion that uses over-cap scope and style segments:
            # - scope: actions edges relations (3 tokens, cap 2)
            # - style: jira story faq bullets (4 tokens, cap 3)
            suggestion_text = (
                "Name: Over-cap ticket | Recipe: ticket · full · actions edges relations · structure flow · jira story faq bullets · fog"
            )
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # Run `model suggest` to populate last_suggested_recipes.
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

            # Execute the suggestion via the GUI to seed last_recipe / last_*.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Now rerun without axis overrides; the canonicaliser should apply
            # soft caps when rebuilding the axis sets.
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
                model_prompt.return_value = "PROMPT-OVER-CAP-AGAIN"

                gpt_module.UserActions.gpt_rerun_last_recipe("", "", "", "", "", "rog")

                config = actions.user.gpt_apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-OVER-CAP-AGAIN")

                # After rerun, last_scope should contain at most 2 tokens drawn
                # from the original suggestion's scope tokens.
                scope_tokens = GPTState.last_scope.split()
                self.assertLessEqual(len(scope_tokens), 2)
                self.assertTrue(
                    set(scope_tokens).issubset({"actions", "edges", "relations"})
                )

                # After rerun, last_style should contain at most 3 tokens drawn
                # from the original suggestion's style tokens.
                style_tokens = GPTState.last_style.split()
                self.assertLessEqual(len(style_tokens), 3)
                self.assertTrue(
                    set(style_tokens).issubset({"jira", "story", "faq", "bullets"})
                )
else:
    if not TYPE_CHECKING:
        class SuggestionIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
