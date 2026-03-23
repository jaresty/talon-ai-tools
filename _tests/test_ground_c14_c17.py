"""Tests for C14–C17 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC14ManifestExhaustedRequiresThreadComplete(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c14_thread_count_check(self):
        self.assertIn("thread count before emitting", self.core,
            "C14: Manifest exhausted must require checking thread count matches Thread N complete sentinels")

    def test_c14_positioned_near_manifest_exhausted(self):
        c14_idx = self.core.index("thread count before emitting")
        gate_phrase = "Manifest exhausted \u2014 \u2705 Manifest exhausted may not be emitted"
        manifest_ex_idx = self.core.index(gate_phrase)
        self.assertLess(abs(c14_idx - manifest_ex_idx), 300,
            "C14: thread-count check must appear near the Manifest exhausted gate instruction")


class TestC15HardStopPositionalConstraint(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c15_hard_stop_requires_vro_execution_observed(self):
        self.assertIn(
            "valid only after a \U0001F534 Execution observed: and \U0001F534 Gap: have been emitted "
            "at the validation run observation rung",
            self.core,
            "C15: HARD STOP must be constrained to fire only after VRO Execution observed + Gap")

    def test_c15_hard_stop_other_positions_prohibited(self):
        idx = self.core.index(
            "valid only after a \U0001F534 Execution observed: and \U0001F534 Gap: have been emitted "
            "at the validation run observation rung")
        segment = self.core[idx:idx+300]
        self.assertIn("protocol violation", segment,
            "C15: HARD STOP at non-VRO positions must be named a protocol violation")


class TestC16FinalReportVerbatimCopy(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c16_verbatim_transcript_check(self):
        self.assertIn("cannot be found verbatim in the transcript", self.core,
            "C16: Final Report must require each artifact to be locatable verbatim in the prior transcript")

    def test_c16_positioned_near_final_report_section(self):
        c16_idx = self.core.index("cannot be found verbatim in the transcript")
        final_idx = self.core.index("After emitting \u2705 Manifest exhausted, produce a final report")
        self.assertLess(abs(c16_idx - final_idx), 500,
            "C16: verbatim-copy constraint must appear near the Final Report instruction")


class TestC17ImplicitConjunctionBan(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c17_structural_plus_data_source_is_conjunction(self):
        self.assertIn("names both a structural element and its data source is a conjunction", self.core,
            "C17: conjunction ban must cover implicit form: naming a structural element and its data source")

    def test_c17_positioned_near_existing_conjunction_ban(self):
        c17_idx = self.core.index("names both a structural element and its data source is a conjunction")
        ban_idx = self.core.index("if the criterion contains the word \u2018and\u2019 it is invalid")
        self.assertLess(abs(c17_idx - ban_idx), 400,
            "C17: implicit conjunction clause must appear near the existing explicit conjunction ban")


if __name__ == "__main__":
    unittest.main()
