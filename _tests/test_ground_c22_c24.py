"""Tests for C22–C24 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC22OBSBuildOutputProhibited(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c22_build_output_never_satisfies(self):
        self.assertIn(
            "build output or compilation result never satisfies this gate",
            self.core,
            "C22: OBS gate must explicitly prohibit build output as direct demonstration")

    def test_c22_positioned_in_obs_section(self):
        c22_idx = self.core.index(
            "build output or compilation result never satisfies this gate")
        obs_idx = self.core.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.core.index("\u2705 Thread N complete may not be emitted")
        self.assertGreater(c22_idx, obs_idx,
            "C22: build-output prohibition must appear after the OBS rung label")
        self.assertLess(c22_idx, thread_complete_idx,
            "C22: build-output prohibition must appear before the Thread N complete gate")


class TestC23CriterionMatchesManifestGap(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c23_narrowing_criterion_prohibited(self):
        self.assertIn(
            "narrowing the criterion, substituting a weaker behavior",
            self.core,
            "C23: criteria rung must prohibit narrowing the criterion from the declared manifest gap")

    def test_c23_positioned_in_criteria_section(self):
        c23_idx = self.core.index("narrowing the criterion, substituting a weaker behavior")
        crit_idx = self.core.index("From the criteria rung onward")
        fn_idx = self.core.index("Formal notation encodes only")
        self.assertGreater(c23_idx, crit_idx,
            "C23: criterion-fidelity gate must appear after the criteria rung section start")
        self.assertLess(c23_idx, fn_idx,
            "C23: criterion-fidelity gate must appear before the formal notation section")


class TestC24VCompleteRequiresRedRun(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c24_v_complete_before_red_run_prohibited(self):
        self.assertIn(
            "emitting V-complete before seeing a red run is a protocol violation",
            self.core,
            "C24: V-complete gate must explicitly prohibit emission before a red run exists in transcript")

    def test_c24_positioned_before_v_complete_sentinel(self):
        c24_idx = self.core.index(
            "emitting V-complete before seeing a red run is a protocol violation")
        v_complete_idx = self.core.index(
            "\u2705 Validation artifact V complete must be emitted at the executable validation rung")
        self.assertLess(c24_idx, v_complete_idx + 100,
            "C24: V-complete red-run gate must appear immediately before the V-complete sentinel line")


if __name__ == "__main__":
    unittest.main()
