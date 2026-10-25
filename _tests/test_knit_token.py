import json
import unittest
from pathlib import Path

from lib.axisConfig import (
    AXIS_KEY_TO_CATEGORY,
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_VALUE,
    axis_token_metadata,
)

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)
RECIPROCAL_TOKENS = ("melody", "seep", "align", "cluster")


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["method"].get("knit", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["method"].get("knit", "")


class KnitMethodTokenTests(unittest.TestCase):
    """knit: rate how strongly the parts of a bounded unit belong together."""

    def test_knit_registered_on_every_method_table(self):
        for table in (
            AXIS_KEY_TO_VALUE,
            AXIS_KEY_TO_LABEL,
            AXIS_KEY_TO_KANJI,
            AXIS_KEY_TO_CATEGORY,
            AXIS_KEY_TO_ROUTING_CONCEPT,
        ):
            self.assertIn("knit", table["method"])

    def test_definition_opens_with_the_response(self):
        self.assertTrue(_definition().startswith("The response"))

    def test_definition_requires_all_three_dimensions(self):
        d = _definition()
        for dimension in ("Purpose:", "Change cause:", "Internal reliance:"):
            self.assertIn(dimension, d)
        self.assertIn("omitting any one is incomplete", d)

    def test_definition_classifies_strong_or_weak(self):
        d = _definition()
        self.assertIn(": strong;", d)
        self.assertIn(": weak.", d)

    def test_definition_names_no_other_token(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in RECIPROCAL_TOKENS:
            self.assertNotIn(other, d)

    def test_metadata_has_heuristics_and_distinctions(self):
        meta = axis_token_metadata()["method"].get("knit", {})
        self.assertTrue(meta.get("heuristics"))
        distinct = {d["token"] for d in meta.get("distinctions", [])}
        self.assertTrue(set(RECIPROCAL_TOKENS) <= distinct)

    def test_each_neighbour_names_knit_in_its_distinctions(self):
        for token in RECIPROCAL_TOKENS:
            with self.subTest(token=token):
                distinct = {
                    d["token"]
                    for d in axis_token_metadata()["method"][token]["distinctions"]
                }
                self.assertIn("knit", distinct)

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))


if __name__ == "__main__":
    unittest.main()
