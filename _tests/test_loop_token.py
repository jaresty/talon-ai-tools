import json
import re
import unittest
from pathlib import Path

from lib.axisConfig import (
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
RECIPROCAL_TOKENS = ("systemic", "effects", "grove")
OTHER_TOKENS = ("systemic", "effects", "grove", "flow", "simulation", "diagram")


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["form"].get("loop", "")


def _grammar_definition(path: str) -> str:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return json.load(handle)["axes"]["definitions"]["form"].get("loop", "")


class LoopFormTokenTests(unittest.TestCase):
    """loop: a causal loop map of listed signed links and labeled closed cycles."""

    def test_loop_registered_on_every_form_table(self):
        for table in (
            AXIS_KEY_TO_VALUE,
            AXIS_KEY_TO_LABEL,
            AXIS_KEY_TO_KANJI,
                    AXIS_KEY_TO_ROUTING_CONCEPT,
        ):
            self.assertIn("loop", table["form"])

    def test_definition_opens_as_a_causal_loop_map(self):
        self.assertTrue(_definition().startswith("The response is a causal loop map"))

    def test_definition_states_the_root_criterion(self):
        self.assertIn(
            "every claim about a cycle can be read off the links it states", _definition()
        )

    def test_definition_requires_quantity_variables(self):
        self.assertIn("quantity that can rise or fall", _definition())

    def test_definition_states_each_link_once_with_an_identifier(self):
        d = _definition()
        self.assertIn("Each link is stated once, with an identifier, from cause to effect", d)

    def test_definition_ties_the_reason_verb_to_the_direction(self):
        d = _definition()
        self.assertIn("'an increase in <cause> raises <effect>' when the effect moves with the cause", d)
        self.assertIn("'an increase in <cause> lowers <effect>' when it moves against it", d)

    def test_definition_forces_a_delay_decision_on_every_link(self):
        d = _definition()
        self.assertIn("ending with 'delayed' when the effect appears only after the cause has held its new value", d)
        self.assertIn("and with 'immediate' otherwise", d)

    def test_definition_derives_cycles_from_cited_link_identifiers(self):
        d = _definition()
        self.assertIn("lists the identifiers of its links in order", d)
        self.assertIn("each link's effect being the next link's cause and the last effect being the first cause", d)
        self.assertIn("No cycle cites a link that has not been stated", d)

    def test_definition_keeps_a_cycle_simple_and_separates_shared_loops(self):
        d = _definition()
        self.assertIn("passes through no variable twice", d)
        self.assertIn("Loops that share a variable are separate cycles", d)

    def test_definition_counts_lowers_links_and_labels_by_parity(self):
        d = _definition()
        self.assertIn("the number of those links whose reason says 'lowers'", d)
        self.assertIn("'reinforcing' when that count is even", d)
        self.assertIn("'balancing' when it is odd", d)

    def test_definition_names_no_other_token_or_subject_domain(self):
        d = _definition().lower()
        self.assertTrue(d, "definition must exist before it can be checked")
        for other in OTHER_TOKENS:
            self.assertIsNone(re.search(rf"\b{other}\b", d), other)
        for domain in ("code", "software", "library", "framework", "mermaid"):
            self.assertIsNone(re.search(rf"\b{domain}\b", d), domain)

    def test_metadata_has_heuristics_and_distinctions(self):
        meta = axis_token_metadata()["form"].get("loop", {})
        self.assertTrue(meta.get("heuristics"))
        distinct = {d["token"] for d in meta.get("distinctions", [])}
        self.assertTrue(set(RECIPROCAL_TOKENS) <= distinct)

    def test_each_neighbour_names_loop_in_its_distinctions(self):
        for token in RECIPROCAL_TOKENS:
            with self.subTest(token=token):
                distinct = {
                    d["token"]
                    for d in axis_token_metadata()["method"][token]["distinctions"]
                }
                self.assertIn("loop", distinct)

    def test_every_grammar_copy_carries_the_same_definition(self):
        source = _definition()
        self.assertTrue(source, "source definition must exist before copies can match")
        for path in GRAMMAR_COPIES:
            with self.subTest(carrier=path):
                self.assertEqual(source, _grammar_definition(path))


if __name__ == "__main__":
    unittest.main()
