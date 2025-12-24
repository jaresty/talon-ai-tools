import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:

    class VoiceAudienceToneIntentListTests(unittest.TestCase):
        def setUp(self) -> None:
            from lib.personaConfig import PERSONA_KEY_TO_VALUE

            self.persona_map = PERSONA_KEY_TO_VALUE

        def test_model_voice_list_trimmed_to_core_set(self) -> None:
            keys = set(self.persona_map["voice"].keys())

            # Core voices we expect to keep.
            expected = {
                "as programmer",
                "as prompt engineer",
                "as scientist",
                "as writer",
                "as designer",
                "as teacher",
                "as facilitator",
                "as PM",
                "as junior engineer",
                "as principal engineer",
                "as Kent Beck",
            }
            for token in expected:
                self.assertIn(token, keys, f"Expected {token!r} in modelVoice list")

            # Deprecated or moved voices should not remain.
            banned = {
                "as XP enthusiast",
                "as adversary",
                "as blender",
                "as artist",
                "as logician",
                "as reader",
                "as editor",
                "as other",
                "as liberator",
                "as negotiator",
                "as mediator",
                "as CEO",
                "as CTO",
                "as CFO",
                "as platform team",
                "as stream aligned team",
                "as enabling team",
                "as complicated subsystem team",
                "as various",
                "as perspectives",
                "as systems thinker",
            }
            for token in banned:
                self.assertNotIn(
                    token,
                    keys,
                    f"Deprecated voice token {token!r} should have been removed",
                )

        def test_model_audience_list_trimmed_to_core_set(self) -> None:
            keys = set(self.persona_map["audience"].keys())

            expected = {
                "to managers",
                "to team",
                "to stakeholders",
                "to product manager",
                "to designer",
                "to analyst",
                "to programmer",
                "to LLM",
                "to junior engineer",
                "to principal engineer",
                "to Kent Beck",
                "to CEO",
                "to platform team",
                "to stream aligned team",
                "to XP enthusiast",
            }
            for token in expected:
                self.assertIn(token, keys, f"Expected {token!r} in modelAudience list")

            banned = {
                "to CTO",
                "to CFO",
                "to enabling team",
                "to complicated subsystem team",
                "to receptive",
                "to resistant",
                "to dummy",
                "to various",
                "to perspectives",
                "to systems thinker",
            }
            for token in banned:
                self.assertNotIn(
                    token,
                    keys,
                    f"Deprecated audience token {token!r} should have been removed",
                )

        def test_model_tone_list_trimmed_and_neutral_is_default(self) -> None:
            keys = set(self.persona_map["tone"].keys())

            self.assertEqual(
                keys,
                {
                    "casually",
                    "formally",
                    "directly",
                    "gently",
                    "kindly",
                },
            )

        def test_intent_buckets_cover_all_intents_and_spoken_tokens(self) -> None:
            from lib.personaConfig import (
                INTENT_BUCKETS,
                PERSONA_KEY_TO_VALUE,
                PERSONA_PRESETS,
                INTENT_PRESETS,
                persona_catalog,
                intent_catalog,
                intent_bucket_spoken_tokens,
                persona_intent_catalog_snapshot,
            )

            canonical_tokens = set(PERSONA_KEY_TO_VALUE["intent"].keys())
            bucket_union = set().union(*INTENT_BUCKETS.values())
            self.assertEqual(
                canonical_tokens,
                bucket_union,
                "Intent buckets must cover all canonical intent tokens",
            )
            snapshot = persona_intent_catalog_snapshot()
            display_map = snapshot.intent_display_map
            self.assertTrue(
                all(display_map.get(token) for token in canonical_tokens),
                "Each canonical intent must have a display label",
            )
            buckets_with_labels = intent_bucket_spoken_tokens()
            bucket_labels = {
                label for labels in buckets_with_labels.values() for label in labels
            }
            self.assertTrue(
                bucket_labels, "Expected intent bucket labels to be populated"
            )

            # Persona and intent presets should align with the persona maps.
            voice_keys = set(PERSONA_KEY_TO_VALUE["voice"].keys())
            audience_keys = set(PERSONA_KEY_TO_VALUE["audience"].keys())
            tone_keys = set(PERSONA_KEY_TO_VALUE["tone"].keys())

            for preset in PERSONA_PRESETS:
                if preset.voice:
                    self.assertIn(
                        preset.voice,
                        voice_keys,
                        f"Persona preset {preset.key!r} uses unknown voice {preset.voice!r}",
                    )
                if preset.audience:
                    self.assertIn(
                        preset.audience,
                        audience_keys,
                        f"Persona preset {preset.key!r} uses unknown audience {preset.audience!r}",
                    )
                if preset.tone:
                    self.assertIn(
                        preset.tone,
                        tone_keys,
                        f"Persona preset {preset.key!r} uses unknown tone {preset.tone!r}",
                    )

            for preset in INTENT_PRESETS:
                self.assertIn(
                    preset.intent,
                    canonical_tokens,
                    f"Intent preset {preset.key!r} uses unknown intent {preset.intent!r}",
                )

            # Persona/intent catalogs should round-trip all presets by key.
            persona_map = persona_catalog()
            preset_persona_keys = {preset.key for preset in PERSONA_PRESETS}
            self.assertEqual(set(persona_map.keys()), preset_persona_keys)
            for key, preset in persona_map.items():
                self.assertEqual(
                    key,
                    preset.key,
                    f"persona_catalog entry for {key!r} must expose matching preset.key",
                )

            intent_map = intent_catalog()
            preset_intent_keys = {preset.key for preset in INTENT_PRESETS}
            self.assertEqual(set(intent_map.keys()), preset_intent_keys)
            for key, preset in intent_map.items():
                self.assertEqual(
                    key,
                    preset.key,
                    f"intent_catalog entry for {key!r} must expose matching preset.key",
                )

else:
    if not TYPE_CHECKING:

        class VoiceAudienceToneIntentListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
