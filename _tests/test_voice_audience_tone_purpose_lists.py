import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from pathlib import Path

    class VoiceAudienceTonePurposeListTests(unittest.TestCase):
        def setUp(self) -> None:
            self.root = Path(__file__).resolve().parents[1]
            self.lists_dir = self.root / "GPT" / "lists"

        def _read_keys(self, filename: str) -> set[str]:
            path = self.lists_dir / filename
            self.assertTrue(
                path.is_file(),
                f"Expected list file {filename!r} to exist",
            )
            keys: set[str] = set()
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if (
                        not s
                        or s.startswith("#")
                        or s.startswith("list:")
                        or s == "-"
                    ):
                        continue
                    if ":" not in s:
                        continue
                    key, _ = s.split(":", 1)
                    keys.add(key.strip())
            return keys

        def test_model_voice_list_trimmed_to_core_set(self) -> None:
            keys = self._read_keys("modelVoice.talon-list")

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
            keys = self._read_keys("modelAudience.talon-list")

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
            keys = self._read_keys("modelTone.talon-list")

            self.assertEqual(
                keys,
                {
                    "casually",
                    "formally",
                    "directly",
                    "gently",
                    "kindly",
                    "plainly",
                    "tightly",
                    "headline first",
                },
            )

        def test_model_purpose_list_only_contains_interaction_level_intents(
            self,
        ) -> None:
            keys = self._read_keys("modelPurpose.talon-list")

            expected = {
                "for information",
                "for entertainment",
                "for persuasion",
                "for brainstorming",
                "for deciding",
                "for planning",
                "for evaluating",
                "for coaching",
                "for appreciation",
                "for triage",
                "for announcing",
                "for walk through",
                "for collaborating",
                "for teaching",
                "for project management",
                "for jobs to be done",
                "for user value",
                "for pain points",
                "for definition of done",
                "for facilitation",
                "for discovery questions",
                "for team mapping",
                "for learning",
            }
            self.assertEqual(
                keys,
                expected,
                "modelPurpose list should contain only interaction-level intents after ADR 015",
            )

else:
    if not TYPE_CHECKING:

        class VoiceAudienceTonePurposeListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
