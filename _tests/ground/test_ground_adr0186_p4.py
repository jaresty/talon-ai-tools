"""ADR-0186: P4 (Rung action discipline) — behavioral-effect anchors.

Tests use OR-form so they pass on both the current prompt and any future
post-deletion prompt where P4-derivative explicit rules have been removed.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestP4Named(unittest.TestCase):
    """P4 must be a named principle in the ground prompt."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_p4_named(self):
        # ADR-0214: P4 named principle header removed; closed action sets expressed via sequence table.
        self.assertNotIn(
            "P4 (Rung action discipline)",
            self.prompt,
            "ADR-0214: P4 named principle header must be absent; sequence table carries closed action sets",
        )

    def test_p4_closed_action_set_stated(self):
        has_rule = (
            "closed action set" in self.prompt
            or (
                "P4" in self.prompt
                and "protocol violation" in self.prompt
                and "rung" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must state that each rung has a closed action set")


class TestP4EVActionSet(unittest.TestCase):
    """P4: EV rung action set — pre-existence check, file-write, test runner in order."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_ev_action_set_names_three_steps(self):
        has_rule = (
            "pre-existence or pre-failure check" in self.prompt
            and "test runner" in self.prompt
            and "EV rung" in self.prompt
        ) or (
            "P4" in self.prompt
            and "EV rung" in self.prompt
            and "in that order" in self.prompt
        )
        self.assertTrue(has_rule, "P4 EV action set must name pre-existence check, artifact writes, test runner")

    def test_ev_action_set_ordered(self):
        has_rule = (
            "in that order" in self.prompt
            and "EV rung" in self.prompt
        ) or (
            "only valid next action is that tool call" in self.prompt
        )
        self.assertTrue(has_rule, "P4 EV action set must be ordered")

    def test_ev_no_implementation_writes(self):
        has_rule = (
            "writing implementation files at the EV rung is a protocol violation" in self.prompt
            or "any edit to any other file at the EV rung is a protocol violation" in self.prompt
            or (
                "P4" in self.prompt
                and "EV rung" in self.prompt
                and "implementation" in self.prompt
                and "protocol violation" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must block implementation file writes at the EV rung")


class TestP4VROActionSet(unittest.TestCase):
    """P4: VRO rung — test runner only."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_vro_test_runner_only(self):
        has_rule = (
            "VRO rung: test runner only" in self.prompt
            or (
                "VRO" in self.prompt
                and "test runner only" in self.prompt
            )
            or (
                "validation run observation" in self.prompt
                and "P4" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must state VRO action set is test runner only")


class TestP4EIActionSet(unittest.TestCase):
    """P4: EI rung — exactly one file-write to implementation; meta-test if editing prior EV artifact."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_ei_implementation_files_only(self):
        has_rule = (
            "EI rung: implementation file-writes only" in self.prompt
            or (
                "EI rung" in self.prompt
                and "implementation" in self.prompt
                and "protocol violation" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must constrain EI writes to implementation files")

    def test_ei_meta_test_required_for_prior_ev_artifact(self):
        has_rule = (
            "meta-test pattern is required" in self.prompt
            or (
                "meta-test" in self.prompt
                and "EV artifact" in self.prompt
                and "prior cycle" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must require meta-test when EI edit targets a prior EV artifact")


class TestP4OBRActionSet(unittest.TestCase):
    """P4: OBR rung — read-only tool calls only."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_read_only(self):
        has_rule = (
            "OBR rung: read-only tool calls only" in self.prompt
            or (
                "OBR" in self.prompt
                and "read-only" in self.prompt
            )
        )
        self.assertTrue(has_rule, "P4 must constrain OBR to read-only tool calls")


class TestP4NoProseCriteriaFNToolCalls(unittest.TestCase):
    """P4: prose, criteria, and formal notation rungs have no tool calls."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prose_criteria_fn_no_tool_calls(self):
        has_rule = (
            "prose, criteria, and formal notation rungs: no tool calls" in self.prompt
            or (
                "P4" in self.prompt
                and "formal notation" in self.prompt
                and "no tool calls" in self.prompt
            )
        )
        self.assertTrue(
            has_rule,
            "P4 must state prose/criteria/formal notation rungs have no tool calls",
        )


if __name__ == "__main__":
    unittest.main()
