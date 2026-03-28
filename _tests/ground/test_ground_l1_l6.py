"""Tests for L1–L6 ground protocol drift closures (narrative compliance escape routes)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL1ExecObservedPrecondition(unittest.TestCase):
    """L1: exec_observed sentinel requires a tool call to exist in the current response before it."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l1_tool_call_must_precede_sentinel(self):
        self.assertIn(
            "preceding tool call in this response",
            self.core,
            "L1: exec_observed paragraph must require a preceding tool call in this response (ADR-0184: condensed form)",
        )

    def test_l1_sentinel_without_tool_call_is_void(self):
        self.assertIn(
            "deviation voids the sentinel",
            self.core,
            "L1: must state that any deviation voids the sentinel (ADR-0184: condensed form replacing explicit void clause)",
        )


class TestL2HardStopValidityGate(unittest.TestCase):
    """L2: HARD STOP gates on exec_observed validity (non-empty verbatim block), not just presence."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l2_hard_stop_requires_valid_exec_observed(self):
        self.assertIn(
            "prose-only exec_observed sentinel does not satisfy this gate",
            self.core,
            "L2: HARD STOP rule must state that a prose-only exec_observed does not satisfy its precondition",
        )


class TestL3RungEntryForcedStop(unittest.TestCase):
    """L3: rung-entry gate forces a stop (tool call only) when (d) reveals no valid exec_observed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l3_false_d_forces_tool_call_only(self):
        self.assertIn(
            "if (d) reveals that no valid exec_observed exists in the current cycle, the only permitted next token is a tool call",
            self.core,
            "L3: rung-entry gate must force a tool-call-only next token when (d) is false",
        )


class TestL4OBRProseProhibition(unittest.TestCase):
    """L4: after criterion re-emission at OBR, prose planning before the tool call is explicitly prohibited."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l4_prose_planning_prohibited_after_criterion_reemission(self):
        self.assertIn(
            "planning statements, diagnostic narration, and commentary between criterion re-emission and the tool call are protocol violations",
            self.core,
            "L4: OBR paragraph must explicitly prohibit prose planning between criterion re-emission and tool call",
        )


class TestL5VCompleteResultInTranscript(unittest.TestCase):
    """L5: V-complete requires the tool-call result (exec_observed block) to appear in the transcript."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l5_v_complete_requires_exec_observed_block(self):
        self.assertIn(
            "asserting confirmation without showing the exec_observed block does not satisfy this gate",
            self.core,
            "L5: V-complete paragraph must require the exec_observed block to appear in the transcript, not just assert confirmation",
        )


class TestL6P3EditDefinition(unittest.TestCase):
    """L6: P3 'one edit' is defined as one tool-call file write."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l6_one_edit_means_one_file_write_tool_call(self):
        self.assertIn(
            "one edit means exactly one tool call that creates or modifies a file",
            self.core,
            "L6: P3 scope discipline must define 'one edit' as one tool-call file write",
        )


if __name__ == "__main__":
    unittest.main()
