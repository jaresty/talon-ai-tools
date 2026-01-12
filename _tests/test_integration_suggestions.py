import json
import os
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
    from talon_user.lib import suggestionCoordinator as suggestion_coordinator

    class SuggestionIntegrationTests(unittest.TestCase):
        def setUp(self):
            os.environ.setdefault("PYTEST_CURRENT_TEST", "unittest")
            GPTState.reset_all()
            GPTState.last_directional = "fog"

            GPTState.last_axes = {
                "completeness": [],
                "scope": [],
                "method": [],
                "form": [],
                "channel": [],
                "directional": ["fog"],
            }
            # Stub out GUI open so we can focus on data flow.
            actions.user.model_prompt_recipe_suggestions_gui_open = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            # Patch pipeline used by gpt_suggest_prompt_recipes.
            self._original_pipeline = gpt_module._prompt_pipeline
            self.pipeline = MagicMock()
            # Force async suggestion flow to fall back to the synchronous
            # pipeline result so the tests can control the suggestion text.
            handle = MagicMock()

            def _wait(timeout=None):
                if handle.result is None:
                    handle.result = self.pipeline.complete.return_value
                return True

            handle.wait = MagicMock(side_effect=_wait)
            handle.result = None
            self.pipeline.complete_async.return_value = handle
            gpt_module._prompt_pipeline = self.pipeline

        def tearDown(self):
            gpt_module._prompt_pipeline = self._original_pipeline

        def test_suggest_then_run_index_executes_recipe(self):
            # Arrange suggestion text returned from the pipeline.
            suggestion_text = "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Now, run the first suggestion by index through the suggestion GUI helper.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Expect that gpt_apply_prompt was invoked and last_recipe reflects the recipe.
            actions.user.gpt_apply_prompt.assert_called_once()
            self.assertIn("describe", GPTState.last_recipe)
            self.assertIn("full", GPTState.last_recipe)

        def test_suggest_populates_persona_intent_metadata_end_to_end(self):
            payload = {
                "suggestions": [
                    {
                        "name": "Mentor junior dev",
                        "recipe": "describe · full · focus · scaffold · plain · fog",
                        "persona_voice": "as teacher",
                        "persona_audience": "to junior engineer",
                        "persona_tone": "kindly",
                        "intent_purpose": "teach",
                        "why": "Coaching stance for junior engineers",
                    }
                ]
            }
            handle = self.pipeline.complete_async.return_value
            handle.wait = MagicMock(return_value=True)
            handle.result = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )
            self.pipeline.complete.return_value = handle.result

            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            entries = suggestion_coordinator.suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["persona_preset_key"], "teach_junior_dev")
            self.assertEqual(entry["persona_preset_spoken"], "mentor")
            self.assertEqual(entry["intent_preset_key"], "teach")
            self.assertEqual(entry["intent_display"], "Teach / explain")

            suggestion_module.SuggestionGUIState.suggestions = []
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)
            self.assertTrue(suggestion_module.SuggestionGUIState.suggestions)
            hydrated = suggestion_module.SuggestionGUIState.suggestions[0]
            self.assertEqual(hydrated.persona_preset_spoken, "mentor")
            self.assertEqual(hydrated.intent_display, "Teach / explain")
            self.assertEqual(hydrated.persona_voice, "as teacher")
            self.assertEqual(hydrated.persona_audience, "to junior engineer")
            self.assertEqual(hydrated.persona_tone, "kindly")

        def test_suggest_alias_only_metadata_round_trip(self):
            payload = {
                "suggestions": [
                    {
                        "name": "Decide with mentor",
                        "recipe": "describe · full · focus · plan · plain · fog",
                        "persona_preset_spoken": "mentor",
                        "intent_display": "Decide",
                        "why": "Alias metadata from Concordance catalog",
                    }
                ]
            }
            handle = self.pipeline.complete_async.return_value
            handle.wait = MagicMock(return_value=True)
            handle.result = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )
            self.pipeline.complete.return_value = handle.result

            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            entries = suggestion_coordinator.suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["persona_preset_key"], "teach_junior_dev")
            self.assertEqual(entry["persona_preset_label"], "Teach junior dev")
            self.assertEqual(entry["persona_preset_spoken"], "mentor")
            self.assertEqual(entry["persona_voice"], "as teacher")
            self.assertEqual(entry["persona_audience"], "to junior engineer")
            self.assertEqual(entry["persona_tone"], "kindly")
            self.assertEqual(entry["intent_preset_key"], "decide")
            self.assertEqual(entry["intent_preset_label"], "Decide")
            self.assertEqual(entry["intent_display"], "Decide")
            self.assertEqual(entry["intent_purpose"], "decide")

            suggestion_module.SuggestionGUIState.suggestions = []
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)
            self.assertTrue(suggestion_module.SuggestionGUIState.suggestions)
            hydrated = suggestion_module.SuggestionGUIState.suggestions[0]
            self.assertEqual(hydrated.persona_preset_spoken, "mentor")
            self.assertEqual(hydrated.persona_preset_label, "Teach junior dev")
            self.assertEqual(hydrated.intent_display, "Decide")
            self.assertEqual(hydrated.intent_preset_key, "decide")
            self.assertEqual(hydrated.intent_preset_label, "Decide")
            self.assertEqual(hydrated.intent_purpose, "decide")
            self.assertEqual(hydrated.persona_voice, "as teacher")
            self.assertEqual(hydrated.persona_audience, "to junior engineer")
            self.assertEqual(hydrated.persona_tone, "kindly")

        def test_suggest_then_again_merges_overrides(self):
            # Arrange suggestion text returned from the pipeline.
            suggestion_text = "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # First, run `model suggest` to populate GPTState.last_suggested_recipes.
            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
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
            # last recipe: keep the same static prompt/scope/method/form/channel but
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
                    "", "gist", [], [], "rog", "", ""
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

        def test_suggest_multi_tag_then_again_resolves_form_channel_singletons(self):
            """End-to-end: multi-tag suggestion followed by overrides respects form/channel singleton caps."""
            # Arrange a multi-tag suggestion that includes both a form and channel token;
            # the normaliser should keep singletons when rerun.
            suggestion_text = "Name: Jira/ADR ticket | Recipe: ticket · full · actions edges · structure flow · adr · jira · fog"
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # Run `model suggest` to populate last_suggested_recipes.
            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Execute the suggestion to seed last_recipe / last_* from the GUI.
            suggestion_module.UserActions.model_prompt_recipe_suggestions_run_index(1)

            # At this point, last form/channel are the raw tokens from the suggestion recipe.
            self.assertEqual(GPTState.last_form, "adr")
            self.assertEqual(GPTState.last_channel, "jira")

            # Now rerun with a channel override that adds 'jira' again; form/channel stay singletons.
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
                    "", "", [], [], "rog", "", "jira"
                )

                # One more apply call with the rerun config.
                config = actions.user.gpt_apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-MULTI-AGAIN")

                # After rerun, form/channel should remain singletons.
                self.assertEqual(GPTState.last_form, "adr")
                self.assertEqual(GPTState.last_channel, "jira")

        def test_suggest_over_cap_axes_then_again_enforces_soft_caps(self):
            """End-to-end: over-cap multi-tag axes from suggestion respect soft caps on rerun."""
            # Arrange a suggestion that uses over-cap scope and form/channel segments:
            # - scope: actions edges relations (3 tokens, cap 2)
            # - form: bullets faq checklist (cap 1)
            # - channel: slack jira remote (cap 1)
            suggestion_text = "Name: Over-cap ticket | Recipe: ticket · full · actions edges relations · structure flow · bullets faq checklist · slack jira remote · fog"
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(suggestion_text)]
            )

            # Run `model suggest` to populate last_suggested_recipes.
            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
            ):
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

                before_count = actions.user.gpt_apply_prompt.call_count

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "", "", [], [], "rog", "", ""
                )

                self.assertGreater(
                    actions.user.gpt_apply_prompt.call_count,
                    before_count,
                    "Expected gpt_apply_prompt to be called during rerun",
                )
                config = actions.user.gpt_apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-OVER-CAP-AGAIN")

                # After rerun, last_scope should contain at most 2 tokens drawn
                # from the original suggestion's scope tokens.
                scope_tokens = GPTState.last_scope.split()
                self.assertLessEqual(len(scope_tokens), 2)
                self.assertTrue(
                    set(scope_tokens).issubset({"actions", "edges", "relations"})
                )

                # After rerun, form/channel should reflect singleton caps from the over-cap inputs.
                form_tokens = GPTState.last_form.split()
                channel_tokens = GPTState.last_channel.split()
                self.assertLessEqual(len(form_tokens), 1)
                self.assertLessEqual(len(channel_tokens), 1)
                self.assertTrue(
                    set(form_tokens).issubset({"bullets", "faq", "checklist"})
                )
                self.assertTrue(
                    set(channel_tokens).issubset({"slack", "jira", "remote"})
                )
else:
    if not TYPE_CHECKING:

        class SuggestionIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
