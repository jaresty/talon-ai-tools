"""Test for L25: EV artifact content must be visible before Validation artifact V complete sentinel.

The escape route: the model emits ✅ Validation artifact V complete with no test
code visible in the transcript — the artifact may be written by a tool call whose
output is not captured, or may not be written at all.

L25 closes this: the artifact content must appear in the current response before
the sentinel; emitting the sentinel without quoting the artifact output is a
protocol violation.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL25EVArtifactVisible(unittest.TestCase):
    """L25: EV artifact content must appear in transcript before V-complete sentinel."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l25_artifact_content_must_appear(self):
        """Gate must state that artifact content must appear in the current response."""
        self.assertIn(
            "artifact content must appear in the current response",
            self.core,
            "L25: must state that artifact content must appear before V-complete sentinel",
        )

    def test_l25_sentinel_blocked_without_artifact(self):
        """Gate must state the sentinel is blocked if artifact is not quoted."""
        idx = self.core.find("artifact content must appear in the current response")
        self.assertGreater(idx, -1, "L25 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "protocol violation",
            segment,
            "L25: emitting sentinel without artifact content must be named a protocol violation",
        )

    def test_l25_positioned_near_ev_sentinel(self):
        """L25 gate must appear near the V-complete sentinel sentence."""
        sentinel_idx = self.core.find("Validation artifact V complete")
        gate_idx = self.core.find("artifact content must appear in the current response")
        self.assertGreater(gate_idx, -1, "L25 gate sentence must be present")
        self.assertLess(
            abs(gate_idx - sentinel_idx), 800,
            "L25: artifact-visible gate must appear near the V-complete sentinel",
        )


if __name__ == "__main__":
    unittest.main()
