import re
import unittest
from pathlib import Path

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


def _talon_settings():
    from talon_user.lib import talonSettings

    return talonSettings


class VoiceAxisSlotTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            self.settings = _talon_settings()
        except Exception as exc:  # pragma: no cover - environment dependent
            self.skipTest(f"talonSettings not importable here: {exc}")

    def _rule_slot_counts(self) -> dict[str, int]:
        source = (
            Path(__file__).resolve().parents[1] / "lib" / "talonSettings.py"
        ).read_text()
        rule = source.split("@mod.capture(", 1)[1].split("def modelPrompt", 1)[0]
        counts = {}
        for axis in ("scope", "method", "form", "channel", "directional"):
            counts[axis] = len(re.findall(r"\{user\.%sModifier\}" % axis, rule))
        return counts

    def test_slots_match_the_modelprompt_rule(self) -> None:
        """The named voice limits equal the optional captures in the spoken-command rule."""

        self.assertEqual(self.settings.voice_axis_slots(), self._rule_slot_counts())

    def test_clamp_keeps_the_most_recent_tokens(self) -> None:
        """A replay snapshot over the voice limit keeps its latest tokens, per axis."""

        clamp = self.settings.clamp_to_voice_slots
        self.assertEqual(clamp("scope", ["a", "b", "c"]), ["b", "c"])
        self.assertEqual(clamp("method", ["a", "b", "c", "d"]), ["b", "c", "d"])
        self.assertEqual(clamp("channel", ["x", "y"]), ["y"])
        self.assertEqual(clamp("form", []), [])

    def test_caps_summary_reports_voice_limits_not_build_limits(self) -> None:
        """The help canvas states what can be spoken, not what bar build accepts."""

        summary = self.settings.voice_caps_summary()
        self.assertEqual(summary, "S≤2 · M≤3 · F≤1 · Ch≤1 · Dir=1")
        self.assertNotIn("M≤5", summary)
        self.assertNotIn("Ch≤3", summary)


if __name__ == "__main__":
    unittest.main()
