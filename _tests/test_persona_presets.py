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

    from unittest.mock import patch
    from talon_user.GPT import gpt

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
            purpose_keys = set(mapping.get("intent", {}).keys())

            for preset in personaConfig.INTENT_PRESETS:
                with self.subTest(preset=preset.key):
                    self.assertIn(preset.intent, purpose_keys)

        def test_expected_core_persona_presets_present(self) -> None:
            keys = {preset.key for preset in personaConfig.PERSONA_PRESETS}
            self.assertTrue(
                {
                    "peer_engineer_explanation",
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
                    "entertain",
                    "resolve",
                    "understand",
                }
                <= keys
            )

        def test_persona_and_intent_preset_keys_are_unique(self) -> None:
            persona_keys = [preset.key for preset in personaConfig.PERSONA_PRESETS]
            intent_keys = [preset.key for preset in personaConfig.INTENT_PRESETS]

            self.assertEqual(len(persona_keys), len(set(persona_keys)))
            self.assertEqual(len(intent_keys), len(set(intent_keys)))

        def test_intent_presets_cover_all_canonical_intents(self) -> None:
            purpose_keys = set(personaConfig.PERSONA_KEY_TO_VALUE.get("intent", {}))
            preset_intents = {preset.intent for preset in personaConfig.INTENT_PRESETS}
            self.assertEqual(
                purpose_keys,
                preset_intents,
                "Intent presets must cover all canonical intents",
            )

        def test_canonical_persona_token_normalizes_tokens(self) -> None:
            self.assertEqual(
                personaConfig.canonical_persona_token("voice", "As Programmer"),
                "as programmer",
            )
            self.assertEqual(
                personaConfig.canonical_persona_token("intent", "decide"),
                "decide",
            )

        def test_canonical_persona_token_rejects_spoken_intent_aliases(self) -> None:
            self.assertEqual(
                personaConfig.canonical_persona_token("intent", "for deciding"),
                "",
            )

        def test_canonical_persona_token_rejects_unknown_values(self) -> None:
            self.assertEqual(
                personaConfig.canonical_persona_token("tone", "invented-tone"), ""
            )

        def test_persona_intent_catalog_snapshot_shapes(self) -> None:
            snapshot = personaConfig.persona_intent_catalog_snapshot()
            self.assertTrue(snapshot.persona_presets)
            self.assertIn("voice", snapshot.persona_axis_tokens)
            self.assertIn("intent", snapshot.intent_axis_tokens)
            self.assertIn("task", snapshot.intent_buckets)
            for spoken, key in snapshot.persona_spoken_map.items():
                self.assertIn(key, snapshot.persona_presets)
                self.assertTrue(spoken)
            for spoken, key in snapshot.intent_spoken_map.items():
                self.assertIn(key, snapshot.intent_presets)
                self.assertTrue(spoken)
            for bucket, keys in snapshot.intent_buckets.items():
                for key in keys:
                    self.assertIn(key, snapshot.intent_presets)
                    self.assertIn(key, snapshot.intent_display_map)

        def test_persona_docs_guardrail_rejects_unknown_axis_tokens(self) -> None:
            bad_preset = personaConfig.PersonaPreset(
                key="bad",
                label="Bad",
                voice="as programmer",
                audience="to programmer",
                tone="invented-tone",
            )
            patched_presets = personaConfig.PERSONA_PRESETS + (bad_preset,)

            with patch("talon_user.lib.personaConfig.PERSONA_PRESETS", patched_presets):
                with self.assertRaisesRegex(ValueError, "unsupported axis tokens"):
                    gpt._build_persona_intent_docs()


else:
    if not TYPE_CHECKING:

        class PersonaPresetTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
