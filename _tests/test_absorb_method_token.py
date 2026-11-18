"""Guard: absorb is a method token (reason as if every step may be repeated)."""

import json
import re
import unittest
from pathlib import Path

import prompts.export as _export
from lib.axisConfig import (
    axis_key_to_kanji_map,
    axis_key_to_label_map,
    axis_key_to_routing_concept_map,
    axis_key_to_value_map,
    axis_token_metadata,
)

_REPO = Path(__file__).resolve().parent.parent
_GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)
_METHOD_SIBLINGS = ("robust", "preserve", "perturb")
_COMPLETENESS_SIBLINGS = ("fixpoint",)
_RECIPROCAL = tuple(("method", t) for t in _METHOD_SIBLINGS) + tuple(("completeness", t) for t in _COMPLETENESS_SIBLINGS)


def _list_tokens(grammar: dict, axis: str) -> list:
    return grammar.get("axes", {}).get("list_tokens", {}).get(axis, [])


def _distinction_targets(axis: str, token: str) -> set:
    meta = axis_token_metadata().get(axis, {}).get(token, {})
    return {d["token"] for d in meta.get("distinctions", [])}


class AbsorbMethodTokenTests(unittest.TestCase):
    def test_absorb_is_method_and_only_method(self):
        """property [1]: absorb is a method token and not a scope token."""
        self.assertIn("absorb", axis_key_to_value_map("method"), "property [1]: absorb missing from method")
        self.assertNotIn("absorb", axis_key_to_value_map("scope"), "property [1]: absorb in scope")

    def test_absorb_description_is_a_posture_about_repetition(self):
        """property [2]: a reasoning posture that treats each step as repeatable."""
        d = axis_key_to_value_map("method").get("absorb", "")
        self.assertTrue(d.startswith("The response enhances the task by"), "property [2]: must begin 'The response enhances the task by'")
        self.assertIn("performed again", d, "property [2]: must treat each step as repeatable")
        self.assertIn("second", d, "property [2]: must state what a second performance changes")

    def test_absorb_description_names_no_sibling_token(self):
        """property [2]: the description states only its own posture and names no other token."""
        d = axis_key_to_value_map("method").get("absorb", "")
        self.assertTrue(d, "property [2]: absorb has no description")
        for t in _METHOD_SIBLINGS + _COMPLETENESS_SIBLINGS:
            with self.subTest(token=t):
                self.assertIsNone(re.search(rf"\b{t}\b", d), f"property [2]: description names sibling token {t}")

    def test_absorb_has_label_kanji_routing(self):
        """property [3]: absorb has a method label, kanji and routing concept."""
        for name, m in (
            ("label", axis_key_to_label_map("method")),
            ("kanji", axis_key_to_kanji_map("method")),
            ("routing", axis_key_to_routing_concept_map("method")),
        ):
            with self.subTest(record=name):
                self.assertTrue(m.get("absorb", ""), f"property [3]: absorb has no method {name}")

    def test_absorb_distinctions_and_heuristics(self):
        """property [4]: distinctions cover the four neighbours; heuristics exist."""
        meta = axis_token_metadata().get("method", {}).get("absorb", {})
        named = {d["token"] for d in meta.get("distinctions", [])}
        for t in _METHOD_SIBLINGS + _COMPLETENESS_SIBLINGS:
            with self.subTest(token=t):
                self.assertIn(t, named, f"property [4]: no distinction against {t}")
        self.assertTrue(meta.get("heuristics"), "property [4]: no heuristics")

    def test_neighbours_name_absorb_in_their_distinctions(self):
        """property [5]: each neighbour carries the reciprocal distinction."""
        for axis, t in _RECIPROCAL:
            with self.subTest(axis=axis, token=t):
                self.assertIn("absorb", _distinction_targets(axis, t), f"property [5]: {t} lacks a distinction against absorb")

    def test_generated_grammar_lists_absorb_under_method(self):
        """property [6]: the generated grammar agrees."""
        grammar = _export._prompt_grammar_module().prompt_grammar_payload()
        self.assertIn("absorb", _list_tokens(grammar, "method"), "property [6]: payload method lacks absorb")

    def test_committed_grammar_copies_list_absorb_under_method(self):
        """property [6]: every committed grammar copy agrees."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                self.assertIn("absorb", _list_tokens(grammar, "method"), f"property [6]: {rel} lacks absorb")


if __name__ == "__main__":
    unittest.main()
