"""Guard: winnow lists and counts its candidates before resizing them."""

import json
import re
import unittest
from pathlib import Path

from lib.axisConfig import axis_key_to_value_map

_REPO = Path(__file__).resolve().parent.parent
_GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)
_OPENING = (
    "The response first lists each candidate under consideration and states their count "
    "as a numeral, then resizes each candidate"
)
_OTHER_TOKENS = ("presume", "pilot", "prioritize", "pick", "prune", "collapse")


class WinnowCandidateListTests(unittest.TestCase):
    def test_winnow_opens_by_listing_and_counting_candidates(self):
        """property [1]: the pool is listed with a numeral count before any resizing."""
        d = axis_key_to_value_map("method").get("winnow", "")
        self.assertTrue(d.startswith(_OPENING), "property [1]: winnow must open by listing and counting candidates")

    def test_winnow_keeps_its_other_clauses(self):
        """property [1]: the selection score and the no-action candidate remain."""
        d = axis_key_to_value_map("method").get("winnow", "")
        self.assertIn("value-over-cost score", d)
        self.assertIn("taking no action", d)

    def test_winnow_names_no_other_token(self):
        """property [1]: the description states only its own concern."""
        d = axis_key_to_value_map("method").get("winnow", "")
        for t in _OTHER_TOKENS:
            with self.subTest(token=t):
                self.assertIsNone(re.search(rf"\b{t}\b", d), f"property [1]: names token {t}")

    def test_grammar_copies_carry_the_new_opening(self):
        """property [1]: every shipped grammar copy matches the source."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                g = json.loads((_REPO / rel).read_text())
                d = g["axes"]["definitions"]["method"]["winnow"]
                self.assertTrue(d.startswith(_OPENING), f"property [1]: {rel} lacks the new opening")


if __name__ == "__main__":
    unittest.main()
