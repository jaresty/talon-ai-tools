"""Tests for ADR-0225: OBR bookends every cycle — each cycle opens and closes with observed running behavior.

The standard derivation previously showed OBR only at session start and end.
This ADR makes explicit that every descent cycle begins with OBR (observe current
state, declare gap) and ends with OBR (confirm gap closed). Thread complete is
only valid after closing OBR exec_observed demonstrates the criterion is met.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_OBRBookendsEveryCycle(unittest.TestCase):
    """Every descent cycle begins and ends with observed running behavior."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]
        self.prompt = build_ground_prompt()

    def test_each_cycle_begins_with_obr(self):
        self.assertIn(
            "cycle begins with an observed-running-behavior rung",
            self.core,
        )

    def test_gap_declared_from_obr_output(self):
        self.assertIn(
            "the gap for that cycle is declared from that observation\u2019s output",
            self.core,
        )

    def test_each_cycle_ends_with_obr(self):
        self.assertIn(
            "each cycle ends with an observed-running-behavior rung confirming the gap is closed",
            self.core,
        )

    def test_thread_complete_requires_closing_obr(self):
        self.assertIn(
            "exec_observed at the rung whose artifact type is observed running behavior directly demonstrating",
            self.prompt,
        )

    def test_no_observed_running_behavior_rung_name_in_gate(self):
        # thread_complete gate must not reference the rung by name
        self.assertNotIn(
            "valid only at the observed-running-behavior rung",
            self.prompt,
        )

    def test_thread_complete_uses_artifact_type_description(self):
        self.assertIn(
            "valid only at the rung whose artifact type is observed running behavior",
            self.prompt,
        )


class TestADR0225CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            17_500,
            f"ADR-0225: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
