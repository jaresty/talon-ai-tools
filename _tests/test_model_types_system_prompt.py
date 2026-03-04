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

        # ADR-0153 T-1: form_default_completeness override

        def test_commit_form_defaults_to_gist_completeness(self):
            """ADR-0153 T-1: commit form without explicit completeness uses gist."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(form="commit")
            lines = prompt.format_as_array()
            gist_desc = axis_key_to_value_map_for("completeness").get("gist", "gist")
            self.assertTrue(
                any(line.startswith(f"Completeness: {gist_desc}") for line in lines),
                f"ADR-0153 T-1: commit form should default to gist completeness, got: {lines}",
            )
            full_desc = axis_key_to_value_map_for("completeness").get("full", "full")
            self.assertFalse(
                any(line.startswith(f"Completeness: {full_desc}") for line in lines),
                f"ADR-0153 T-1: commit form must not use full completeness by default, got: {lines}",
            )

        def test_explicit_completeness_not_overridden_by_form_default(self):
            """ADR-0153 T-1: explicit completeness wins over form_default_completeness."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(form="commit", completeness="full")
            lines = prompt.format_as_array()
            full_desc = axis_key_to_value_map_for("completeness").get("full", "full")
            self.assertTrue(
                any(line.startswith(f"Completeness: {full_desc}") for line in lines),
                f"ADR-0153 T-1: explicit full completeness must not be overridden by form default, got: {lines}",
            )

        # ADR-0153 T-2: conflict notes

        def test_gist_fig_renders_conflict_note(self):
            """ADR-0153 T-2: gist + fig must render a ↳ conflict note."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(completeness="gist", directional="fig")
            lines = prompt.format_as_array()
            self.assertTrue(
                any("↳" in line for line in lines),
                f"ADR-0153 T-2: expected conflict note (↳) for gist+fig, got: {lines}",
            )
            self.assertTrue(
                any("completeness governs" in line for line in lines),
                f"ADR-0153 T-2: conflict note must declare which constraint governs, got: {lines}",
            )

        def test_skim_fog_renders_conflict_note(self):
            """ADR-0153 T-2: skim + fog must render a ↳ conflict note."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(completeness="skim", directional="fog")
            lines = prompt.format_as_array()
            self.assertTrue(
                any("↳" in line for line in lines),
                f"ADR-0153 T-2: expected conflict note (↳) for skim+fog, got: {lines}",
            )

        def test_non_conflicting_pair_has_no_note(self):
            """ADR-0153 T-2: non-cautionary combination must not render a conflict note."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(completeness="full", directional="fig")
            lines = prompt.format_as_array()
            self.assertFalse(
                any("↳" in line for line in lines),
                f"ADR-0153 T-2: non-conflicting full+fig must not render a conflict note, got: {lines}",
            )

        def test_commit_form_fig_directional_renders_conflict_note(self):
            """ADR-0153 T-2: commit form + fig directional must render a form-level conflict note."""
            settings.set("user.model_default_completeness", "")
            prompt = GPTSystemPrompt(form="commit", directional="fig")
            lines = prompt.format_as_array()
            self.assertTrue(
                any("↳" in line for line in lines),
                f"ADR-0153 T-2: expected conflict note (↳) for commit+fig, got: {lines}",
            )

else:
    if not TYPE_CHECKING:

        class GPTSystemPromptDefaultsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
