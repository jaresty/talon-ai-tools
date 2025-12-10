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
    from talon_user.lib.axisMappings import axis_key_to_value_map_for
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

            self.assertIn(
                f"Completeness: {axis_key_to_value_map_for('completeness').get('full', 'full')}",
                lines,
            )
            self.assertIn(
                f"Scope: {axis_key_to_value_map_for('scope').get('narrow', 'narrow')}",
                lines,
            )
            self.assertIn(
                f"Method: {axis_key_to_value_map_for('method').get('steps', 'steps')}",
                lines,
            )
            self.assertIn(
                f"Style: {axis_key_to_value_map_for('style').get('bullets', 'bullets')}",
                lines,
            )

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

            self.assertIn(
                f"Completeness: {axis_key_to_value_map_for('completeness').get('max', 'max')}",
                lines,
            )
            self.assertIn(
                f"Scope: {axis_key_to_value_map_for('scope').get('bound', 'bound')}",
                lines,
            )
            self.assertIn(
                f"Method: {axis_key_to_value_map_for('method').get('plan', 'plan')}",
                lines,
            )
            self.assertIn(
                f"Style: {axis_key_to_value_map_for('style').get('code', 'code')}",
                lines,
            )

        def test_directional_is_hydrated_when_present(self):
            prompt = GPTSystemPrompt(directional="fog")

            lines = prompt.format_as_array()

            directional_desc = axis_key_to_value_map_for("directional").get(
                "fog", "fog"
            )
            self.assertTrue(
                any(
                    line.startswith("Directional: ") and directional_desc in line
                    for line in lines
                )
            )

else:
    if not TYPE_CHECKING:
        class GPTSystemPromptDefaultsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
