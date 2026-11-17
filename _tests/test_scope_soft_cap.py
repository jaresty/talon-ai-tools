"""Guard: the scope soft cap is 3, in the grammar and in the axis description."""

import json
import unittest
from pathlib import Path

import prompts.export as _export
from lib.axisConfig import AXIS_KEY_TO_AXIS_DESC

_REPO = Path(__file__).resolve().parent.parent
_GRAMMAR_COPIES = (
    "build/prompt-grammar.json",
    "internal/barcli/embed/prompt-grammar.json",
    "cmd/bar/testdata/grammar.json",
    "web/static/prompt-grammar.json",
)


class ScopeSoftCapTests(unittest.TestCase):
    def test_generated_grammar_scope_cap_is_three(self):
        """property [1]: the freshly generated grammar caps scope at 3."""
        grammar = _export._prompt_grammar_module().prompt_grammar_payload()
        cap = grammar.get("hierarchy", {}).get("axis_soft_caps", {}).get("scope")
        self.assertEqual(cap, 3, "property [1]: payload scope cap must be 3")

    def test_committed_grammar_copies_scope_cap_is_three(self):
        """property [1]: every committed grammar copy caps scope at 3."""
        for rel in _GRAMMAR_COPIES:
            with self.subTest(copy=rel):
                grammar = json.loads((_REPO / rel).read_text(encoding="utf-8"))
                cap = grammar.get("hierarchy", {}).get("axis_soft_caps", {}).get("scope")
                self.assertEqual(cap, 3, f"property [1]: {rel} scope cap must be 3")

    def test_scope_axis_description_states_three(self):
        """property [3]: the scope axis description states the cap as three."""
        desc = AXIS_KEY_TO_AXIS_DESC.get("scope", "")
        self.assertIn("Up to three.", desc, "property [3]: scope description must say 'Up to three.'")
        self.assertNotIn("Up to two.", desc, "property [3]: scope description must not say 'Up to two.'")


if __name__ == "__main__":
    unittest.main()
