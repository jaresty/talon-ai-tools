"""Falsifiable tests for the ibis form token (deliberation map).

Each test must FAIL before the corresponding entries are added to
axisConfig.py and the grammar is regenerated, and PASS after. The tests map
one-to-one onto the retained properties:

    [1] ibis resolves as a form token
    [2] the definition requires typed, nested nodes
    [3] the definition forbids verdicts
    [4] the definition requires a closing Open line
    [5] the catalog entry is complete (label, kanji, routing concept, guidebook)
    [6] every committed grammar copy carries ibis
"""

import json
import unittest
from pathlib import Path

from lib.axisConfig import (
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_VALUE,
    axis_token_metadata,
)

_REPO = Path(__file__).resolve().parent.parent
_GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "web/static/prompt-grammar.json",
)


def _definition() -> str:
    return AXIS_KEY_TO_VALUE["form"].get("ibis", "")


class IbisResolvesTests(unittest.TestCase):
    """property [1]"""

    def test_ibis_in_form_values(self):
        self.assertIn("ibis", AXIS_KEY_TO_VALUE["form"])


class IbisTypedTreeTests(unittest.TestCase):
    """property [2]"""

    def test_definition_names_all_four_node_labels(self):
        for label in ("Question:", "Idea:", "Pro:", "Con:"):
            with self.subTest(label=label):
                self.assertIn(label, _definition())

    def test_definition_requires_nesting_under_a_parent(self):
        self.assertIn("nested under", _definition())


class IbisNoVerdictTests(unittest.TestCase):
    """property [3]"""

    def test_definition_forbids_ranking_selecting_and_concluding(self):
        self.assertIn("No node ranks, selects, or concludes", _definition())


class IbisOpenLineTests(unittest.TestCase):
    """property [4]"""

    def test_definition_requires_closing_open_line(self):
        definition = _definition()
        self.assertIn("The map's final line is 'Open:'", definition)
        self.assertNotIn("The last line is", definition)
        self.assertIn("'Open: none'", definition)


class IbisExchangeManagementTests(unittest.TestCase):
    """property [7]"""

    def test_definition_gives_exchange_management_moves_no_node(self):
        self.assertIn(
            "is not a contribution and has no node", _definition()
        )


class IbisReplyRoutingTests(unittest.TestCase):
    """property [8]"""

    def test_definition_routes_reply_to_argument_through_a_question(self):
        self.assertIn(
            "A reply to a Pro or Con is a Question nested under that Pro or Con",
            _definition(),
        )


class IbisCatalogEntryTests(unittest.TestCase):
    """property [5]"""

    def test_label_present(self):
        self.assertTrue(AXIS_KEY_TO_LABEL["form"].get("ibis"))

    def test_routing_concept_present(self):
        self.assertTrue(AXIS_KEY_TO_ROUTING_CONCEPT["form"].get("ibis"))

    def test_kanji_is_one_character(self):
        self.assertEqual(len(AXIS_KEY_TO_KANJI["form"].get("ibis", "")), 1)

    def test_kanji_unique_across_form_axis(self):
        kanji = AXIS_KEY_TO_KANJI["form"].get("ibis")
        others = [
            token
            for token, value in AXIS_KEY_TO_KANJI["form"].items()
            if token != "ibis" and value == kanji
        ]
        self.assertTrue(kanji)
        self.assertEqual(others, [])

    def test_guidebook_has_distinctions_and_heuristics(self):
        entry = axis_token_metadata().get("form", {}).get("ibis", {})
        self.assertTrue(entry.get("distinctions"))
        self.assertTrue(entry.get("heuristics"))


class IbisGrammarCopiesTests(unittest.TestCase):
    """property [6]"""

    def test_every_grammar_copy_carries_ibis(self):
        for relative in _GRAMMAR_COPIES:
            with self.subTest(copy=relative):
                data = json.loads((_REPO / relative).read_text(encoding="utf-8"))
                self.assertIn("ibis", data["axes"]["definitions"]["form"])


if __name__ == "__main__":
    unittest.main()
