"""Tests for Thread 2: ADR-0174 existence and structure."""

import unittest
from pathlib import Path

ADR_PATH = Path(__file__).parent.parent / "docs/adr/0174-ground-prompt-minimal-spec.md"

REQUIRED_SECTIONS = [
    "## Context",
    "## Decision",
    "## Consequences",
]

REQUIRED_TERMS = [
    "GROUND_PARTS_MINIMAL",
    "minimal=True",
    "overspecif",
]


class TestADR0174(unittest.TestCase):
    def setUp(self):
        self.text = ADR_PATH.read_text()

    def test_adr_file_exists(self):
        self.assertTrue(ADR_PATH.exists(), f"ADR file not found: {ADR_PATH}")

    def test_required_sections_present(self):
        for section in REQUIRED_SECTIONS:
            self.assertIn(section, self.text, f"Section missing: {section}")

    def test_required_terms_present(self):
        for term in REQUIRED_TERMS:
            self.assertIn(term, self.text, f"Required term missing: {term!r}")


if __name__ == "__main__":
    unittest.main()
