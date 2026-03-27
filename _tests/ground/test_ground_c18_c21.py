"""Tests for C18–C21 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC18ProtocolStickiness(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c18_subsequent_response_starts_with_rung_check(self):
        self.assertIn(
            "every subsequent response must begin by identifying the current rung",
            self.core,
            "C18: ground must require every subsequent response to identify current rung before other content")

    def test_c18_protocol_active_after_manifest_exhausted(self):
        idx = self.core.index("every subsequent response must begin by identifying the current rung")
        segment = self.core[idx:idx+300]
        self.assertIn("Manifest exhausted", segment,
            "C18: stickiness rule must explicitly state protocol remains active past Manifest exhausted")


class TestC19PostDeliveryIntegration(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c19_post_delivery_integration_observation(self):
        self.assertIn("post-delivery integration observation", self.core,
            "C19: ground must require a post-delivery integration OBS before the final report")

    def test_c19_positioned_before_final_report(self):
        c19_idx = self.core.index("post-delivery integration observation")
        final_idx = self.core.index("After emitting \u2705 Manifest exhausted, produce a final report")
        self.assertLess(abs(c19_idx - final_idx), 800,
            "C19: post-delivery integration gate must appear near the final report instruction")


class TestC20RedRunBeforeImplementation(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c20_red_run_required_before_implementation(self):
        # ADR-0182: "implementation edits may not begin until a red run exists" removed as P2 corollary.
        # P2 + rung table EI gate ("exec_observed + gap declared; impl_gate sentinel emitted") subsume it.
        from lib.groundPrompt import RUNG_SEQUENCE
        ei_entry = next(e for e in RUNG_SEQUENCE if e["name"] == "executable implementation")
        self.assertIn(
            "exec_observed + gap declared",
            ei_entry["gate"],
            "C20: EI rung table gate must require exec_observed + gap — P2 + rung table subsume red-run-before-edit")

    def test_c20_positioned_in_ev_rung(self):
        # ADR-0182: anchor sentence removed; verify EI gate in rung table covers the C20 requirement.
        from lib.groundPrompt import RUNG_SEQUENCE
        ei_entry = next(e for e in RUNG_SEQUENCE if e["name"] == "executable implementation")
        self.assertIn(
            "exec_observed",
            ei_entry["gate"],
            "C20: EI rung table gate must include exec_observed as precondition (subsumes red-run-before-edit)")


class TestC21FormalNotationNonCompilable(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c21_compilability_test(self):
        self.assertIn(
            "cannot be directly compiled or executed without modification",
            self.core,
            "C21: formal notation validity must be defined by non-compilability, not a prohibition list")

    def test_c21_positioned_in_formal_notation_section(self):
        # ADR-0182: "Formal notation encodes only" anchor removed as P3 corollary.
        # Anchor updated to retained sentence "The formal notation rung separates behavioral specification".
        c21_idx = self.core.index("cannot be directly compiled or executed without modification")
        fn_idx = self.core.index("The formal notation rung separates behavioral specification")
        self.assertLess(abs(c21_idx - fn_idx), 900,
            "C21: compilability test must appear in the formal notation rung section")


if __name__ == "__main__":
    unittest.main()
