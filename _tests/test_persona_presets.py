import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib import personaConfig

    class PersonaPresetTests(unittest.TestCase):
        def test_persona_presets_use_known_tokens(self) -> None:
            mapping = personaConfig.PERSONA_KEY_TO_VALUE
            voice_keys = set(mapping.get("voice", {}).keys())
            audience_keys = set(mapping.get("audience", {}).keys())
            tone_keys = set(mapping.get("tone", {}).keys())

            for preset in personaConfig.PERSONA_PRESETS:
                with self.subTest(preset=preset.key):
                    if preset.voice is not None:
                        self.assertIn(preset.voice, voice_keys)
                    if preset.audience is not None:
                        self.assertIn(preset.audience, audience_keys)
                    if preset.tone is not None:
                        self.assertIn(preset.tone, tone_keys)

        def test_intent_presets_use_known_purposes(self) -> None:
            mapping = personaConfig.PERSONA_KEY_TO_VALUE
            purpose_keys = set(mapping.get("purpose", {}).keys())

            for preset in personaConfig.INTENT_PRESETS:
                with self.subTest(preset=preset.key):
                    self.assertIn(preset.purpose, purpose_keys)

        def test_expected_core_persona_presets_present(self) -> None:
            keys = {preset.key for preset in personaConfig.PERSONA_PRESETS}
            self.assertTrue(
                {
                    "peer_engineer_explanation",
                    "coach_junior",
                    "teach_junior_dev",
                    "stakeholder_facilitator",
                    "designer_to_pm",
                    "product_manager_to_team",
                    "executive_brief",
                }
                <= keys
            )

        def test_expected_intent_presets_present(self) -> None:
            keys = {preset.key for preset in personaConfig.INTENT_PRESETS}
            self.assertTrue(
                {
                    "teach",
                    "decide",
                    "plan",
                    "evaluate",
                    "brainstorm",
                    "appreciate",
                    "persuade",
                    "coach",
                    "collaborate",
                    "entertain",
                }
                <= keys
            )

        def test_persona_and_intent_preset_keys_are_unique(self) -> None:
            persona_keys = [preset.key for preset in personaConfig.PERSONA_PRESETS]
            intent_keys = [preset.key for preset in personaConfig.INTENT_PRESETS]

            self.assertEqual(len(persona_keys), len(set(persona_keys)))
            self.assertEqual(len(intent_keys), len(set(intent_keys)))


else:
    if not TYPE_CHECKING:

        class PersonaPresetTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
