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
        self.assertIn("locate the N in", self.core,
            "C14/C2: Manifest exhausted must anchor count to declared N in Manifest declared sentinel")

    def test_c14_positioned_near_manifest_exhausted(self):
        c14_idx = self.core.index("locate the N in")
        gate_phrase = "Manifest exhausted \u2014 \u2705 Manifest exhausted may not be emitted"
        manifest_ex_idx = self.core.index(gate_phrase)
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
        # ADR-0181: attractor 7 (final-report transcript gate) removed — subsumed by rung-entry gate.
        # C16 enforcement now fires at rung entry via gate part (b): the current gap as a
        # currently-false assertion must be stateable from the current-cycle transcript.
        self.assertIn("Rung-entry gate", self.core,
            "C16: rung-entry gate (ADR-0181) subsumes final-report transcript check — gate must be present")

    def test_c16_positioned_near_final_report_section(self):
        # ADR-0181: removed phrase no longer anchors position; verify gate precedes final report.
        gate_idx = self.core.index("Rung-entry gate")
        final_idx = self.core.index("After emitting \u2705 Manifest exhausted, produce a final report")
        self.assertLess(gate_idx, final_idx,
            "C16: rung-entry gate must appear before the Final Report instruction")


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
        # Regression: OBR has a completion gate (exec_observed must precede Thread N complete)
        # but no sequencing gate — the model can skip the tool call and emit Thread N complete by inference.
        # This test checks that the prompt names a tool call as the only valid next action after criterion re-emission.
        self.assertIn(
            "the tool call is the only valid next action after criterion re-emission",
            self.core,
            "OBR sequencing gate: tool call must be named as the only valid next action after criterion re-emission",
        )

    def test_obr_thread_complete_requires_tool_call_in_transcript(self):
        # The completion gate must reference a tool call in the transcript, not just an exec_observed sentinel.
        self.assertIn(
            "Thread N complete may not appear until a tool call exists in the transcript",
            self.core,
            "OBR gate must block Thread N complete until a tool call exists after the OBR label in the current cycle",
        )

    def test_obr_test_runner_output_blocks_thread_complete(self):
        # Regression: ADR-0181 removed the OBR test-runner-output sentinel block.
        # Without it the model can satisfy OBR with test runner output and emit Thread N complete.
        self.assertIn(
            "it does not satisfy the OBR gate \u2014 re-invoke the implemented artifact directly",
            self.core,
            "OBR gate must block Thread N complete when exec_observed contains test runner output",
        )


if __name__ == "__main__":
    unittest.main()
