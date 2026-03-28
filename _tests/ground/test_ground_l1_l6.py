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
        # ADR-0187: rung-entry gate item (d) deleted — entire gate block removed as P1 procedural restatement.
        # P1 (Evidential boundary) carries the guarantee: exec_observed type check gates rung content.
        self.assertNotIn(
            "if (d) reveals that no valid exec_observed exists in the current cycle, the only permitted next token is a tool call",
            self.core,
            "ADR-0187: rung-entry gate item (d) must be absent — deleted as P1 procedural restatement",
        )
        self.assertIn(
            "P1 (Evidential boundary)",
            self.core,
            "P1 must be present to carry the rung-entry forced-stop guarantee",
        )


class TestL4OBRProseProhibition(unittest.TestCase):
    """L4: after criterion re-emission at OBR, prose planning before the tool call is explicitly prohibited."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l4_prose_planning_prohibited_after_criterion_reemission(self):
        # ADR-0187: "planning statements, diagnostic narration..." phrase deleted from OBR prose block.
        # P4 Clause A ("no content other than the next step in the sequence may appear between steps") carries the guarantee.
        self.assertNotIn(
            "planning statements, diagnostic narration, and commentary between criterion re-emission and the tool call are protocol violations",
            self.core,
            "ADR-0187: explicit prose-planning prohibition phrase must be absent — subsumed by P4 Clause A",
        )
        self.assertIn(
            "no content other than the next step in the sequence may appear between steps",
            self.core,
            "P4 Clause A must carry the no-prose-between-steps guarantee",
        )


class TestL5VCompleteResultInTranscript(unittest.TestCase):
    """L5: V-complete requires the tool-call result (exec_observed block) to appear in the transcript."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l5_v_complete_requires_exec_observed_block(self):
        # ADR-0187: "asserting confirmation without showing the exec_observed block does not satisfy this gate"
        # was part of the L31 forward gate, deleted as derivable from P4 EV sequence.
        # P4 EV step (1) pre-existence check + P4 sequence binding (Clause A) carry the guarantee.
        self.assertNotIn(
            "asserting confirmation without showing the exec_observed block does not satisfy this gate",
            self.core,
            "ADR-0187: L31 forward gate phrase must be absent — subsumed by P4 Clause A + EV sequence",
        )
        self.assertIn(
            "EV rung: (1) pre-existence or pre-failure check",
            self.core,
            "P4 EV sequence must be present to carry the V-complete exec_observed guarantee",
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
