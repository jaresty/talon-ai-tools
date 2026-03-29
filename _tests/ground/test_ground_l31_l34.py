"""Tests for L31–L34: crystal-form forward gates closing EV/VRO/HARD-STOP escape routes.

L31: V-complete forward gate — if pre-existence tool call not made, only valid next action is that call.
L32: HARD STOP harness-classification gate — before emitting HARD STOP, must classify most recent EV
     exec_observed; if it shows a harness error, HARD STOP is a protocol violation.
L33: Unchanged-criterion HARD STOP trap — HARD STOP with criterion identical to prior cycle is a violation.
L34: EV artifact sequencing — file-write tool call must precede test run at EV rung.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestL31VCompleteForwardGate(unittest.TestCase):
    """L31: V-complete must be gated by a forward check, not just a void condition."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_l31_forward_gate_blocks_until_tool_call_made(self):
        """If the pre-existence tool call has not been made, V-complete is blocked."""
        has_gate = (
            "if that tool call has not been made" in self.prompt
            or "if no such tool call exists in the current response" in self.prompt
            or (
                "only valid next action" in self.prompt
                and "pre-exist" in self.prompt
                and "Validation artifact V complete" in self.prompt
            )
        )
        self.assertTrue(
            has_gate,
            "L31: V-complete must have a forward gate — if pre-existence tool call absent, "
            "only valid next action is that tool call",
        )

    def test_l31_gate_names_tool_call_as_only_valid_action(self):
        """The gate must name the pre-existence/failing check tool call as the only valid action."""
        # P4-derivative: explicit L31 sentence OR P4 EV action-set ordering covers this
        explicit_gate = False
        idx = self.prompt.find("confirm via tool call that the artifact path does not pre-exist")
        if idx != -1:
            segment = self.prompt[idx:idx+300]
            explicit_gate = (
                "only valid next action is" in segment
                or "only valid next token is" in segment
            )
        # ADR-0214: P4 named principle removed; sequence table covers EV ordered action set.
        sequence_table_gate = (
            "pre-existence" in self.prompt
            and "EV rung" in self.prompt
            and "in order" in self.prompt
        )
        self.assertTrue(
            explicit_gate or sequence_table_gate,
            "L31: pre-existence check forward gate must be present via explicit rule or EV sequence table",
        )


class TestL32HardStopHarnessClassificationGate(unittest.TestCase):
    """L32: Before emitting HARD STOP, model must classify most recent EV exec_observed."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_l32_before_hard_stop_classify_ev_exec_observed(self):
        """Before emitting HARD STOP, the model must check if most recent EV exec_observed is a harness error."""
        has_gate = (
            "before emitting" in self.prompt
            and "HARD STOP" in self.prompt
            and "harness error" in self.prompt
            and (
                "classify" in self.prompt
                or "most recent" in self.prompt
                or "check whether" in self.prompt
            )
        )
        self.assertTrue(
            has_gate,
            "L32: a pre-hoc check must require classification of the most recent EV exec_observed "
            "before HARD STOP is a valid token",
        )

    def test_l32_hard_stop_blocked_if_ev_shows_harness_error(self):
        """HARD STOP must be explicitly blocked (not just prohibited) when EV exec_observed is a harness error."""
        # The current prohibition exists; verify it is structured as a blocking gate
        idx = self.prompt.find("HARD STOP may not be emitted at the executable validation rung")
        self.assertGreater(idx, -1, "L32 base prohibition must be present")
        segment = self.prompt[idx:idx+500]
        # ADR-0216: "only valid next action" clause removed (derivable from "harness error requires fixing the harness")
        # Verify the base prohibition + harness-requires-fix clause remain
        has_gate = (
            "harness error at EV requires fixing the harness" in segment
            or "only valid next token is a tool call that repairs the harness" in segment
            or "only valid next action" in segment
        )
        self.assertTrue(
            has_gate,
            "L32: when EV exec_observed is a harness error, must state harness requires fixing",
        )

    def test_l32_gate_precedes_hard_stop_definition(self):
        """The harness-classification gate must appear before (or at) the HARD STOP definition."""
        hard_stop_def_idx = self.prompt.find("HARD STOP \u2014 upward return to criteria rung is valid in exactly one case")
        harness_block_idx = self.prompt.find("HARD STOP may not be emitted at the executable validation rung")
        self.assertGreater(hard_stop_def_idx, -1, "HARD STOP validity condition must be present")
        self.assertGreater(harness_block_idx, -1, "Harness-error block must be present")
        # The harness block should appear near the HARD STOP definition (within 600 chars)
        self.assertLess(
            abs(hard_stop_def_idx - harness_block_idx),
            1200,
            "L32: harness-classification gate must be co-located with HARD STOP validity definition (ADR-0205: positive gate text added ~200 chars)",
        )


class TestL33UnchangedCriterionTrap(unittest.TestCase):
    """L33: HARD STOP with criterion identical to prior cycle is a protocol violation."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_l33_unchanged_criterion_rule_present(self):
        """A rule must exist preventing HARD STOP when the criterion is unchanged from the prior cycle."""
        has_rule = (
            "identical" in self.prompt
            and "criterion" in self.prompt
            and "HARD STOP" in self.prompt
        ) or (
            "unchanged" in self.prompt
            and "criterion" in self.prompt
        )
        self.assertTrue(
            has_rule,
            "L33: must have a rule blocking HARD STOP when criterion is identical to the prior cycle",
        )

    def test_l33_names_correct_alternative_action(self):
        """ADR-0188 P5: 'textually identical' block deleted; P5 owns the convergence exit.
        P5 states: criterion has not changed → return to criteria rung (mandatory)."""
        # P5 uses "has not changed" (not "textually identical" or "unchanged")
        idx = self.prompt.find("has not changed")
        self.assertGreater(idx, -1, "L33/P5 rule must be present — 'has not changed' triggers convergence exit")
        segment = self.prompt[max(0, idx-50):idx+400]
        has_alternative = (
            "criteria rung" in segment
            or "formal notation" in segment
            or "executable implementation" in segment
            or "loop within" in segment
        )
        self.assertTrue(
            has_alternative,
            "L33/P5: criterion-unchanged rule must name the correct exit (criteria rung, formal notation, or impl loop)",
        )


class TestL34EVArtifactSequencing(unittest.TestCase):
    """L34: file-write tool call must precede any test run at the EV rung."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_l34_ev_ordering_constraint_present(self):
        """An ordering constraint must state that the EV artifact file-write precedes any test run."""
        has_rule = (
            "before" in self.prompt
            and "executable validation" in self.prompt
            and (
                "file-write" in self.prompt
                or "write the" in self.prompt
            )
            and (
                "run" in self.prompt
                or "invoke" in self.prompt
            )
        ) or (
            "EV artifact must be written" in self.prompt
            or "artifact must exist before" in self.prompt
        )
        self.assertTrue(
            has_rule,
            "L34: EV rung must have an ordering constraint — file-write precedes test run",
        )

    def test_l34_running_before_writing_is_violation(self):
        """Running a test before writing the artifact must be named as a protocol violation."""
        has_rule = (
            "running" in self.prompt
            and "before writing" in self.prompt
        ) or (
            "test run before" in self.prompt
            and "protocol violation" in self.prompt
        ) or (
            "before any run" in self.prompt
            and "artifact" in self.prompt
            and "executable validation" in self.prompt
        )
        self.assertTrue(
            has_rule,
            "L34: running a test before writing the EV artifact must be a protocol violation",
        )


if __name__ == "__main__":
    unittest.main()
