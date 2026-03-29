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

    def test_l24_criteria_label_per_thread_prose_absent(self):
        # ADR-0215: batch-collect paragraph removed (thread sequencing in axiom block covers it)
        self.assertNotIn(
            "criteria rung label is per-thread",
            self.core,
            "ADR-0215: per-thread criteria rung label prose must be absent",
        )

    def test_l24_batch_criteria_prose_absent(self):
        # ADR-0215: batch-collect rule removed (derivable from axiom block)
        self.assertNotIn(
            "batch-collecting criteria for multiple threads under one criteria label",
            self.core,
            "ADR-0215: batch-collect criteria prose must be absent",
        )

    def test_l24_thread_sequencing_still_in_axiom_block(self):
        """Thread sequencing policy remains in axiom block (where L24 prose was derivable from)."""
        self.assertTrue(
            "all seven rungs for Thread N must complete before any content for Thread N+1 may appear" in self.core
            or "all seven rungs must complete for Thread N before any rung content for Thread N+1 may appear" in self.core,
            "Thread sequencing policy must remain in axiom block",
        )


if __name__ == "__main__":
    unittest.main()
