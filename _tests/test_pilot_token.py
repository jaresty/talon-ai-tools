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
from lib.compositionConfig import COMPOSITIONS

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)
RECIPROCAL_TOKENS = ("presume", "lazy", "prioritize", "winnow", "experimental")


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["method"].get("pilot", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["method"].get("pilot", "")


def _pair_entry() -> dict:
    for entry in COMPOSITIONS:
        if set(entry.get("tokens", [])) == {"presume", "pilot"}:
            return entry
    return {}


class PilotMethodTokenTests(unittest.TestCase):
    """pilot: order steps and select options by learning rate."""

    def test_pilot_registered_on_every_method_table(self):
        for table in (
            AXIS_KEY_TO_VALUE,
            AXIS_KEY_TO_LABEL,
            AXIS_KEY_TO_KANJI,
            AXIS_KEY_TO_CATEGORY,
            AXIS_KEY_TO_ROUTING_CONCEPT,
        ):
            self.assertIn("pilot", table["method"])

    def test_pilot_kanji_is_sen(self):
        self.assertEqual(AXIS_KEY_TO_KANJI["method"].get("pilot"), "先")

    def test_definition_opens_with_the_response(self):
        self.assertTrue(_definition().startswith("The response"))

    def test_definition_ranks_by_learning_rate(self):
        self.assertIn("learning rate", _definition())

    def test_definition_requires_an_unknown_line_with_observable_and_rate(self):
        d = _definition()
        self.assertIn("Unknown: <what is not yet known>", d)
        self.assertIn("Rate: <high | medium | low>", d)
        self.assertIn("Unknown: none", d)

    def test_definition_orders_steps_by_the_stated_rate(self):
        self.assertIn("descending order of the stated rate", _definition())

    def test_definition_closes_with_reordering_or_none(self):
        self.assertIn("No reordering", _definition())

    def test_definition_names_no_other_token(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in RECIPROCAL_TOKENS:
            self.assertNotIn(other, d)

    def test_metadata_has_heuristics_and_distinctions_on_the_five_tokens(self):
        meta = axis_token_metadata()["method"].get("pilot", {})
        self.assertTrue(meta.get("heuristics"))
        distinct = {d["token"] for d in meta.get("distinctions", [])}
        self.assertTrue(set(RECIPROCAL_TOKENS) <= distinct)

    def test_each_of_the_five_tokens_names_pilot_in_its_distinctions(self):
        for token in RECIPROCAL_TOKENS:
            with self.subTest(token=token):
                distinct = {
                    d["token"]
                    for d in axis_token_metadata()["method"][token]["distinctions"]
                }
                self.assertIn("pilot", distinct)

    def test_composition_with_presume_states_the_precedence(self):
        prose = _pair_entry().get("prose", "")
        self.assertTrue(prose, "a presume+pilot composition entry must exist")
        self.assertIn(
            "presume governs whether a choice may be taken without asking and how it is closed",
            prose,
        )
        self.assertIn(
            "pilot governs which step comes first and which option is taken among the options the subject does not rule out",
            prose,
        )

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))


if __name__ == "__main__":
    unittest.main()
