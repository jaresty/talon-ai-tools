"""Falsifiable tests for the storyboard form token (ADR-0155 pattern).

Each test must FAIL before the corresponding entry is added to axisConfig.py
and PASS after. Tests cover all five required dicts for a form token.
"""

import unittest

from lib.axisConfig import (
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_VALUE,
    axis_token_metadata,
)

_AXIS_TOKEN_METADATA = axis_token_metadata()


class StoryboardFormTokenTests(unittest.TestCase):
    """Storyboard is present and correctly structured in all five form dicts."""

    def test_storyboard_in_axis_key_to_value(self):
        """storyboard must appear in AXIS_KEY_TO_VALUE['form']."""
        self.assertIn("storyboard", AXIS_KEY_TO_VALUE["form"])

    def test_storyboard_in_axis_key_to_label(self):
        """storyboard must appear in AXIS_KEY_TO_LABEL['form']."""
        self.assertIn("storyboard", AXIS_KEY_TO_LABEL["form"])

    def test_storyboard_in_axis_key_to_kanji(self):
        """storyboard must appear in AXIS_KEY_TO_KANJI['form']."""
        self.assertIn("storyboard", AXIS_KEY_TO_KANJI["form"])

    def test_storyboard_in_axis_key_to_routing_concept(self):
        """storyboard must appear in AXIS_KEY_TO_ROUTING_CONCEPT['form']."""
        self.assertIn("storyboard", AXIS_KEY_TO_ROUTING_CONCEPT["form"])

    def test_storyboard_in_axis_token_metadata(self):
        """storyboard must appear in AXIS_TOKEN_METADATA['form'] with definition, heuristics, distinctions."""
        form_meta = _AXIS_TOKEN_METADATA.get("form", {})
        self.assertIn("storyboard", form_meta)
        entry = form_meta["storyboard"]
        self.assertTrue(entry.get("definition"))
        self.assertTrue(entry.get("heuristics"))
        self.assertTrue(entry.get("distinctions"))
