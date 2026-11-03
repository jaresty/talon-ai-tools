"""Falsifiable tests for the ibis form token (deliberation map).

Each test must FAIL before the corresponding entries are added to
axisConfig.py and the grammar is regenerated, and PASS after. The tests map
onto the retained properties:

    [1]  ibis resolves as a form token
    [2]  the definition names the node types, that each node names its type,
         and that each non-root node shows its parent
    [3]  the map records the deliberation and does not decide it
    [4]  the open items sit under a label and nothing else
    [5]  the catalog entry is complete (label, kanji, routing concept, guidebook)
    [6]  every committed grammar copy carries ibis
    [7]  moves that only manage the exchange have no node
    [8]  a reply to a Pro or Con attaches through a Question
    [12] the definition fixes no rendering syntax
    [13] every contribution that poses a question or states an option, support
         or objection has one node, including one the speaker defers
    [14] the definition carries no evidence-provenance concept: which nodes the
         subject states and which are inferred belongs to ``pin``, and the
         guidebook entry says so
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

    def test_definition_names_the_node_types(self):
        self.assertIn("The node types are Question, Idea, Pro and Con", _definition())

    def test_definition_requires_each_node_to_name_its_type(self):
        self.assertIn("Each node names its type", _definition())

    def test_definition_requires_each_non_root_node_to_show_its_parent(self):
        self.assertIn(
            "each node other than a root Question shows its parent", _definition()
        )

    def test_definition_names_the_relations(self):
        self.assertIn(
            "an Idea answers a Question, a Pro supports an Idea, a Con opposes an Idea",
            _definition(),
        )


class IbisNoVerdictTests(unittest.TestCase):
    """property [3]"""

    def test_definition_says_the_map_does_not_decide(self):
        self.assertIn(
            "The map records the deliberation and does not decide it", _definition()
        )


class IbisOpenItemsTests(unittest.TestCase):
    """property [4]"""

    def test_definition_states_open_items_under_a_label(self):
        definition = _definition()
        self.assertIn(
            "The map states its open items under the label 'Open', each as the text "
            "of a node of the map",
            definition,
        )
        self.assertIn(
            "every Question with no Idea answering it and every Idea with no Pro or Con",
            definition,
        )
        self.assertIn(
            "or 'Open: none'; an item that is not a node of the map is not listed",
            definition,
        )
        self.assertNotIn("The last line is", definition)
        self.assertNotIn("final line is", definition)


class IbisCoverageTests(unittest.TestCase):
    """properties [7] and [13]"""

    def test_a_deferred_contribution_keeps_its_node(self):
        self.assertIn(
            "has exactly one node, including one the speaker defers", _definition()
        )

    def test_exchange_management_moves_have_no_node_and_appear_nowhere(self):
        self.assertIn(
            "a move that only manages the exchange of contributions, such as calling "
            "for closure, signalling agreement, or deferring a topic, has no node and "
            "appears nowhere in the map",
            _definition(),
        )

    def test_the_map_holds_nodes_and_open_items_and_nothing_else(self):
        self.assertIn(
            "The map holds its nodes and its open items and nothing else",
            _definition(),
        )


class IbisReplyRoutingTests(unittest.TestCase):
    """property [8]"""

    def test_definition_routes_reply_to_argument_through_a_question(self):
        self.assertIn(
            "a reply to a Pro or Con attaches through a Question that node raised, "
            "with the reply as an Idea answering it",
            _definition(),
        )


class IbisMediumNeutralTests(unittest.TestCase):
    """property [12]: structure is defined; rendering belongs to the medium"""

    def test_definition_fixes_no_rendering_syntax(self):
        definition = _definition()
        for phrase in (
            "Each node is one line opening with its type label",
            "line opening with its type name and a colon",
            "The map ends with a line",
            "separated by semicolons",
            "nothing better",
            "whatever form the medium offers",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, definition)


class IbisOrthogonalityTests(unittest.TestCase):
    """property [14]: provenance belongs to pin, not to this form"""

    def test_definition_carries_no_provenance_concept(self):
        definition = _definition()
        for phrase in (
            "span of the subject",
            "records no span",
            "implied Question",
            "stated Question",
            "never implied",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, definition)

    def test_guidebook_routes_provenance_to_pin(self):
        entry = axis_token_metadata().get("form", {}).get("ibis", {})
        tokens = [d.get("token") for d in entry.get("distinctions", [])]
        self.assertIn("pin", tokens)


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
