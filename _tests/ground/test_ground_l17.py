"""Test for L17: multiple criteria under a single thread is a protocol violation.

The escape route: a model uses one [T: gap-name] for all behavioral predicates,
declares one thread, then writes multiple criteria under that thread — bypassing
the one-criterion-per-thread constraint.

L17 closes this: after the first criterion is written for the current thread,
the only valid next token is the formal notation rung label.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL17OneCriterionGate(unittest.TestCase):
    """L17: second criterion for same thread is a protocol violation."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l17_second_criterion_is_protocol_violation(self):
        """After the first criterion, the only valid next token is formal notation label."""
        self.assertIn(
            "second criterion for the same thread",
            self.core,
            "L17: a second criterion for the same thread must be named a protocol violation",
        )

    def test_l17_gate_requires_split_at_prose(self):
        """When multiple criteria exist, the thread must be split at prose, not criteria."""
        idx = self.core.find("second criterion for the same thread")
        self.assertGreater(idx, -1, "L17 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "split",
            segment,
            "L17: gate must require splitting the thread at the prose rung, not at criteria",
        )

    def test_l17_positioned_in_criteria_section(self):
        """L17 gate must appear in the criteria rung section."""
        criteria_idx = self.core.index("one independently testable behavior derived from the prose alone")
        gate_idx = self.core.find("second criterion for the same thread")
        self.assertGreater(gate_idx, criteria_idx,
            "L17: second-criterion gate must appear in the criteria section")


if __name__ == "__main__":
    unittest.main()
