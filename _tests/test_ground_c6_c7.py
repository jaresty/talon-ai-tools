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
        preexist_idx = self.core.index("confirm via tool call that the artifact path does not pre-exist")
        tree_idx = self.core.index("version-controlled file tree")
        self.assertGreater(tree_idx, preexist_idx,
            "C6: version-controlled tree requirement must appear after the pre-existence check clause")

    def test_c6_positioned_before_v_complete_sentinel(self):
        tree_idx = self.core.index("version-controlled file tree")
        v_complete_idx = self.core.index("\u2705 Validation artifact V complete must be emitted")
        self.assertLess(tree_idx, v_complete_idx,
            "C6: version-controlled tree requirement must appear before the V-complete sentinel line")


class TestC7ObservedRunningBehaviorType(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c7_distinguishes_implemented_artifact_from_tests(self):
        orb_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        segment = self.core[orb_idx:thread_complete_idx]
        self.assertIn("not the", segment,
            "C7: observed running behavior rung must explicitly distinguish implemented artifact from test suite")

    def test_c7_prohibits_running_tests_at_orb_rung(self):
        orb_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        segment = self.core[orb_idx:thread_complete_idx]
        self.assertTrue(
            "test" in segment.lower() and "not" in segment.lower(),
            "C7: ground must state that running tests does not satisfy the observed running behavior rung")

    def test_c7_carveout_for_non_invocable_artifacts(self):
        orb_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        segment = self.core[orb_idx:thread_complete_idx]
        self.assertIn("no directly invocable artifact", segment,
            "C7: ground must include a carve-out for implementations with no directly invocable artifact")


if __name__ == "__main__":
    unittest.main()
