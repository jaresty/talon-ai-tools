"""Test for L22: [T: gap-name] markers may only appear in the prose rung.

The escape route: the model writes [T: gap-name] markers inside a criteria
artifact, formal notation, or other rung — re-doing thread discovery at the
wrong rung instead of writing a single falsifiable criterion.

L22 closes this: [T: gap-name] markers are valid only in the prose rung;
their presence in any other rung artifact is a protocol violation.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL22TMarkerProseOnly(unittest.TestCase):
    """L22: [T: gap-name] markers are valid only in the prose rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l22_t_markers_prose_rung_only(self):
        """[T: gap-name] markers are valid only in the prose rung."""
        self.assertIn(
            "[T: gap-name] markers are valid only in the prose rung",
            self.core,
            "L22: must explicitly state that [T: gap-name] markers are prose-rung-only",
        )

    def test_l22_markers_in_other_rungs_is_violation(self):
        """[T: gap-name] markers in any other rung artifact is a protocol violation."""
        idx = self.core.find("[T: gap-name] markers are valid only in the prose rung")
        self.assertGreater(idx, -1, "L22 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "protocol violation",
            segment,
            "L22: markers outside prose rung must be named a protocol violation",
        )

    def test_l22_positioned_near_t_marker_rule(self):
        """L22 gate must appear near the [T: gap-name] marker rule."""
        marker_rule_idx = self.core.index(
            "Each sentence in the prose containing a behavioral predicate"
        )
        gate_idx = self.core.find("[T: gap-name] markers are valid only in the prose rung")
        self.assertGreater(gate_idx, -1, "L22 gate sentence must be present")
        self.assertLess(abs(gate_idx - marker_rule_idx), 800,
            "L22: prose-only gate must appear near the [T: gap-name] marker rule")


if __name__ == "__main__":
    unittest.main()
