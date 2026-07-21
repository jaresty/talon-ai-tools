"""Falsifiable tests for the canvas channel token (ADR-0155 pattern).

Each test must FAIL before the corresponding entry is added to axisConfig.py
and PASS after. Tests cover all five required dicts for a channel token.
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


class CanvasChannelTokenTests(unittest.TestCase):
    """canvas is present and correctly structured in all five channel dicts."""

    def test_canvas_in_axis_key_to_value(self):
        """canvas must appear in AXIS_KEY_TO_VALUE['channel']."""
        self.assertIn("canvas", AXIS_KEY_TO_VALUE["channel"])

    def test_canvas_in_axis_key_to_label(self):
        """canvas must appear in AXIS_KEY_TO_LABEL['channel']."""
        self.assertIn("canvas", AXIS_KEY_TO_LABEL["channel"])

    def test_canvas_in_axis_key_to_kanji(self):
        """canvas must appear in AXIS_KEY_TO_KANJI['channel']."""
        self.assertIn("canvas", AXIS_KEY_TO_KANJI["channel"])

    def test_canvas_in_axis_key_to_routing_concept(self):
        """canvas must appear in AXIS_KEY_TO_ROUTING_CONCEPT['channel']."""
        self.assertIn("canvas", AXIS_KEY_TO_ROUTING_CONCEPT["channel"])

    def test_canvas_in_axis_token_metadata(self):
        """canvas must appear in AXIS_TOKEN_METADATA['channel'] with definition, heuristics, distinctions."""
        channel_meta = _AXIS_TOKEN_METADATA.get("channel", {})
        self.assertIn("canvas", channel_meta)
        entry = channel_meta["canvas"]
        self.assertTrue(entry.get("definition"))
        self.assertTrue(entry.get("heuristics"))
        self.assertTrue(entry.get("distinctions"))

    def test_canvas_definition_names_canvas_rendering_agent(self):
        """canvas definition must name 'canvas rendering agent' as the addressee."""
        value = AXIS_KEY_TO_VALUE["channel"].get("canvas", "")
        self.assertIn("canvas rendering agent", value)

    def test_canvas_definition_requires_skill_invocation(self):
        """canvas definition must require agent to invoke the canvas rendering skill."""
        value = AXIS_KEY_TO_VALUE["channel"].get("canvas", "")
        self.assertIn("canvas rendering skill", value)

    def test_canvas_definition_names_shapes_and_connections(self):
        """canvas definition must describe output as shapes and connections."""
        value = AXIS_KEY_TO_VALUE["channel"].get("canvas", "")
        self.assertIn("shapes and connections", value)
