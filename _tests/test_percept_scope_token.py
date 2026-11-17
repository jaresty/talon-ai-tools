"""Guard: percept is a scope token (focus on perceptual presentation and attention)."""

import json
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


def _list_tokens(grammar: dict, axis: str) -> list:
    return grammar.get("axes", {}).get("list_tokens", {}).get(axis, [])


class PerceptScopeTokenTests(unittest.TestCase):
    def test_percept_is_scope_and_only_scope(self):
        """property [1]: percept is a scope token and not a method token."""
        self.assertIn("percept", axis_key_to_value_map("scope"), "property [1]: percept missing from scope")
        self.assertNotIn("percept", axis_key_to_value_map("method"), "property [1]: percept in method")

    def test_percept_description_is_a_focus_statement(self):
        """property [2]: the description is a focus statement about perception and attention."""
        d = axis_key_to_value_map("scope").get("percept", "")
        self.assertTrue(d.startswith("The response focuses on"), "property [2]: must begin 'The response focuses on'")
        self.assertIn("attention", d, "property [2]: must name attention")

    def test_percept_has_label_kanji_routing(self):
        """property [3]: percept has a scope label, kanji and routing concept."""
        for name, m in (
            ("label", axis_key_to_label_map("scope")),
            ("kanji", axis_key_to_kanji_map("scope")),
            ("routing", axis_key_to_routing_concept_map("scope")),
        ):
            with self.subTest(record=name):
                self.assertTrue(m.get("percept", ""), f"property [3]: percept has no scope {name}")

    def test_percept_distinctions_and_heuristics(self):
        """property [4]: distinctions cover visual, view, afford, struct, good; heuristics exist."""
        meta = axis_token_metadata().get("scope", {}).get("percept", {})
        named = {d["token"] for d in meta.get("distinctions", [])}
        for t in ("visual", "view", "afford", "struct", "good"):
            with self.subTest(token=t):
                self.assertIn(t, named, f"property [4]: no distinction against {t}")
        self.assertTrue(meta.get("heuristics"), "property [4]: no heuristics")

    def test_generated_grammar_lists_percept_under_scope(self):
        """property [6]: the generated grammar agrees."""
        grammar = _export._prompt_grammar_module().prompt_grammar_payload()
        self.assertIn("percept", _list_tokens(grammar, "scope"), "property [6]: payload scope lacks percept")

    def test_committed_grammar_copies_list_percept_under_scope(self):
        """property [6]: every committed grammar copy agrees."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                self.assertIn("percept", _list_tokens(grammar, "scope"), f"property [6]: {rel} lacks percept")


if __name__ == "__main__":
    unittest.main()
