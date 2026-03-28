"""Tests for L28 (closed-world manifest), L29 (Thread complete ordering), L30 (final report gate).

L28: only threads declared in Manifest declared may be addressed — creating an
undeclared thread is a protocol violation.

L29: Thread N complete may not be emitted before the OBR rung tool call and
Execution observed sentinel exist for Thread N in the current cycle.

L30: any final-report prose may not appear unless Manifest exhausted immediately
precedes it in the transcript.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL28ManifestClosedWorld(unittest.TestCase):
    """L28: only declared threads may be addressed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l28_undeclared_thread_is_violation(self):
        self.assertIn(
            "creating a thread not in the manifest is a protocol violation",
            self.core,
            "L28: must state that creating an undeclared thread is a protocol violation",
        )

    def test_l28_new_gap_handling(self):
        idx = self.core.find("creating a thread not in the manifest is a protocol violation")
        self.assertGreater(idx, -1, "L28 gate must be present")
        segment = self.core[idx:idx+400]
        self.assertIn(
            "return to prose",
            segment,
            "L28: must say to return to prose and revise the manifest rather than creating a new thread",
        )

    def test_l28_positioned_near_manifest(self):
        anchor_idx = self.core.find("Manifest declared may be emitted exactly once per invocation")
        gate_idx = self.core.find("creating a thread not in the manifest is a protocol violation")
        self.assertGreater(gate_idx, -1, "L28 gate must be present")
        self.assertLess(abs(gate_idx - anchor_idx), 300,
            "L28 gate must appear immediately after 'Manifest declared may be emitted exactly once'")


class TestL29ThreadCompleteOrdering(unittest.TestCase):
    """L29: Thread N complete must follow OBR Execution observed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l29_thread_complete_follows_obr(self):
        self.assertIn(
            "immediately follows",
            self.core,
            "L29: must state Thread N complete immediately follows Execution observed at OBR rung",
        )

    def test_l29_thread_complete_not_before_obr(self):
        idx = self.core.find("immediately follows")
        self.assertGreater(idx, -1, "L29 gate must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "not before",
            segment,
            "L29: must state Thread complete may not appear before OBR",
        )


class TestL30FinalReportGate(unittest.TestCase):
    """L30: final report may not appear before Manifest exhausted."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l30_final_report_requires_manifest_exhausted(self):
        self.assertIn(
            "final report may not appear unless",
            self.core,
            "L30: must gate final report on Manifest exhausted existing in transcript",
        )

    def test_l30_final_report_definition(self):
        idx = self.core.find("final report may not appear unless")
        self.assertGreater(idx, -1, "L30 gate must be present")
        segment = self.core[max(0, idx-300):idx+200]
        self.assertIn(
            "summarizes implemented behavior",
            segment,
            "L30: must define what counts as a final report",
        )


if __name__ == "__main__":
    unittest.main()
