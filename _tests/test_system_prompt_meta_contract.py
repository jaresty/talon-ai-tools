import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.modelTypes import GPTSystemPrompt

    class SystemPromptMetaContractTests(unittest.TestCase):
        def test_model_system_prompt_default_mentions_model_interpretation(self) -> None:
            prompt = settings.get("user.model_system_prompt")
            self.assertIsInstance(prompt, str)
            self.assertIn("## Model interpretation", prompt)
            # The richer structure should at least mention suggestions and axes.
            self.assertIn("Suggestion:", prompt)
            self.assertIn("axis", prompt.lower())

        def test_gpt_system_prompt_includes_model_interpretation_heading(self) -> None:
            system_prompt = GPTSystemPrompt()
            lines = system_prompt.format_as_array()

            # The freeform guidance line at the end should mention the
            # structured meta section and its heading.
            tail = lines[-1]
            self.assertIn("## Model interpretation", tail)
            self.assertIn("Suggestion:", tail)
            self.assertIn("axis", tail.lower())

else:
    if not TYPE_CHECKING:
        class SystemPromptMetaContractTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

