import json
import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.GPT import gpt as gpt_module

    class GPTSuggestValidationTests(unittest.TestCase):
        def setUp(self) -> None:
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
            # Force suggest flow to use the synchronous result text we control.
            self._original_pipeline = gpt_module._prompt_pipeline
            self.pipeline = MagicMock()
            handle = MagicMock()
            handle.wait.return_value = True
            handle.result = None
            self.pipeline.complete_async.return_value = handle
            gpt_module._prompt_pipeline = self.pipeline

        def tearDown(self) -> None:
            gpt_module._prompt_pipeline = self._original_pipeline

        def test_json_suggestions_validate_stance_and_capture_reasoning(self) -> None:
            # Arrange a JSON payload with one valid and one invalid stance.
            payload = {
                "suggestions": [
                    {
                        "name": "Valid stance",
                        "recipe": "describe · gist · focus bound · steps structure flow plan · bullets table · slack jira · rog",
                        "persona_voice": "as teacher",
                        "persona_audience": "to junior engineer",
                        "persona_tone": "kindly",
                        "intent_purpose": "for teaching",
                        "stance_command": "model write as teacher to junior engineer kindly",
                        "why": "For teaching-focused summaries.",
                        "reasoning": "Uses teaching persona and planning intent.",
                    },
                    {
                        "name": "Invalid stance",
                        "recipe": "describe · full · actions · structure · bullets · rog",
                        "persona_voice": "as facilitator",
                        "persona_audience": "to stakeholders",
                        "persona_tone": "gently",
                        "intent_purpose": "for collaborating",
                        "stance_command": "model write for collaborating",
                        "why": "Bad stance should be dropped.",
                        "reasoning": "Tried to leave intent underspecified.",
                    },
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )

            # Enable debug mode so validation failures are logged; we only assert
            # that this does not raise and that suggestions are still recorded.
            GPTState.debug_enabled = True

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

            # Two suggestions should be recorded.
            self.assertEqual(len(GPTState.last_suggested_recipes), 2)

            first, second = GPTState.last_suggested_recipes

            # The valid suggestion keeps its stance_command.
            self.assertEqual(first["name"], "Valid stance")
            self.assertIn("stance_command", first)
            # Axis caps should be enforced when normalising the recipe.
            self.assertEqual(
                first["recipe"],
                "describe · gist · focus bound · structure flow plan · table · jira · rog",
            )

            # The invalid stance suggestion is kept but without a stance_command.
            self.assertEqual(second["name"], "Invalid stance")
            self.assertNotIn("stance_command", second)

        def test_json_suggestions_validate_persona_axes(self) -> None:
            # Persona/intent fields should be canonicalised to known tokens; unknowns are dropped.
            payload = {
                "suggestions": [
                    {
                        "name": "Bad persona",
                        "recipe": "describe · gist · edges · rog",
                        "persona_voice": "as product manager",  # invalid token (canonical is 'as PM')
                        "persona_audience": "to team",  # valid token
                        "persona_tone": "firmly",  # invalid token
                        "intent_purpose": "for collaborating",  # invalid token
                        "stance_command": "model write as product manager to team firmly",
                        "why": "Ensure invalid persona tokens do not leak through.",
                        "reasoning": "Deliberately uses invalid persona/intent tokens.",
                    }
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
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

            self.assertEqual(len(GPTState.last_suggested_recipes), 1)
            suggestion = GPTState.last_suggested_recipes[0]
            self.assertEqual(suggestion["name"], "Bad persona")
            self.assertNotIn("persona_voice", suggestion)
            self.assertEqual(suggestion.get("persona_audience"), "to team")
            self.assertNotIn("persona_tone", suggestion)
            self.assertNotIn("intent_purpose", suggestion)
            # Stance should also be rejected because it uses an invalid persona token.
            self.assertNotIn("stance_command", suggestion)

        def test_json_suggestions_accept_snapshot_display_intent(self) -> None:
            # Display names from the persona/intent snapshot should canonicalise to intent tokens.
            payload = {
                "suggestions": [
                    {
                        "name": "Display intent",
                        "recipe": "describe · rog",
                        "intent_purpose": "Vision for Execs",
                        "why": "Ensure snapshot display names are accepted.",
                    }
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )

            from talon_user.lib import personaConfig

            PersonaIntentCatalogSnapshot = personaConfig.PersonaIntentCatalogSnapshot
            IntentPreset = personaConfig.IntentPreset

            custom_snapshot = PersonaIntentCatalogSnapshot(
                persona_presets={},
                persona_spoken_map={},
                persona_axis_tokens={
                    "voice": ["as pioneer"],
                    "audience": ["to scouts"],
                    "tone": ["kindly"],
                },
                intent_presets={
                    "vision": IntentPreset(
                        key="vision",
                        label="Vision label",
                        intent="vision",
                    )
                },
                intent_spoken_map={"vision spoken": "vision"},
                intent_axis_tokens={"intent": ["vision"]},
                intent_buckets={"strategy": ["vision"]},
                intent_display_map={"vision": "Vision for Execs"},
            )

            original_docs_map = gpt_module.persona_docs_map

            def fake_persona_docs_map(axis: str):
                if axis == "intent":
                    return {"vision": "Vision intent"}
                return original_docs_map(axis)

            original_canonical = personaConfig.canonical_persona_token

            def fake_canonical(axis: str, raw: str) -> str:
                if str(raw or "").strip().lower() == "vision for execs".lower():
                    return ""
                return original_canonical(axis, raw)

            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch(
                    "talon_user.lib.personaConfig.persona_intent_catalog_snapshot",
                    return_value=custom_snapshot,
                ),
                patch(
                    "talon_user.GPT.gpt.persona_docs_map",
                    side_effect=fake_persona_docs_map,
                ),
                patch(
                    "talon_user.lib.personaConfig.canonical_persona_token",
                    side_effect=fake_canonical,
                ),
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            self.assertEqual(len(GPTState.last_suggested_recipes), 1)
            suggestion = GPTState.last_suggested_recipes[0]
            self.assertEqual(suggestion["name"], "Display intent")
            self.assertEqual(suggestion.get("intent_purpose"), "vision")

        def test_json_suggestions_alias_only_fields_canonicalise(self) -> None:
            payload = {
                "suggestions": [
                    {
                        "name": "Alias metadata",
                        "recipe": "describe · full · focus · plan · plain · fog",
                        "persona_preset_label": "TEACH JUNIOR DEV",
                        "intent_display": "For-Deciding!",
                        "why": "Ensure alias-only presets canonicalise before storage.",
                    }
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )

            captured: list[dict[str, str]] = []

            def fake_record_suggestions(suggestions, source_key) -> None:
                for entry in suggestions:
                    captured.append(dict(entry))
                GPTState.last_suggested_recipes = list(suggestions)
                GPTState.last_suggest_source = source_key or ""

            with (
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch(
                    "talon_user.GPT.gpt.record_suggestions",
                    side_effect=fake_record_suggestions,
                ),
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                session = session_cls.return_value
                session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            self.assertEqual(len(captured), 1)
            entry = captured[0]
            self.assertEqual(entry.get("persona_preset_key"), "teach_junior_dev")
            self.assertEqual(entry.get("persona_preset_label"), "Teach junior dev")
            self.assertEqual(entry.get("persona_preset_spoken"), "mentor")
            self.assertEqual(entry.get("persona_voice"), "as teacher")
            self.assertEqual(entry.get("persona_audience"), "to junior engineer")
            self.assertEqual(entry.get("persona_tone"), "kindly")
            self.assertEqual(entry.get("intent_purpose"), "decide")
            self.assertEqual(entry.get("intent_preset_key"), "decide")
            self.assertEqual(entry.get("intent_preset_label"), "Decide")
            self.assertEqual(entry.get("intent_display"), "for deciding")

        def test_canonical_persona_value_normalises_aliases(self) -> None:
            self.assertEqual(
                gpt_module._canonical_persona_value("intent", "For-Deciding!"),
                "decide",
            )
            self.assertEqual(
                gpt_module._canonical_persona_value("voice", "AS TEACHER!!!"),
                "as teacher",
            )

        def test_json_suggestions_without_reasoning_still_parse(self) -> None:
            # Payload omits reasoning entirely; validation should still succeed.
            payload = {
                "suggestions": [
                    {
                        "name": "No reasoning",
                        "recipe": "describe · gist · focus · bullets · rog",
                        "persona_voice": "as teacher",
                        "persona_audience": "to junior engineer",
                        "persona_tone": "kindly",
                        "intent_purpose": "for teaching",
                        "stance_command": "model write as teacher to junior engineer kindly",
                        "why": "For teaching-focused summaries.",
                    }
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )

            GPTState.debug_enabled = True

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

            self.assertEqual(len(GPTState.last_suggested_recipes), 1)
            self.assertEqual(GPTState.last_suggested_recipes[0]["name"], "No reasoning")

        def test_all_invalid_suggestions_results_in_no_structured_entries(self) -> None:
            # When every suggestion fails validation (for example, bad recipes),
            # we should end up with an empty structured suggestions list.
            payload = {
                "suggestions": [
                    {
                        "name": "Bad recipe",
                        # Missing directional; normaliser will reject this.
                        "recipe": "describe · gist · focus · bullets",
                        "stance_command": "model write as teacher to junior engineer kindly",
                        "why": "Should be dropped.",
                        "reasoning": "Recipe is missing a directional.",
                    }
                ]
            }
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message(json.dumps(payload))]
            )

            GPTState.debug_enabled = True

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

            self.assertEqual(GPTState.last_suggested_recipes, [])


else:

    class GPTSuggestValidationTests(unittest.TestCase):  # type: ignore[no-redef]
        @unittest.skip("bootstrap not available in this environment")
        def test_placeholder(self) -> None:
            pass
