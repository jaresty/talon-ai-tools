"""Tests for ADR-0228: write_authorized sentinel — every file write must be preceded by
🔵 Write authorized citing the open rung, artifact type, and file path.

T1 write-authorized-sentinel: sentinel template and gate exist and propagate to prompt.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import SENTINEL_TEMPLATES, _SENTINEL_GATES, build_ground_prompt


class TestThread1_WriteAuthorizedSentinel(GroundADRTestBase):
    """write_authorized sentinel template, gate, and P20 present in prompt."""

    def setUp(self):
        self.prompt = build_ground_prompt()
        self.gate = _SENTINEL_GATES.get("write_authorized", "")

    def test_sentinel_template_exists(self):
        self.assertIn("write_authorized", SENTINEL_TEMPLATES)

    def test_sentinel_format_contains_rung(self):
        self.assertIn("rung:", SENTINEL_TEMPLATES["write_authorized"])

    def test_sentinel_format_contains_artifact_type(self):
        self.assertIn("artifact type:", SENTINEL_TEMPLATES["write_authorized"])

    def test_sentinel_format_contains_file(self):
        self.assertIn("file:", SENTINEL_TEMPLATES["write_authorized"])

    def test_gate_exists(self):
        self.assertNotEqual(self.gate, "", "write_authorized must have a gate in _SENTINEL_GATES")

    def test_gate_requires_open_rung(self):
        self.assertIn("open rung", self.gate)

    def test_gate_requires_permitted_tool_calls_match(self):
        self.assertIn("permitted-tool-calls", self.gate)

    def test_gate_voids_write_without_sentinel(self):
        self.assertIn("voids", self.gate)

    def test_p20_in_prompt(self):
        self.assertIn("P18 (Write authorization)", self.prompt)

    def test_p20_requires_write_authorized_before_file_write(self):
        self.assertDetects("Every file write immediately preceded by", self.prompt)

    def test_write_authorized_propagated_to_prompt(self):
        self.assertDetects("Write authorized", self.prompt)


if __name__ == "__main__":
    unittest.main()
