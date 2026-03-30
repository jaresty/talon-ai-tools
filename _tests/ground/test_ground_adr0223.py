"""Tests for ADR-0223: three escape routes from run 57 + rung table tool-call constraints.

T1 artifact-type freeze: after a rung's completion sentinel, that artifact type is frozen.
T2 formal notation scope: cannot retrieve from prose what criteria omitted.
T3 structural failure at VRO: import/compilation failure ≠ criterion exercised.
T4 rung table tool-call constraints column.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ArtifactTypeFreeze(unittest.TestCase):
    """P6: artifact type frozen after its completion sentinel."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_frozen_after_sentinel(self):
        self.assertIn(
            "frozen artifacts may not be modified at subsequent rungs",
            self.core,
        )

    def test_modifying_frozen_artifact_voids_rung(self):
        self.assertIn(
            "frozen artifacts may not be modified at subsequent rungs",
            self.core,
        )


class TestThread2_FormalNotationScope(unittest.TestCase):
    """P17: formal notation derives only from criteria — vagueness not remedied by reaching back."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_cannot_retrieve_from_prose_what_criteria_omitted(self):
        self.assertIn(
            "scope does not expand between rungs",
            self.core,
        )

    def test_remedy_for_vague_criteria_is_upward_return(self):
        self.assertIn(
            "difficulty, failure, or constraint pressure from any lower rung is not a valid trigger",
            self.core,
        )


class TestThread3_StructuralFailureAtVRO(unittest.TestCase):
    """VRO: import/compilation failure is not criterion exercise."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_criterion_exercised_only_when_assertions_fail(self):
        self.assertIn(
            "criterion is exercised only when the automated validation suite runs to completion and individual assertions fail",
            self.core,
        )

    def test_halted_execution_does_not_exercise_criterion(self):
        self.assertIn(
            "execution halted before reaching the assertions",
            self.core,
        )

    def test_ei_resolves_only_infrastructure_gap(self):
        self.assertIn(
            "the executable-implementation artifact for such a halt resolves only the infrastructure gap",
            self.core,
        )

    def test_new_cycle_required_before_criterion_exercised(self):
        self.assertIn(
            "the criterion has not been exercised until individual assertions fail in a subsequent cycle",
            self.core,
        )


class TestThread4_RungTableToolCallConstraints(unittest.TestCase):
    """Rung table derivation instruction must include a permitted tool calls column."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_rung_table_has_permitted_tool_calls_column(self):
        self.assertIn(
            "permitted tool calls",
            self.core,
        )

    def test_read_observe_always_permitted(self):
        self.assertIn(
            "all rungs permit read, observe, and non-modifying run commands",
            self.core,
        )

    def test_file_modification_constrained_to_artifact_type(self):
        self.assertIn(
            "file modifications are constrained to the artifact type of that rung",
            self.core,
        )


class TestADR0223CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            22_000,
            f"ADR-0223: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
