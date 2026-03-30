"""Tests for ADR-0230: P21 upward-return principle.

T1 p21-upward-return: P21 permits upward returns triggered at or above the revised rung
   and prohibits upward returns triggered by lower-rung pressure.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_P21UpwardReturn(unittest.TestCase):
    """P21 upward-return principle present and correct."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_p21_exists(self):
        self.assertIn("P19 (Upward return)", self.core)

    def test_p21_permits_upward_return_on_derivation_error(self):
        self.assertIn("derivation error", self.core)

    def test_p21_trigger_must_originate_at_or_above(self):
        self.assertIn("trigger for an upward return must originate at the rung being revised or above", self.core)

    def test_p21_lower_rung_pressure_prohibited(self):
        self.assertIn("difficulty, failure, or constraint pressure from any lower rung is not a valid trigger", self.core)

    def test_p21_lower_rung_hard_to_produce_voids(self):
        self.assertIn("returning upward because a lower rung", self.core)

    def test_p21_revised_rung_re_derived_from_input(self):
        self.assertIn("re-derived from its input rung", self.core)

    def test_p21_descent_resumes_from_revised_rung(self):
        self.assertIn("descent resumes downward", self.core)

    def test_p21_propagated_to_prompt(self):
        self.assertIn("P19 (Upward return)", build_ground_prompt())


if __name__ == "__main__":
    unittest.main()
