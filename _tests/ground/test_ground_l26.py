"""Test for L26: Manifest exhausted may only fire when all declared threads are complete.

The escape route: the model emits ✅ Manifest exhausted — 2/10 threads complete
after only completing 2 of 10 declared threads, treating it as a progress marker
rather than a terminal sentinel.

L26 closes this: Manifest exhausted may not be emitted unless the count of
Thread N complete sentinels equals the N declared in Manifest declared.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL26ManifestExhaustedCount(unittest.TestCase):
    """L26: Manifest exhausted requires all declared threads to be complete."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l26_manifest_exhausted_requires_all_threads(self):
        """Gate must state Manifest exhausted may not be emitted until all threads complete."""
        self.assertIn(
            "Manifest exhausted may not be emitted unless",
            self.core,
            "L26: must gate Manifest exhausted on all declared threads being complete",
        )

    def test_l26_count_equality_check(self):
        """Gate must require count of Thread N complete equals declared N."""
        idx = self.core.find("Manifest exhausted may not be emitted unless")
        self.assertGreater(idx, -1, "L26 gate sentence must be present")
        segment = self.core[idx:idx+400]
        self.assertIn(
            "protocol violation",
            segment,
            "L26: emitting Manifest exhausted before all threads complete must be a protocol violation",
        )

    def test_l26_positioned_near_manifest_exhausted(self):
        """L26 gate must appear near the Manifest exhausted sentinel."""
        sentinel_idx = self.core.find("Manifest exhausted")
        gate_idx = self.core.find("Manifest exhausted may not be emitted unless")
        self.assertGreater(gate_idx, -1, "L26 gate sentence must be present")
        self.assertLess(
            abs(gate_idx - sentinel_idx), 600,
            "L26: count gate must appear near the Manifest exhausted sentinel",
        )


if __name__ == "__main__":
    unittest.main()
