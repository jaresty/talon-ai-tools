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

    class GPTSystemPromptDefaultsTests(unittest.TestCase):
        def setUp(self):
            # Ensure we start from a fresh prompt object for each test.
            self.prompt = GPTSystemPrompt()

        def test_uses_default_settings_for_new_axes(self):
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "narrow")
            settings.set("user.model_default_method", "steps")
            settings.set("user.model_default_style", "bullets")

            lines = self.prompt.format_as_array()

            self.assertIn("Completeness: full", lines)
            self.assertIn("Scope: narrow", lines)
            self.assertIn("Method: steps", lines)
            self.assertIn("Style: bullets", lines)

        def test_overrides_settings_when_fields_set_explicitly(self):
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "narrow")
            settings.set("user.model_default_method", "steps")
            settings.set("user.model_default_style", "bullets")

            prompt = GPTSystemPrompt(
                completeness="max",
                scope="bound",
                method="plan",
                style="code",
            )

            lines = prompt.format_as_array()

            self.assertIn("Completeness: max", lines)
            self.assertIn("Scope: bound", lines)
            self.assertIn("Method: plan", lines)
            self.assertIn("Style: code", lines)

else:
    if not TYPE_CHECKING:
        class GPTSystemPromptDefaultsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
