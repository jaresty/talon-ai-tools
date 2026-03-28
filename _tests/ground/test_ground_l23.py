"""Test for L23: after HARD STOP with a new criterion, EV and VRO must fire before impl_gate.

The escape route: the L18 fix states "after criterion re-statement, impl_gate
is the next valid token." After a HARD STOP that introduces a new criterion,
the model reads this as permission to skip EV and VRO entirely and jump
directly to impl_gate — the criterion has never had a red run.

L23 closes this by scoping L18: the shortcut applies only when a red VRO
already exists in the current cycle for the current criterion. When HARD STOP
introduces a new criterion, EV and VRO must fire before impl_gate.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL23HardStopEVVROGate(unittest.TestCase):
    """L23: after HARD STOP with new criterion, EV and VRO must fire before impl_gate."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l23_l18_scoped_to_existing_red_vro(self):
        """The impl_gate shortcut applies only when a red VRO exists for the current criterion."""
        self.assertIn(
            "only when a red VRO already exists",
            self.core,
            "L23: L18 shortcut must be scoped to cases where a red VRO exists for the current criterion",
        )

    def test_l23_hard_stop_new_criterion_requires_ev_vro(self):
        """When HARD STOP introduces a new criterion, EV and VRO must fire before impl_gate."""
        self.assertIn(
            "new criterion introduced by HARD STOP",
            self.core,
            "L23: must state that a new criterion from HARD STOP requires EV and VRO before impl_gate",
        )

    def test_l23_skipping_ev_vro_after_hard_stop_is_violation(self):
        """Skipping EV and VRO after HARD STOP with new criterion is a protocol violation."""
        idx = self.core.find("new criterion introduced by HARD STOP")
        self.assertGreater(idx, -1, "L23 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "protocol violation",
            segment,
            "L23: skipping EV and VRO after HARD STOP with new criterion must be a protocol violation",
        )

    def test_l23_positioned_near_l18_gate(self):
        """L23 must appear near the L18 gate sentence."""
        l18_idx = self.core.index("re-running VRO without an implementation edit is a protocol violation")
        gate_idx = self.core.find("new criterion introduced by HARD STOP")
        self.assertGreater(gate_idx, -1, "L23 gate sentence must be present")
        self.assertLess(abs(gate_idx - l18_idx), 600,
            "L23: scoping gate must appear near the L18 gate")


if __name__ == "__main__":
    unittest.main()
