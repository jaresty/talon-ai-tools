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
                INTENT_SPOKEN_TO_CANONICAL,
                PERSONA_KEY_TO_VALUE,
            )

            canonical_tokens = set(PERSONA_KEY_TO_VALUE["intent"].keys())
            bucket_union = set().union(*INTENT_BUCKETS.values())
            self.assertEqual(
                canonical_tokens,
                bucket_union,
                "Intent buckets must cover all canonical intent tokens",
            )
            spoken_canonical = set(INTENT_SPOKEN_TO_CANONICAL.values())
            self.assertEqual(
                canonical_tokens,
                spoken_canonical,
                "Each canonical intent must have a spoken variant in the Talon list",
            )
            self.assertIn("understand", canonical_tokens)
            self.assertIn("understand", spoken_canonical)

else:
    if not TYPE_CHECKING:

        class VoiceAudienceToneIntentListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
