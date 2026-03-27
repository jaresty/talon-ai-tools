"""Tests for L14–L15 ground protocol escape-route closures.

L14: Green VRO exec_observed may not produce a Gap — a passing test run
     has no failing assertion; emitting Gap after green is a protocol violation.

L15: Manifest declared header count N must equal the count of listed threads.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL14GreenVROGapBlocked(unittest.TestCase):
    """L14: Gap may not be emitted after a green (passing) exec_observed at VRO."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l14_green_exec_observed_may_not_produce_gap(self):
        """VRO must state that a green exec_observed may not produce a Gap."""
        self.assertIn(
            "green exec_observed",
            self.core,
            "L14: VRO must explicitly state a green exec_observed may not produce a Gap sentinel",
        )

    def test_l14_gap_requires_failing_assertion(self):
        """Gap at VRO must be derived from a failing assertion in the output."""
        self.assertIn(
            "failing assertion",
            self.core,
            "L14: Gap must cite a failing assertion from the exec_observed output — "
            "a conceptual gap not derived from a failing test is a protocol violation",
        )

    def test_l14_positioned_in_vro_section(self):
        """L14 gate must appear in the VRO rung section."""
        vro_idx = self.core.index("At the validation run observation rung")
        gate_idx = self.core.find("green exec_observed")
        self.assertGreater(gate_idx, vro_idx,
            "L14: green exec_observed gate must appear in the VRO section")


class TestL15ManifestCountVerified(unittest.TestCase):
    """L15: Manifest declared header N must equal the count of listed threads."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l15_manifest_count_must_equal_list_length(self):
        """Before emitting Manifest declared, the N in the header must equal the thread count."""
        self.assertIn(
            "count the thread entries",
            self.core,
            "L15: before emitting Manifest declared, the N in the header must be "
            "verified to equal the count of listed threads",
        )

    def test_l15_positioned_near_manifest_declaration(self):
        """L15 gate must appear near the Manifest declared instruction."""
        manifest_idx = self.core.index("Before emitting \u2705 Manifest declared, scan every sentence")
        gate_idx = self.core.find("count the thread entries")
        self.assertGreater(gate_idx, -1, "L15 gate sentence must be present")
        self.assertLess(abs(gate_idx - manifest_idx), 600,
            "L15: thread count verification must appear near the Manifest declared instruction")


if __name__ == "__main__":
    unittest.main()
