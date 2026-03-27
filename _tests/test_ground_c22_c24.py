"""Tests for C22–C24 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL



class TestC23CriterionMatchesManifestGap(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c23_narrowing_criterion_prohibited(self):
        self.assertIn(
            "narrowing the criterion, substituting a weaker behavior",
            self.core,
            "C23: criteria rung must prohibit narrowing the criterion from the declared manifest gap")

    def test_c23_positioned_in_criteria_section(self):
        # ADR-0182: "From the criteria rung onward" and "Formal notation encodes only" anchors removed as P3 corollaries.
        # Criterion-fidelity gate is in the criteria section; verify it's before the formal notation section.
        c23_idx = self.core.index("narrowing the criterion, substituting a weaker behavior")
        fn_idx = self.core.index("The formal notation rung separates behavioral specification")
        self.assertLess(c23_idx, fn_idx,
            "C23: criterion-fidelity gate must appear before the formal notation section")


class TestC24VCompleteRequiresRedRun(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c24_v_complete_before_red_run_prohibited(self):
        # ADR-0182: "emitting V-complete before seeing a red run is a protocol violation" removed as P2 corollary.
        # P2 + EI rung table gate ("exec_observed + gap declared") subsumes the red-run-before-V-complete gate.
        from lib.groundPrompt import RUNG_SEQUENCE
        ei_entry = next(e for e in RUNG_SEQUENCE if e["name"] == "executable implementation")
        self.assertIn(
            "exec_observed",
            ei_entry["gate"],
            "C24: EI rung table gate must include exec_observed — P2 + rung table subsume V-complete-before-red-run")

    def test_c24_positioned_before_v_complete_sentinel(self):
        # ADR-0182: "emitting V-complete before seeing a red run" removed; anchor updated to perturbation check.
        # The perturbation check ("perturb the implementation to force a red run") covers the same escape route.
        c24_idx = self.core.index("perturb the implementation to force a red run")
        ev_idx = self.core.index("each test function asserts exactly one behavioral property")
        self.assertGreater(c24_idx, ev_idx,
            "C24: perturbation check must appear in the EV rung section")


if __name__ == "__main__":
    unittest.main()
