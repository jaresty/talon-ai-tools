"""Tests for ADR-0234: observation loop is sole valid termination path for Ground complete.

T1 observation-loop-terminates-ground: Ground complete may only be emitted as the
   outcome of the observation loop; emitting it outside the loop is a protocol violation.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ObservationLoopTerminatesGround(unittest.TestCase):
    """Observation loop is the sole valid termination path for Ground complete."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_ground_complete_only_from_observation_loop(self):
        self.assertIn(
            "\u2705 Ground complete may only be emitted as the outcome of the observation loop",
            self.core,
        )

    def test_emitting_outside_loop_is_violation(self):
        self.assertIn(
            "emitting it outside the loop is a protocol violation",
            self.core,
        )

    def test_violation_regardless_of_closing_observation(self):
        self.assertIn(
            "regardless of whether \U0001f535 Closing observation is present",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "\u2705 Ground complete may only be emitted as the outcome of the observation loop",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
