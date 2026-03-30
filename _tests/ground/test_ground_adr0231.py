"""Tests for ADR-0231: P21 observation-loop return clause.

T1 p21-observation-loop-return: returning to the session observation loop is valid
   when a tool-executed observation reveals the declared gap is incorrect;
   trigger must be observation evidence; entire ladder is voided on return.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_P21ObservationLoopReturn(unittest.TestCase):
    """P21 observation-loop return clause present and correct."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_observation_loop_return_permitted(self):
        self.assertIn("Returning to the session observation loop is valid", self.core)

    def test_trigger_must_be_tool_executed_observation(self):
        self.assertIn("tool-executed observation reveals the declared gap is incorrect", self.core)

    def test_lower_rung_pressure_excluded_as_trigger(self):
        self.assertIn("difficulty, failure, or constraint pressure from any lower rung is not a valid trigger", self.core)

    def test_ladder_voided_on_return(self):
        self.assertIn("entire current ladder is void", self.core)

    def test_new_observation_required_before_new_gap(self):
        self.assertIn("new observation must be made before any new gap may be declared", self.core)

    def test_propagated_to_prompt(self):
        self.assertIn("Returning to the session observation loop is valid", build_ground_prompt())


if __name__ == "__main__":
    unittest.main()
