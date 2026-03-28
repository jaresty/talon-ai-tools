"""Test for L16: prose with no [T: gap-name] markers may not advance to Manifest declared.

The escape route: a model writes prose with multiple behavioral predicates
but zero [T: gap-name] markers, then emits a one-thread manifest — bypassing
the thread-count discipline entirely.

L16 closes this by requiring that if the prose contains no [T: gap-name]
markers, Manifest declared is blocked and the prose must be re-emitted
with markers before proceeding.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL16TMarkerGate(unittest.TestCase):
    """L16: Manifest declared is blocked if prose contains no [T: gap-name] markers."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l16_t_marker_absence_blocks_manifest(self):
        """Manifest declared may not be emitted if prose contains no [T: gap-name] markers."""
        self.assertIn(
            "no [T: gap-name] markers",
            self.core,
            "L16: if the prose contains no [T: gap-name] markers, "
            "Manifest declared must be blocked",
        )

    def test_l16_gate_requires_prose_reemission(self):
        """When no markers are present, the prose must be re-emitted with markers."""
        idx = self.core.find("no [T: gap-name] markers")
        self.assertGreater(idx, -1, "L16 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "re-emit",
            segment,
            "L16: gate must require re-emitting prose with markers when none are present",
        )

    def test_l16_positioned_near_manifest_declaration(self):
        """L16 gate must appear near the Manifest declared instruction."""
        manifest_idx = self.core.index("Before emitting \u2705 Manifest declared, scan every sentence")
        gate_idx = self.core.find("no [T: gap-name] markers")
        self.assertGreater(gate_idx, -1, "L16 gate sentence must be present")
        self.assertLess(abs(gate_idx - manifest_idx), 800,
            "L16: marker-absence gate must appear near the Manifest declared instruction")


if __name__ == "__main__":
    unittest.main()
