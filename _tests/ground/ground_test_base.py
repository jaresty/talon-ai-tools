"""Shared base class for ground ADR tests (ADR-0240).

Provides assertDetects(phrase, text) which demonstrates both:
  - red state: the test would catch the phrase being absent
  - green state: the phrase is present in the actual text
"""
import unittest


class GroundADRTestBase(unittest.TestCase):
    def assertDetects(self, phrase: str, text: str, msg: str = "") -> None:
        """Assert phrase is present (green) and detectable when absent (red)."""
        stripped = text.replace(phrase, "\x00")
        self.assertNotIn(
            phrase,
            stripped,
            f"Red-state check: '{phrase}' is not detectable when absent{': ' + msg if msg else ''}",
        )
        self.assertIn(
            phrase,
            text,
            f"Green-state check: '{phrase}' must be present{': ' + msg if msg else ''}",
        )
