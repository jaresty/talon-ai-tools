"""Tests for ADR-0236: session observation loop defines valid observation.

T1 observation-definition: observing running behavior means direct invocation
   of the behavior named in intent; output produced by behavior itself;
   test suite runs excluded regardless of pass/fail.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ObservationDefinition(unittest.TestCase):
    """Session observation loop defines what qualifies as observing running behavior."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_observation_means_direct_invocation(self):
        self.assertIn(
            "Observing running behavior means invoking the system directly",
            self.core,
        )

    def test_output_produced_by_behavior_itself(self):
        self.assertIn(
            "output must be produced by the behavior itself",
            self.core,
        )

    def test_not_by_test_framework(self):
        self.assertIn(
            "not by a test framework asserting properties of it",
            self.core,
        )

    def test_test_suite_run_excluded(self):
        self.assertIn(
            "a test suite run does not satisfy this requirement",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "Observing running behavior means invoking the system directly",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
