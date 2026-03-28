"""Tests for C6 (artifact location gate) and C7 (observed running behavior type constraint)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC6ArtifactLocationGate(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c6_tmp_prohibited(self):
        self.assertIn("version-controlled file tree", self.core,
            "C6: ground must require validation artifacts to reside within the version-controlled file tree")

    def test_c6_positioned_after_head_check(self):
        # ADR-0187: "confirm via tool call that the artifact path does not pre-exist" deleted (L31 forward gate).
        # Pre-existence check is now carried by P4 EV sequence step (1).
        # Position test updated: version-controlled tree requirement must appear after the P4 EV sequence.
        p4_ev_idx = self.core.index("EV rung: (1) pre-existence or pre-failure check")
        tree_idx = self.core.index("version-controlled file tree")
        self.assertGreater(tree_idx, p4_ev_idx,
            "C6: version-controlled tree requirement must appear after the P4 EV sequence (ADR-0187: L31 phrase deleted)")

    def test_c6_positioned_before_v_complete_sentinel(self):
        tree_idx = self.core.index("version-controlled file tree")
        v_complete_idx = self.core.index("\u2705 Validation artifact V complete must be emitted")
        self.assertLess(tree_idx, v_complete_idx,
            "C6: version-controlled tree requirement must appear before the V-complete sentinel line")


class TestC7ObservedRunningBehaviorType(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c7_distinguishes_implemented_artifact_from_tests(self):
        # ADR-0188 Fix 1: OBR void condition scoped; the cross-type distinction is now expressed as
        # "test runner output used as OBR live-process evidence voids this rung".
        self.assertIn(
            "test runner output used as OBR live-process evidence voids this rung",
            self.core,
            "C7: OBR rung table void condition must distinguish live-process evidence from test runner output")

    def test_c7_prohibits_running_tests_at_orb_rung(self):
        # ADR-0188 Fix 1: void condition scoped; step-5 run is permitted, live-process-evidence use is not.
        self.assertIn(
            "test runner output used as OBR live-process evidence voids this rung",
            self.core,
            "C7: OBR rung table void condition must state test-runner output voids the rung when used as live-process evidence")

    def test_c7_carveout_for_non_invocable_artifacts(self):
        # ADR-0187: "Upon writing the observed running behavior label" deleted (criterion re-emission rule).
        # Test updated to check the carve-out phrase is present globally (not bounded by deleted section marker).
        self.assertIn("no runnable artifact exists", self.core,
            "C7: ground must include a carve-out for implementations with no runnable artifact")


if __name__ == "__main__":
    unittest.main()
