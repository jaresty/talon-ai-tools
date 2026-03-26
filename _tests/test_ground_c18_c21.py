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
        self.assertLess(abs(c19_idx - final_idx), 400,
            "C19: post-delivery integration gate must appear near the final report instruction")


class TestC20RedRunBeforeImplementation(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c20_red_run_required_before_implementation(self):
        self.assertIn(
            "implementation edits may not begin until a red run exists",
            self.core,
            "C20: ground must gate implementation edits on a red run existing in the transcript")

    def test_c20_positioned_in_ev_rung(self):
        # ADR-0181: "Only validation artifacts may be produced" removed (attractor 1 subsumed by gate).
        # EV rung now opens with "each test function asserts exactly one behavioral property".
        c20_idx = self.core.index("implementation edits may not begin until a red run exists")
        ev_idx = self.core.index("each test function asserts exactly one behavioral property")
        v_complete_idx = self.core.index("\u2705 Validation artifact V complete must be emitted")
        self.assertGreater(c20_idx, ev_idx,
            "C20: red-run-before-edit gate must appear after the EV rung start")
        self.assertLess(c20_idx, v_complete_idx + 200,
            "C20: red-run-before-edit gate must appear before the V-complete sentinel line")


class TestC21FormalNotationNonCompilable(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c21_compilability_test(self):
        self.assertIn(
            "cannot be directly compiled or executed without modification",
            self.core,
            "C21: formal notation validity must be defined by non-compilability, not a prohibition list")

    def test_c21_positioned_in_formal_notation_section(self):
        c21_idx = self.core.index("cannot be directly compiled or executed without modification")
        fn_idx = self.core.index("Formal notation encodes only")
        self.assertLess(abs(c21_idx - fn_idx), 600,
            "C21: compilability test must appear in the formal notation rung section")


if __name__ == "__main__":
    unittest.main()
