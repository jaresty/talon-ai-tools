"""Tests for ADR-0233: closing_observation gate requires direct invocation of intended behavior.

T1 closing-observation-positive-gate: gate requires the tool call to directly invoke
   the behavior named in session intent and produce output showing it is present.
"""
import unittest

from lib.groundPrompt import _SENTINEL_GATES, build_ground_prompt


class TestThread1_ClosingObservationPositiveGate(unittest.TestCase):
    """closing_observation gate states positively what the tool call must be."""

    def setUp(self):
        self.gate = _SENTINEL_GATES.get("closing_observation", "")
        self.prompt = build_ground_prompt()

    def test_gate_requires_direct_invocation_of_intent(self):
        self.assertIn("directly invoke the behavior named in the session intent", self.gate)

    def test_gate_requires_output_shows_behavior_present(self):
        self.assertIn("output must show that behavior is present", self.gate)

    def test_propagated_to_prompt(self):
        self.assertIn("directly invoke the behavior named in the session intent", self.prompt)


if __name__ == "__main__":
    unittest.main()
