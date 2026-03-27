"""Tests for C9–C13 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC9FormalNotationArtifactType(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c9_prohibits_executable_code(self):
        self.assertIn("type signatures, interfaces, pseudocode", self.core,
            "C9: formal notation rung must state permitted artifact types")

    def test_c9_executable_code_prohibited(self):
        idx = self.core.index("type signatures, interfaces, pseudocode")
        segment = self.core[idx:idx+500]
        self.assertIn("cannot be directly compiled or executed without modification", segment,
            "C9/C21: formal notation gate must use compilability test to prohibit implementation code")

    def test_c9_positioned_before_ev_rung(self):
        # ADR-0181: "Only validation artifacts may be produced" removed (attractor 1 subsumed by gate).
        # EV rung now opens with "each test function asserts exactly one behavioral property".
        fn_idx = self.core.index("type signatures, interfaces, pseudocode")
        ev_idx = self.core.index("each test function asserts exactly one behavioral property")
        self.assertLess(fn_idx, ev_idx,
            "C9: formal notation gate must appear before the EV rung section")


class TestC10EVRequiredAfterUpwardReturn(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c10_prior_cycle_does_not_satisfy(self):
        self.assertIn("prior cycle does not satisfy this gate", self.core,
            "C10: ground must state that a prior-cycle EV artifact does not satisfy EV after upward return")

    def test_c10_positioned_after_upward_return_clause(self):
        upward_idx = self.core.index("Upward returns follow the failure class")
        c10_idx = self.core.index("prior cycle does not satisfy this gate")
        self.assertGreater(c10_idx, upward_idx,
            "C10: prior-cycle disqualification must appear after the upward-return section")


class TestC11HarnessErrorGatePosition(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c11_fix_harness_before_red_witness(self):
        self.assertIn("fix the harness error before treating any run as a red witness", self.core,
            "C11: ground must require fixing harness errors before treating any run as a red witness")

    def test_c11_positioned_near_harness_error_clause(self):
        harness_idx = self.core.index("a harness error (import failure")
        fix_idx = self.core.index("fix the harness error before treating any run as a red witness")
        self.assertLess(abs(fix_idx - harness_idx), 400,
            "C11: fix-harness-first sentence must appear near the harness-error disqualification")


class TestC12ManifestCoverageAtDeclaration(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c12_each_predicate_requires_thread(self):
        self.assertIn("each distinct predicate requires a separate thread", self.core,
            "C12: manifest declaration must require a thread for each behavioral predicate")

    def test_c12_positioned_before_manifest_sentinel(self):
        c12_idx = self.core.index("each distinct predicate requires a separate thread")
        manifest_sentinel = "✅ Manifest declared"
        # The gate must appear before the sentinel definition at end of prompt
        sentinel_block_idx = self.core.rindex(manifest_sentinel)
        self.assertLess(c12_idx, sentinel_block_idx,
            "C12: predicate-per-thread gate must appear before the manifest sentinel definition")


class TestC13ManifestOnce(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c13_exactly_once_stated(self):
        self.assertIn("exactly once per invocation", self.core,
            "C13: ground must prohibit re-declaring the manifest — exactly once per invocation")

    def test_c13_positioned_near_manifest_gate(self):
        c13_idx = self.core.index("exactly once per invocation")
        predicate_idx = self.core.index("each distinct predicate requires a separate thread")
        self.assertLess(abs(c13_idx - predicate_idx), 600,
            "C13: once-per-invocation prohibition must appear near manifest coverage gate")


if __name__ == "__main__":
    unittest.main()
