"""Tests for ADR-0227: impl_gate requires assertion-level failure text in verbatim exec_observed.

T1 impl-gate-assertion-level: impl_gate gate condition requires assertion-level failure strings
   in verbatim exec_observed output; infrastructure failure and model-described summaries excluded.
"""
import unittest

from lib.groundPrompt import _SENTINEL_GATES, build_ground_prompt


class TestThread1_ImplGateAssertionLevel(unittest.TestCase):
    """impl_gate gate requires assertion-level failure strings in verbatim output."""

    def setUp(self):
        self.gate = _SENTINEL_GATES["impl_gate"]
        self.prompt = build_ground_prompt()

    def test_assertion_level_failure_required(self):
        self.assertIn("assertion-level failure", self.gate)

    def test_example_assertion_strings_cited(self):
        self.assertIn("AssertionError", self.gate)

    def test_infrastructure_failure_excluded(self):
        self.assertIn("infrastructure failure", self.gate)

    def test_import_error_excluded(self):
        self.assertIn("import error", self.gate)

    def test_model_described_summary_excluded(self):
        self.assertIn("model-described summary", self.gate)

    def test_gate_propagated_to_prompt(self):
        self.assertIn("assertion-level failure", self.prompt)

    def test_infrastructure_cycle_constraint(self):
        self.assertIn(
            "this gate cannot be emitted until a subsequent cycle produces assertion-level failure output",
            self.gate,
        )


if __name__ == "__main__":
    unittest.main()
