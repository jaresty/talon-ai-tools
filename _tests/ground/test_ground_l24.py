"""Test for L24: criteria rung label is per-thread; batch-collecting all thread
criteria under one label bypasses sequential descent.

The escape route: after Manifest declared, the model writes one 'criteria'
rung label and then lists criteria for all threads under it — treating criteria
as a collective planning phase. L17 says the formal notation label must follow
the first criterion, but the model writes Thread 2's criterion instead.

L24 closes this: the criteria rung label is per-thread; writing a criterion
for Thread N+1 before Thread N complete is emitted is a protocol violation
regardless of whether they share a criteria rung label.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL24CriteriaPerThread(unittest.TestCase):
    """L24: criteria rung is per-thread; batch criteria under one label is a violation."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l24_criteria_label_is_per_thread(self):
        """The criteria rung label is per-thread, not shared across all threads."""
        self.assertIn(
            "criteria rung label is per-thread",
            self.core,
            "L24: must state that the criteria rung label applies to one thread at a time",
        )

    def test_l24_batch_criteria_is_violation(self):
        """Writing criteria for multiple threads under one label is a protocol violation."""
        idx = self.core.find("criteria rung label is per-thread")
        self.assertGreater(idx, -1, "L24 gate sentence must be present")
        segment = self.core[idx:idx+400]
        self.assertIn(
            "protocol violation",
            segment,
            "L24: batch-collecting criteria for multiple threads must be named a protocol violation",
        )

    def test_l24_positioned_near_criteria_rules(self):
        """L24 gate must appear near the criteria rung rules."""
        criteria_idx = self.core.index("one independently testable behavior derived from the prose alone")
        gate_idx = self.core.find("criteria rung label is per-thread")
        self.assertGreater(gate_idx, -1, "L24 gate sentence must be present")
        self.assertLess(abs(gate_idx - criteria_idx), 1600,
            "L24: per-thread gate must appear near the criteria rung rules")


if __name__ == "__main__":
    unittest.main()
