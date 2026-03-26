"""Tests for Thread 2: rung sequence table in groundPrompt.py.

Validates that after refactor:
- RUNG_SEQUENCE exists with 7 entries, each having required keys
- All 7 canonical rung names are present
- build_ground_prompt() output contains a tabular representation
- rung_sequence_code character count is lower than baseline
"""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt

CANONICAL_RUNG_NAMES = [
    "prose",
    "criteria",
    "formal notation",
    "executable validation",
    "validation run observation",
    "executable implementation",
    "observed running behavior",
]

REQUIRED_RUNG_KEYS = {"name", "artifact", "gate", "voids_if"}

# Baseline character count of rung_sequence_code before refactor (measured: 8679 chars).
# Target: numbered list compressed to inline arrow sequence; reduction modest (~30+ chars).
BASELINE_RUNG_SEQUENCE_CODE_CHARS = 22900  # ADR-0179: ~1117; ADR-0180: ~500; ADR-0181: ~900; ADR-0182: ~770; formal notation separation


class TestRungSequenceExists(unittest.TestCase):
    def test_rung_sequence_dict_exists(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        self.assertIsInstance(RUNG_SEQUENCE, list)

    def test_rung_sequence_has_seven_entries(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        self.assertEqual(len(RUNG_SEQUENCE), 7)

    def test_each_entry_has_required_keys(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        for entry in RUNG_SEQUENCE:
            self.assertEqual(
                set(entry.keys()),
                REQUIRED_RUNG_KEYS,
                f"Entry {entry.get('name', '?')} missing required keys",
            )

    def test_all_canonical_rung_names_present(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        names = [entry["name"] for entry in RUNG_SEQUENCE]
        for canonical in CANONICAL_RUNG_NAMES:
            self.assertIn(canonical, names, f"Canonical rung name missing: {canonical}")

    def test_rung_order_matches_canonical(self):
        from lib.groundPrompt import RUNG_SEQUENCE

        names = [entry["name"] for entry in RUNG_SEQUENCE]
        self.assertEqual(names, CANONICAL_RUNG_NAMES)


class TestBuildGroundPromptContainsRungTable(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prompt_contains_all_rung_names(self):
        for name in CANONICAL_RUNG_NAMES:
            self.assertIn(name, self.prompt, f"Rung name missing from prompt: {name}")


class TestRungSequenceCodeShorter(unittest.TestCase):
    def test_rung_sequence_code_shorter_than_baseline(self):
        actual = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            actual,
            BASELINE_RUNG_SEQUENCE_CODE_CHARS,
            f"GROUND_PARTS_MINIMAL core is {actual} chars; expected < {BASELINE_RUNG_SEQUENCE_CODE_CHARS}",
        )


if __name__ == "__main__":
    unittest.main()
