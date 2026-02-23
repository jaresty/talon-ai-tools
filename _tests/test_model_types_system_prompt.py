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
    from talon_user.lib.axisConfig import axis_key_to_kanji_map
    from talon_user.lib.modelTypes import GPTSystemPrompt

    class GPTSystemPromptDefaultsTests(unittest.TestCase):
        def setUp(self):
            # Ensure we start from a fresh prompt object for each test.
            self.prompt = GPTSystemPrompt()

        def test_uses_default_settings_for_new_axes(self):
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "narrow")
            settings.set("user.model_default_method", "steps")
            settings.set("user.model_default_form", "bullets")
            settings.set("user.model_default_channel", "slack")

            lines = self.prompt.format_as_array()

            full_desc = axis_key_to_value_map_for("completeness").get("full", "full")
            self.assertTrue(
                any(line.startswith(f"Completeness: {full_desc}") for line in lines),
                f"Completeness line should start with description: {lines}",
            )

        def test_overrides_settings_when_fields_set_explicitly(self):
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "narrow")
            settings.set("user.model_default_method", "steps")
            settings.set("user.model_default_form", "bullets")
            settings.set("user.model_default_channel", "slack")

            prompt = GPTSystemPrompt(
                completeness="max",
                scope="struct",
                method="plan",
                form="code",
                channel="jira",
            )

            lines = prompt.format_as_array()

            max_desc = axis_key_to_value_map_for("completeness").get("max", "max")
            self.assertTrue(
                any(line.startswith(f"Completeness: {max_desc}") for line in lines),
                f"Completeness line should start with description: {lines}",
            )

        def test_hydrated_promptlets_include_kanji(self):
            """ADR-0143: Hydrated promptlets should include kanji when available."""
            prompt = GPTSystemPrompt(
                completeness="full",
                scope="struct",
                method="probe",
            )

            lines = prompt.format_as_array()

            kanji_completeness = axis_key_to_kanji_map("completeness").get("full", "")
            kanji_scope = axis_key_to_kanji_map("scope").get("struct", "")
            kanji_method = axis_key_to_kanji_map("method").get("probe", "")

            self.assertIn(
                kanji_completeness, " ".join(lines), "Completeness should include kanji"
            )
            self.assertIn(kanji_scope, " ".join(lines), "Scope should include kanji")
            self.assertIn(kanji_method, " ".join(lines), "Method should include kanji")

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
