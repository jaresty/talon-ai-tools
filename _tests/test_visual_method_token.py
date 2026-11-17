"""Guard: visual is positional reasoning, stated without output-format or sibling-token vocabulary."""

import json
import re
import unittest
from pathlib import Path

import prompts.export as _export
from lib.axisConfig import axis_key_to_label_map, axis_key_to_value_map

_REPO = Path(__file__).resolve().parent.parent
_GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)
_SIBLINGS = ("percept", "view", "draw", "diagram", "afford", "struct")


def _contains_string(node, target: str) -> bool:
    if isinstance(node, str):
        return node == target
    if isinstance(node, dict):
        return any(_contains_string(v, target) for v in node.values())
    if isinstance(node, list):
        return any(_contains_string(v, target) for v in node)
    return False


class VisualMethodTokenTests(unittest.TestCase):
    def setUp(self):
        self.d = axis_key_to_value_map("method").get("visual", "")

    def test_keeps_method_opening(self):
        """property [1]: method opening."""
        self.assertTrue(self.d.startswith("The response enhances the task by"), "property [1]: opening changed")

    def test_encodes_relationships_in_perceivable_dimensions(self):
        """property [2]: relationships are assigned to perceivable dimensions beyond position."""
        self.assertIn("perceiv", self.d, "property [2]: no perceivable dimension named")
        self.assertTrue(
            any(w in self.d for w in ("size", "grouping", "contrast")),
            "property [2]: names no dimension beyond position",
        )

    def test_label_speaks_of_encoding_not_position(self):
        """property [7]: the label is not position-only."""
        label = axis_key_to_label_map("method").get("visual", "")
        self.assertNotIn("positional", label.lower(), "property [7]: label still position-only")
        self.assertIn("encod", label.lower(), "property [7]: label does not mention encoding")

    def test_arrangement_belongs_to_the_reasoning(self):
        """property [3]: the arranged things are the concepts in the reasoning, not the subject's look."""
        self.assertIn("reasoning", self.d, "property [3]: description does not locate the arrangement in the reasoning")

    def test_no_output_format_vocabulary(self):
        """property [4]: no output-format phrasing."""
        for w in ("diagram", " map"):
            with self.subTest(word=w):
                self.assertNotIn(w, self.d, f"property [4]: description still says '{w.strip()}'")

    def test_names_no_sibling_token(self):
        """property [5]: no sibling token named."""
        for w in _SIBLINGS:
            with self.subTest(token=w):
                self.assertIsNone(re.search(rf"\b{w}\b", self.d.lower()), f"property [5]: description names '{w}'")

    def test_grammar_copies_carry_current_description(self):
        """property [6]: generated and committed grammars carry the current text."""
        self.assertTrue(
            _contains_string(_export._prompt_grammar_module().prompt_grammar_payload(), self.d),
            "property [6]: generated payload lacks current visual description",
        )
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                self.assertTrue(_contains_string(grammar, self.d), f"property [6]: {rel} lacks current visual description")


if __name__ == "__main__":
    unittest.main()
