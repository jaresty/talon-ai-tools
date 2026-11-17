"""Guard: afford is a scope token (focus on the available-action space), not a method token."""

import json
import unittest
from pathlib import Path

import prompts.export as _export
from lib.axisConfig import (
    axis_key_to_category_map,
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


class AffordScopeTokenTests(unittest.TestCase):
    def test_afford_is_scope_and_only_scope(self):
        """property [1]: afford is a scope token and only a scope token."""
        self.assertIn("afford", axis_key_to_value_map("scope"), "property [1]: afford missing from scope")
        self.assertNotIn("afford", axis_key_to_value_map("method"), "property [1]: afford still in method")

    def test_afford_scope_description_focuses_on_actions(self):
        """property [2]: the scope description is a focus statement about available actions."""
        d = axis_key_to_value_map("scope").get("afford", "")
        self.assertTrue(
            d.startswith("The response focuses on"),
            "property [2]: afford scope description must begin 'The response focuses on'",
        )
        self.assertIn("action", d, "property [2]: afford scope description must name actions")

    def test_afford_scope_record_has_label_and_kanji(self):
        """property [3]: afford has a scope-axis label and kanji."""
        self.assertTrue(
            axis_key_to_label_map("scope").get("afford", ""),
            "property [3]: afford has no scope label",
        )
        self.assertTrue(
            axis_key_to_kanji_map("scope").get("afford", ""),
            "property [3]: afford has no scope kanji",
        )

    def test_afford_has_no_method_axis_records(self):
        """property [5]: afford has no method-axis record besides its description."""
        records = {
            "label": axis_key_to_label_map("method"),
            "kanji": axis_key_to_kanji_map("method"),
            "category": axis_key_to_category_map("method"),
            "routing": axis_key_to_routing_concept_map("method"),
            "metadata": axis_token_metadata().get("method", {}),
        }
        for name, record in records.items():
            with self.subTest(record=name):
                self.assertNotIn("afford", record, f"property [5]: stale method {name} entry for afford")

    def test_afford_scope_heuristics_include_carried_over_phrases(self):
        """property [7]: the scope heuristics for afford include the six chosen phrases."""
        heuristics = axis_token_metadata().get("scope", {}).get("afford", {}).get("heuristics", [])
        for phrase in (
            "why do users do X",
            "the design encourages Y",
            "affordances",
            "what the API makes easy",
            "design defaults bias toward",
            "interface suppresses this action",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, heuristics, f"property [7]: scope heuristics lack '{phrase}'")

    def test_afford_has_scope_routing_concept(self):
        """property [6]: afford has a scope routing concept."""
        self.assertTrue(
            axis_key_to_routing_concept_map("scope").get("afford", ""),
            "property [6]: afford has no scope routing concept",
        )

    def test_generated_grammar_lists_afford_under_scope_only(self):
        """property [4]: the freshly generated grammar agrees."""
        grammar = _export._prompt_grammar_module().prompt_grammar_payload()
        self.assertIn("afford", _list_tokens(grammar, "scope"), "property [4]: payload scope lacks afford")
        self.assertNotIn("afford", _list_tokens(grammar, "method"), "property [4]: payload method has afford")

    def test_committed_grammar_copies_list_afford_under_scope_only(self):
        """property [4]: every committed grammar copy agrees."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                self.assertIn("afford", _list_tokens(grammar, "scope"), f"property [4]: {rel} scope lacks afford")
                self.assertNotIn("afford", _list_tokens(grammar, "method"), f"property [4]: {rel} method has afford")


if __name__ == "__main__":
    unittest.main()
