"""Tests for ADR-0232: closing_observation sentinel gates Ground complete.

T1 closing-observation-sentinel: sentinel exists with tool-call gate; ground_complete
   gate requires closing_observation to appear in the current response before it.
"""
import unittest

from lib.groundPrompt import SENTINEL_TEMPLATES, _SENTINEL_GATES, build_ground_prompt


class TestThread1_ClosingObservationSentinel(unittest.TestCase):
    """closing_observation sentinel present with correct gate."""

    def setUp(self):
        self.prompt = build_ground_prompt()
        self.gate = _SENTINEL_GATES.get("closing_observation", "")
        self.ground_complete_gate = _SENTINEL_GATES.get("ground_complete", "")

    def test_sentinel_template_exists(self):
        self.assertIn("closing_observation", SENTINEL_TEMPLATES)

    def test_sentinel_format(self):
        self.assertIn("Closing observation", SENTINEL_TEMPLATES["closing_observation"])

    def test_gate_requires_tool_call_before(self):
        self.assertIn("directly invoke the behavior named in the session intent", self.gate)

    def test_gate_requires_after_manifest_exhausted(self):
        self.assertIn("Manifest exhausted", self.gate)

    def test_gate_requires_before_ground_complete(self):
        self.assertIn("Ground complete", self.gate)

    def test_ground_complete_gate_requires_closing_observation(self):
        self.assertIn("Closing observation", self.ground_complete_gate)

    def test_propagated_to_prompt(self):
        self.assertIn("Closing observation", self.prompt)


if __name__ == "__main__":
    unittest.main()
