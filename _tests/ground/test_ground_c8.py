"""Test for C8: static-state artifact vacuousness check."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC8StaticStateVacuousness(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c8_static_state_mentioned(self):
        self.assertIn("static", self.core,
            "C8: ground must mention static-state artifacts in the vacuousness check")

    def test_c8_pre_edit_run_required(self):
        self.assertIn("before any edit", self.core,
            "C8: ground must require running static-state artifacts against the pre-edit codebase")

    def test_c8_positioned_within_vacuousness_clause(self):
        # ADR-0181: "Only validation artifacts may be produced" removed (attractor 1 subsumed by gate).
        # EV rung now opens with "each test function asserts exactly one behavioral property".
        ev_idx = self.core.index("each test function asserts exactly one behavioral property")
        v_complete_idx = self.core.index("\u2705 Validation artifact V complete must be emitted")
        static_idx = self.core.index("static", ev_idx)
        self.assertLess(static_idx, v_complete_idx,
            "C8: static-state check must appear within the EV rung section, before V-complete sentinel")

    def test_c8_passing_before_edit_is_vacuous(self):
        static_idx = self.core.index("static")
        v_complete_idx = self.core.index("\u2705 Validation artifact V complete must be emitted")
        segment = self.core[static_idx:v_complete_idx]
        self.assertIn("vacuous", segment,
            "C8: ground must state that a static-state artifact passing before any edit is vacuous")


if __name__ == "__main__":
    unittest.main()
