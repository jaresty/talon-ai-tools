"""Tests for ADR-0219: sentinel inline gates + criteria-complete sentinel.

Thread 1: each sentinel in the sentinel block carries its gate condition inline.
Thread 2: criteria-complete sentinel exists with single-criterion gate.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt, SENTINEL_TEMPLATES


class TestThread1_SentinelInlineGates(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_exec_observed_gate_inline(self):
        self.assertIn(
            "tool call made in the current response immediately before this sentinel",
            self.prompt,
        )

    def test_manifest_declared_gate_inline(self):
        self.assertIn(
            "rung table precedes this sentinel",
            self.prompt,
        )

    def test_impl_gate_gate_inline(self):
        self.assertIn(
            "valid only at the EI rung",
            self.prompt,
        )

    def test_thread_complete_gate_inline(self):
        self.assertIn(
            "OBR exec_observed directly demonstrating criterion in current cycle",
            self.prompt,
        )

    def test_manifest_exhausted_gate_inline(self):
        self.assertIn(
            "count of Thread N complete sentinels equals N in Manifest declared",
            self.prompt,
        )

    def test_gap_gate_inline(self):
        self.assertIn(
            "gap text is a currently-false behavioral assertion",
            self.prompt,
        )

    def test_v_complete_gate_inline(self):
        self.assertIn(
            "test file written via tool call in current response",
            self.prompt,
        )

    def test_hard_stop_gate_inline(self):
        self.assertIn(
            "criterion identical to prior cycle criterion for this thread",
            self.prompt,
        )

    def test_r2_audit_gate_inline(self):
        self.assertIn(
            "every criterion encoded in notation; audit section named and separate",
            self.prompt,
        )


class TestThread2_CriteriaCompleteSentinel(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_criteria_complete_sentinel_in_templates(self):
        self.assertIn("criteria_complete", SENTINEL_TEMPLATES)

    def test_criteria_complete_format_string(self):
        self.assertIn("\u2705 Criteria complete", self.prompt)

    def test_criteria_complete_gate_single_criterion(self):
        self.assertIn(
            "exactly one criterion in this rung",
            self.prompt,
        )

    def test_criteria_complete_gate_no_conjunction(self):
        self.assertIn(
            "criterion contains no conjunction",
            self.prompt,
        )

    def test_formal_notation_blocked_until_criteria_complete(self):
        self.assertIn(
            "formal notation rung label may not be emitted until",
            self.prompt,
        )


if __name__ == "__main__":
    unittest.main()
