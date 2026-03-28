"""Tests for ADR-0185 Phase 1: precision clauses added to P1, P3, A3, R2."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestPrecisionClauses(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_p1_intra_cycle_cross_rung_clause(self):
        """P1 must state that cross-rung output within the same cycle does not satisfy a gate."""
        self.assertIn(
            "cross-rung output within the same cycle",
            self.prompt,
            "P1 must include intra-cycle cross-rung type discipline clause",
        )

    def test_p3_sentinel_singleton_clause(self):
        """P3 must state that each sentinel is valid exactly once at its defining rung per invocation."""
        self.assertIn(
            "exactly once at its defining rung per invocation",
            self.prompt,
            "P3 must include sentinel-singleton clause",
        )

    def test_a3_evidential_context_reset_clause(self):
        """A3 must state that evidential context resets at every re-emission of the prose rung label."""
        self.assertIn(
            "evidential context resets at every re-emission of the prose rung label",
            self.prompt,
            "A3 must include prose-rung-label reset clause",
        )

    def test_r2_void_propagation_clause(self):
        """R2 must state that if the prior rung's artifact is absent or void, no artifact below it is valid."""
        self.assertIn(
            "absent or void",
            self.prompt,
            "R2 must include void-propagation clause",
        )


if __name__ == "__main__":
    unittest.main()
