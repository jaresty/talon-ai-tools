"""Tests for ADR-0224: text-artifact rungs response-only; criterion falsifiability; V complete gate.

T1 text-artifact rungs: prose/criteria/formal-notation produce response content only — no file writes.
T2 criterion falsifiability: criterion must be a falsifiable behavioral assertion, not a feature name.
T3 V complete gate: file must not pre-exist AND must be written by a tool call in current response.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_TextArtifactRungsResponseOnly(GroundADRTestBase):
    """P6: text artifact types (prose, criteria, formal notation) produce response content only."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_text_artifact_types_response_only(self):
        self.assertIn(
            "One rung per type; text rungs produce no files",
            self.core,
        )

    def test_no_file_representation(self):
        self.assertIn(
            "text rungs produce no files",
            self.core,
        )

    def test_writing_file_at_text_rung_is_violation(self):
        self.assertIn(
            "text rungs produce no files",
            self.core,
        )


class TestThread2_CriterionFalsifiability(GroundADRTestBase):
    """P12: criterion must be a falsifiable behavioral assertion."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_criterion_is_falsifiable_assertion(self):
        self.assertIn(
            "criterion is a falsifiable behavioral assertion",
            self.core,
        )

    def test_given_action_observable_outcome(self):
        self.assertIn(
            "criterion is a falsifiable behavioral assertion",
            self.core,
        )

    def test_feature_name_is_not_criterion(self):
        self.assertIn(
            "a feature name is not a criterion",
            self.core,
        )


class TestThread3_VCompleteGate(GroundADRTestBase):
    """V complete gate: pre-existence check + tool call write both required."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_pre_existence_check_required(self):
        self.assertIn(
            "pre-existence check tool call result present",
            self.prompt,
        )

    def test_tool_call_wrote_file(self):
        self.assertIn(
            "tool call in this response wrote the file to disk",
            self.prompt,
        )


class TestADR0224CharCount(GroundADRTestBase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            22_000,
            f"ADR-0224: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
