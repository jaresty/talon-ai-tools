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
            self.assertEqual(first["recipe"], "describe · gist · focus bound · structure flow plan · table · jira · rog")

            # The invalid stance suggestion is kept but without a stance_command.
            self.assertEqual(second["name"], "Invalid stance")
            self.assertNotIn("stance_command", second)

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
