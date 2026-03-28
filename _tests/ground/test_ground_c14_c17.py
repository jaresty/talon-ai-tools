"""Tests for C14–C17 ground protocol escape-route closures."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC14ManifestExhaustedRequiresThreadComplete(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c14_thread_count_check(self):
        # ADR-0180 C2 supersedes the original vague "check the thread count" phrase with a
        # specific anchor: locate the N in Manifest declared and compare against Thread N complete sentinels.
        self.assertIn("Manifest exhausted may not be emitted unless the count of", self.core,
            "C14/C2: Manifest exhausted must anchor count to declared N in Manifest declared sentinel")

    def test_c14_positioned_near_manifest_exhausted(self):
        c14_idx = self.core.index("Manifest exhausted may not be emitted unless the count of")
        # L26 gate and C14 gate are now the same sentence — just check it exists within session-persistence block
        manifest_ex_idx = self.core.index("it remains active until the session ends or the user explicitly exits")
        self.assertLess(abs(c14_idx - manifest_ex_idx), 400,
            "C14/C2: thread-count anchor must appear near the Manifest exhausted gate instruction")


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
        # ADR-0187: rung-entry gate block deleted entirely (P1 procedural restatement).
        # C16 behavioral guarantee now carried by P1 evidential boundary.
        self.assertNotIn("Rung-entry gate", self.core,
            "C16: rung-entry gate must be absent (ADR-0187: deleted as P1 procedural restatement)")
        self.assertIn("P1 (Evidential boundary)", self.core,
            "C16: P1 must be present to carry the rung-entry guarantee")

    def test_c16_positioned_near_final_report_section(self):
        # ADR-0187: rung-entry gate block deleted — position test replaced by absence assertion.
        self.assertNotIn("Rung-entry gate", self.core,
            "C16: rung-entry gate must be absent (ADR-0187)")


class TestC17ImplicitConjunctionBan(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c17_structural_plus_data_source_is_conjunction(self):
        self.assertIn("names both a structural element and its data source is a conjunction", self.core,
            "C17: conjunction ban must cover implicit form: naming a structural element and its data source")

    def test_c17_positioned_near_existing_conjunction_ban(self):
        c17_idx = self.core.index("names both a structural element and its data source is a conjunction")
        ban_idx = self.core.index("if the criterion contains the word \u2018and\u2019 it is a conjunction")
        self.assertLess(abs(c17_idx - ban_idx), 400,
            "C17: implicit conjunction clause must appear near the explicit conjunction definition")

    def test_conjunction_explicit_has_split_action(self):
        # Regression: ADR-0181 removed "split before continuing" from the explicit conjunction clause.
        # Without the action verb the model identifies the conjunction but is not gated from continuing.
        self.assertIn(
            "it is a conjunction \u2014 split before continuing",
            self.core,
            "Explicit conjunction clause must prescribe 'split before continuing' not just identify the pattern",
        )

    def test_conjunction_implicit_has_split_action(self):
        # Regression: ADR-0181 removed "split before continuing" from the implicit (structural+data) conjunction clause.
        self.assertIn(
            "data source is a conjunction \u2014 split before continuing",
            self.core,
            "Implicit conjunction clause must also prescribe 'split before continuing'",
        )

    def test_obr_tool_call_is_only_valid_next_action(self):
        # ADR-0187: "the tool call is the only valid next action after criterion re-emission" deleted.
        # Incompatible with new P4 Clause B: provenance statement (step 2) is now required between
        # criterion re-emission (step 1) and live-process invocation (step 3).
        # P4 Clause A ("no content other than the next step") carries the sequencing guarantee.
        self.assertNotIn(
            "the tool call is the only valid next action after criterion re-emission",
            self.core,
            "ADR-0187: this phrase must be absent — incompatible with P4 Clause B provenance statement step",
        )
        self.assertIn(
            "no content other than the next step in the sequence may appear between steps",
            self.core,
            "P4 Clause A must carry the OBR sequencing guarantee",
        )

    def test_obr_thread_complete_requires_tool_call_in_transcript(self):
        # ADR-0187: condition (1) preamble deleted — derivable from P4 Clause B step (3) + Clause A sequence binding.
        # P4 Clause B names live-process invocation (tool call) as step (3); Clause A requires the full sequence.
        self.assertNotIn(
            "Thread N complete may not appear until a tool call exists in the transcript",
            self.core,
            "ADR-0187: condition (1) preamble must be absent — derivable from P4 Clause A+B",
        )
        self.assertIn(
            "live-process invocation",
            self.core,
            "P4 Clause B must name live-process invocation (tool call) as a required OBR step",
        )

    def test_obr_test_runner_output_blocks_thread_complete(self):
        # ADR-0187: rung-entry gate deleted (P1 procedural restatement).
        # OBR test-runner blocking now carried by: P1 (test runner output is not live-process output type)
        # + OBR rung table void condition + P4 Clause B (test suite is step 5, after live-process step 3).
        self.assertIn(
            "P1 (Evidential boundary)",
            self.core,
            "OBR test-runner prohibition carried by P1 (test runner output is not live-process output type)",
        )
        self.assertNotIn(
            "Rung-entry gate",
            self.core,
            "ADR-0187: rung-entry gate must be absent — deleted as P1 procedural restatement",
        )
        self.assertIn(
            "test runner output — a test-suite pass is validation-run-observation-type output",
            self.core,
            "OBR rung table void condition must name test-runner output as voiding the rung",
        )


    def test_obr_partial_demonstration_requires_gap_and_return(self):
        # If OBR exec_observed does not directly demonstrate the criterion, the model must
        # emit Gap: naming what is undemonstrated and apply failure-class upward-return routing.
        # Without this gate the model can rationalize partial evidence as sufficient.
        self.assertIn(
            "does not directly demonstrate the criterion",
            self.core,
            "OBR partial-demonstration gate: prompt must name the failure path when exec_observed is insufficient",
        )
        self.assertIn(
            "upward-return failure-class rules",
            self.core,
            "OBR partial-demonstration gate: failure path must defer to failure-class routing, not hardcode a rung",
        )


if __name__ == "__main__":
    unittest.main()
