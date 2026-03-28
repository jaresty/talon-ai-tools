"""Test for L13: Thread N+1 all-rung sequential gate.

The parallel-thread escape route: P3 gates only criteria for Thread N+1;
all other rungs (formal notation, EV, VRO, EI, OBR) of Thread N+1 are
ungated. A model satisfies the criteria gate, then runs all threads'
remaining rungs in parallel via the "advance continuously" instruction.

L13 closes this by extending P3's sequential constraint from criteria-scoped
to thread-scoped: no rung artifact of any type for Thread N+1 may appear
until Thread N complete is emitted.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL13ThreadSequentialGate(unittest.TestCase):
    """L13: Thread N+1 all-rung gate — sequential constraint covers all rungs."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l13_all_rung_gate_present(self):
        """The gate must state that no rung content of any type for Thread N+1
        may appear before Thread N complete — not just criteria."""
        has_gate = (
            "all seven rungs must complete for Thread N before any rung content for Thread N+1 may appear"
            in self.core
            or "all seven rungs for Thread N must complete before any content for Thread N+1 may appear"
            in self.core
        )
        self.assertTrue(has_gate, "L13: P3 must gate all rung types for Thread N+1, not only criteria")

    def test_l13_gate_references_thread_n_complete(self):
        """The gate must name Thread N complete as the condition that opens Thread N+1."""
        idx = self.core.find("all seven rungs")
        self.assertGreater(idx, -1, "L13 gate sentence must be present")
        segment = self.core[idx:idx+200]
        self.assertIn(
            "Thread N+1",
            segment,
            "L13: all-rung gate must reference Thread N+1 as the blocked party",
        )

    def test_l13_gate_positioned_in_p3(self):
        """The gate must appear in the P3 scope discipline section."""
        p3_idx = self.core.index("P3 (Scope discipline)")
        gate_idx = self.core.find("all seven rungs")
        self.assertGreater(gate_idx, p3_idx,
            "L13: all-rung gate must appear after the P3 label")
        # Must appear before the rung table
        rung_table_idx = self.core.index("Rung table")
        self.assertLess(gate_idx, rung_table_idx,
            "L13: all-rung gate must appear within P3, before the rung table")


if __name__ == "__main__":
    unittest.main()
