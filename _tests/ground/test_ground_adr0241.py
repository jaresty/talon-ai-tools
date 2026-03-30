"""Tests for ADR-0241: transcript must show red+green evidence per assertion.

T1 red-green-transcript-evidence: the protocol requires that every assertion
   in the validation artifact appears in the transcript in both a failing
   state (red) and a passing state (green); impl_gate exec_observed must show
   every assertion failing; thread_complete exec_observed must show every
   assertion passing.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, _SENTINEL_GATES, build_ground_prompt


class TestThread1_RedGreenTranscriptEvidence(unittest.TestCase):
    """Protocol requires both red and green transcript evidence per assertion."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]
        self.impl_gate = _SENTINEL_GATES["impl_gate"]
        self.thread_complete = _SENTINEL_GATES["thread_complete"]

    def test_p5_requires_green_evidence(self):
        self.assertIn(
            "green-state evidence",
            self.core,
        )

    def test_impl_gate_requires_every_assertion_failing(self):
        self.assertIn(
            "every assertion in the validation artifact must appear failing",
            self.impl_gate,
        )

    def test_thread_complete_requires_every_assertion_passing(self):
        self.assertIn(
            "every assertion in the validation artifact must appear passing",
            self.thread_complete,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "green-state evidence",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
