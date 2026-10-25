import json
import unittest
from pathlib import Path

from lib.axisConfig import AXIS_KEY_TO_VALUE, axis_token_metadata

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["method"].get("pulse", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["method"].get("pulse", "")


class PulseMethodTokenTests(unittest.TestCase):
    """pulse: model a transfer as content vs medium, and how the medium changes what arrives."""

    def test_definition_keeps_the_fixed_core(self):
        d = _definition()
        self.assertTrue(d.startswith("The response"))
        self.assertIn("what is being conveyed from the medium that carries it", d)
        self.assertIn("detects and corrects", d)

    def test_definition_names_the_discipline(self):
        self.assertIn("communication theory", _definition())

    def test_definition_covers_delivery_properties(self):
        d = _definition()
        for prop in ("fidelity", "reach", "timing", "persistence", "attention"):
            self.assertIn(prop, d)

    def test_definition_covers_changes_beyond_distortion(self):
        d = _definition()
        for change in ("distortion", "loss", "delay"):
            self.assertIn(change, d)

    def test_definition_names_no_other_token(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in ("flow", "systemic", "relay", "mesh", "trace"):
            self.assertNotIn(other, d.split())

    def test_heuristics_reach_delivery_questions(self):
        heuristics = " ".join(axis_token_metadata()["method"]["pulse"]["heuristics"])
        for phrase in ("notification", "synchronous", "attention"):
            self.assertIn(phrase, heuristics)
        self.assertIn("signal-to-noise", heuristics)

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))


if __name__ == "__main__":
    unittest.main()
