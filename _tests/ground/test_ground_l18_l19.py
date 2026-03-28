"""Tests for L18–L19 ground protocol escape-route closures.

L18: After a red VRO (non-harness-error), re-writing FN/EV or re-running VRO
     without an intervening implementation edit is a protocol violation.
     After criterion re-statement, impl_gate is the next valid token.

L19: OBR voids_if must explicitly name test runner output as a void condition.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL, RUNG_SEQUENCE


class TestL18HardStopLoop(unittest.TestCase):
    """L18: After red VRO, re-running descent without implementation edit is blocked."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l18_rerun_vro_without_edit_is_violation(self):
        """Re-running VRO without an implementation edit after red VRO is a protocol violation."""
        self.assertIn(
            "re-running VRO without an implementation edit",
            self.core,
            "L18: re-running VRO without an implementation edit must be named a protocol violation",
        )

    def test_l18_impl_gate_is_next_valid_token(self):
        """After criterion re-statement following red VRO, impl_gate is the next valid token."""
        idx = self.core.find("re-running VRO without an implementation edit")
        self.assertGreater(idx, -1, "L18 gate sentence must be present")
        segment = self.core[idx:idx+400]
        self.assertIn(
            "Implementation gate cleared",
            segment,
            "L18: gate must state impl_gate is the next valid token after criterion re-statement",
        )

    def test_l18_positioned_near_vro_section(self):
        """L18 gate must appear near the VRO section."""
        vro_idx = self.core.index("At the validation run observation rung")
        gate_idx = self.core.find("re-running VRO without an implementation edit")
        self.assertGreater(gate_idx, vro_idx,
            "L18: gate must appear after the VRO section label")
        self.assertLess(gate_idx, vro_idx + 1200,
            "L18: gate must appear within the VRO section")


class TestL19OBRTestRunnerVoid(unittest.TestCase):
    """L19: OBR rung table voids_if must name test runner output as a void condition."""

    def setUp(self):
        self.obr = next(r for r in RUNG_SEQUENCE if r["name"] == "observed running behavior")

    def test_l19_test_runner_output_voids_obr(self):
        """OBR voids_if must explicitly state that test runner output voids the rung."""
        self.assertIn(
            "test runner",
            self.obr["voids_if"],
            "L19: OBR voids_if must name test runner output as a void condition",
        )

    def test_l19_voids_if_references_vro_type(self):
        """ADR-0188 Fix 1: OBR voids_if scoped — test runner as live-process evidence voids;
        step-5 run exempt. Type distinction now expressed via scoped void condition."""
        self.assertIn(
            "test runner output used as OBR live-process evidence voids this rung",
            self.obr["voids_if"],
            "L19: OBR voids_if must state that test runner output used as live-process evidence voids the rung",
        )


if __name__ == "__main__":
    unittest.main()
