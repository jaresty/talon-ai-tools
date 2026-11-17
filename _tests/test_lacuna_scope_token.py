"""Guard: lacuna is a scope token (focus on absences implied by what is present)."""

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
_SCOPE_SIBLINGS = ("relations", "struct", "thing", "assume", "fail")
_METHOD_SIBLINGS = ("gap", "unknowns", "conjoin")
_RECIPROCAL = tuple(("scope", t) for t in _SCOPE_SIBLINGS) + tuple(("method", t) for t in _METHOD_SIBLINGS)


def _list_tokens(grammar: dict, axis: str) -> list:
    return grammar.get("axes", {}).get("list_tokens", {}).get(axis, [])


def _distinction_targets(axis: str, token: str) -> set:
    meta = axis_token_metadata().get(axis, {}).get(token, {})
    return {d["token"] for d in meta.get("distinctions", [])}


class LacunaScopeTokenTests(unittest.TestCase):
    def test_lacuna_is_scope_and_only_scope(self):
        """property [1]: lacuna is a scope token and not a method token."""
        self.assertIn("lacuna", axis_key_to_value_map("scope"), "property [1]: lacuna missing from scope")
        self.assertNotIn("lacuna", axis_key_to_value_map("method"), "property [1]: lacuna in method")

    def test_lacuna_description_is_a_focus_statement_with_implied_absence(self):
        """property [2]: a focus statement; an absence counts only when the present elements imply it."""
        d = axis_key_to_value_map("scope").get("lacuna", "")
        self.assertTrue(d.startswith("The response focuses on"), "property [2]: must begin 'The response focuses on'")
        self.assertIn("imply", d, "property [2]: must state that absences are implied by present elements")
        self.assertIn("present", d, "property [2]: must name the present elements")

    def test_lacuna_description_names_no_sibling_token(self):
        """property [2]: the description states only its own focus and names no other token."""
        d = axis_key_to_value_map("scope").get("lacuna", "")
        self.assertTrue(d, "property [2]: lacuna has no description")
        for t in _SCOPE_SIBLINGS + _METHOD_SIBLINGS:
            with self.subTest(token=t):
                self.assertIsNone(
                    re.search(rf"\b{t}\b", d), f"property [2]: description names sibling token {t}"
                )

    def test_lacuna_has_label_kanji_routing(self):
        """property [3]: lacuna has a scope label, kanji and routing concept."""
        for name, m in (
            ("label", axis_key_to_label_map("scope")),
            ("kanji", axis_key_to_kanji_map("scope")),
            ("routing", axis_key_to_routing_concept_map("scope")),
        ):
            with self.subTest(record=name):
                self.assertTrue(m.get("lacuna", ""), f"property [3]: lacuna has no scope {name}")

    def test_lacuna_distinctions_and_heuristics(self):
        """property [4]: distinctions cover the eight neighbours; heuristics exist."""
        meta = axis_token_metadata().get("scope", {}).get("lacuna", {})
        named = {d["token"] for d in meta.get("distinctions", [])}
        for t in _SCOPE_SIBLINGS + _METHOD_SIBLINGS:
            with self.subTest(token=t):
                self.assertIn(t, named, f"property [4]: no distinction against {t}")
        self.assertTrue(meta.get("heuristics"), "property [4]: no heuristics")

    def test_neighbours_name_lacuna_in_their_distinctions(self):
        """property [5]: each neighbour carries the reciprocal distinction."""
        for axis, t in _RECIPROCAL:
            with self.subTest(axis=axis, token=t):
                self.assertIn(
                    "lacuna", _distinction_targets(axis, t), f"property [5]: {t} lacks a distinction against lacuna"
                )

    def test_generated_grammar_lists_lacuna_under_scope(self):
        """property [6]: the generated grammar agrees."""
        grammar = _export._prompt_grammar_module().prompt_grammar_payload()
        self.assertIn("lacuna", _list_tokens(grammar, "scope"), "property [6]: payload scope lacks lacuna")

    def test_committed_grammar_copies_list_lacuna_under_scope(self):
        """property [6]: every committed grammar copy agrees."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                self.assertIn("lacuna", _list_tokens(grammar, "scope"), f"property [6]: {rel} lacks lacuna")


if __name__ == "__main__":
    unittest.main()
