"""Tests for L7–L12 ground protocol forward-gate closures (ADR-0183)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL7ManifestDeclaredForwardGate(unittest.TestCase):
    """L7: After Manifest declared, the only valid next token is the Thread 1 criteria rung label."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l7_only_valid_next_token_is_thread1_criteria_label(self):
        self.assertIn(
            "the only valid next token is the criteria rung label for Thread 1",
            self.core,
            "L7: criteria paragraph must state that the only valid next token after Manifest declared is the Thread 1 criteria rung label",
        )

    def test_l7_thread_n_criterion_blocked_until_thread_n_complete(self):
        self.assertIn(
            "No criterion for Thread N+1 may appear until \u2705 Thread N complete has been emitted",
            self.core,
            "L7: criteria paragraph must block Thread N+1 criteria until Thread N complete has been emitted",
        )


class TestL8OBRProcessStartQueryGate(unittest.TestCase):
    """L8: OBR process-start requires a subsequent query tool call before exec_observed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l8_two_tool_calls_required_in_sequence(self):
        self.assertIn(
            "two tool calls are required in sequence",
            self.core,
            "L8: OBR paragraph must require two tool calls in sequence (process-start then query)",
        )

    def test_l8_sentinel_not_emitted_until_both_calls_complete(self):
        self.assertIn(
            "sentinel may not be emitted until both complete",
            self.core,
            "L8: OBR paragraph must state exec_observed sentinel may not be emitted until both calls complete",
        )


class TestL9EVHarnessErrorForwardGate(unittest.TestCase):
    """L9: EV harness error → only valid next token is harness-repair tool call."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l9_only_valid_next_token_is_harness_repair(self):
        self.assertIn(
            "the only valid next token is a tool call that repairs the harness",
            self.core,
            "L9: HARD STOP paragraph must state that after EV harness error the only valid next token is a harness-repair tool call",
        )

    def test_l9_hard_stop_may_not_appear_with_harness_error(self):
        self.assertIn(
            "HARD STOP may not appear in the same response as a harness-error exec_observed at the EV rung",
            self.core,
            "L9: must state HARD STOP may not appear in the same response as a harness-error exec_observed at the EV rung",
        )


class TestL10FormalNotationCycleIdentityCheck(unittest.TestCase):
    """L10: Before formal notation, confirm via tool call that criteria was produced this cycle."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l10_confirm_criteria_produced_this_cycle(self):
        self.assertIn(
            "confirm via tool call that the criteria artifact for this cycle was produced in this cycle's transcript",
            self.core,
            "L10: formal notation paragraph must require confirming via tool call that criteria was produced this cycle",
        )


class TestL11ImplGateAsFirstToken(unittest.TestCase):
    """L11: impl_gate is the first token of the EI rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l11_impl_gate_is_first_token_of_ei_rung(self):
        self.assertIn(
            "\U0001f7e2 Implementation gate cleared is the first token of the executable implementation rung",
            self.core,
            "L11: impl_gate paragraph must state that 🟢 Implementation gate cleared is the first token of the EI rung",
        )

    def test_l11_no_content_before_impl_gate(self):
        self.assertIn(
            "no tool call, no prose, and no file modification may appear before it in the current response",
            self.core,
            "L11: impl_gate paragraph must state that no tool call, prose, or file modification may appear before it",
        )


class TestL12FinalReportContentTypeGate(unittest.TestCase):
    """L12: Final report gate is content-type-based, not heading-based."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l12_any_prose_summarizing_implemented_behavior(self):
        self.assertIn(
            "Any prose that summarizes implemented behavior",
            self.core,
            "L12: final report paragraph must classify prose summarizing implemented behavior as a final report regardless of heading",
        )

    def test_l12_such_prose_blocked_until_manifest_exhausted(self):
        self.assertIn(
            "Such prose may not appear until \u2705 Manifest exhausted exists in the transcript for this invocation",
            self.core,
            "L12: must state such prose may not appear until Manifest exhausted exists in the transcript",
        )


if __name__ == "__main__":
    unittest.main()
