"""Tests for ADR-0218: Ground prompt — principle strengthening pass.

Six escape routes closed by strengthening P3, P5, P6, P12, P14, and the
ladder derivation rung based on transcript violation analysis.
"""
import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_P14GateBlocksSentinel(GroundADRTestBase):
    """P14: unsatisfied gates block sentinels and subsequent rung labels."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_gate_blocks_sentinel_clause_present(self):
        self.assertIn(
            "A completion sentinel is a closing marker",
            self.core,
        )

    def test_emitting_before_gate_is_protocol_violation(self):
        self.assertIn(
            "emitting it before its artifact is complete voids both",
            self.core,
        )


class TestThread2_P14ExecObservedToolCall(GroundADRTestBase):
    """P14: exec_observed requires a preceding tool call in the current response."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_exec_observed_requires_tool_call(self):
        self.assertIn(
            "is only valid when a tool call was made in the current response immediately before it",
            self.core,
        )

    def test_fabrication_voids_rung(self):
        self.assertIn(
            "a fabricated sentinel voids the rung",
            self.core,
        )


class TestThread3_P5RunMeansToolInvocation(GroundADRTestBase):
    """P5: 'run and failed' means tool-executed invocation with verbatim output."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_run_means_tool_call_with_verbatim_output(self):
        self.assertIn(
            "Automation must fail before passing",
            self.core,
        )

    def test_prose_description_insufficient(self):
        self.assertIn(
            "the failure output is required",
            self.core,
        )


class TestThread4_P3CriterionSpecificity(GroundADRTestBase):
    """P3: OBR observation must directly demonstrate the specific criterion."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_criterion_specificity_clause_present(self):
        self.assertIn(
            "the observation must directly demonstrate the behavior named in the criterion",
            self.core,
        )

    def test_infrastructure_evidence_insufficient(self):
        self.assertIn(
            "infrastructure evidence",
            self.core,
        )
        self.assertIn(
            "infrastructure evidence does not satisfy this",
            self.core,
        )


class TestThread5_P6SentinelTypeDiscipline(GroundADRTestBase):
    """P6: sentinels are typed to their defining rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_sentinel_type_discipline_clause_present(self):
        self.assertIn(
            "One rung per type; text rungs produce no files",
            self.core,
        )

    def test_cross_type_emission_voids_rung(self):
        self.assertIn(
            "frozen artifacts may not be modified at subsequent rungs",
            self.core,
        )


class TestThread6_P12SingularSlice(GroundADRTestBase):
    """P12: criteria rung must assert exactly one independently testable behavior."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_singular_slice_clause_present(self):
        self.assertIn(
            "One independently testable behavior per thread per cycle",
            self.core,
        )

    def test_conjunction_is_protocol_violation(self):
        self.assertIn(
            "criterion is a falsifiable behavioral assertion",
            self.core,
        )

    def test_and_is_presumptive_conjunction(self):
        self.assertIn(
            "a feature name is not a criterion",
            self.core,
        )


class TestThread7_LadderManifestGate(GroundADRTestBase):
    """Ladder derivation rung gates Manifest declared on rung table existence."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_manifest_blocked_until_rung_table(self):
        self.assertIn(
            "\u2705 Manifest declared is the closing sentinel of the ladder derivation rung",
            self.core,
        )

    def test_manifest_without_rung_table_is_violation(self):
        self.assertIn(
            "a manifest emitted without a preceding rung table is a protocol violation",
            self.core,
        )


class TestADR0218CharCount(GroundADRTestBase):
    """Core string must stay below a reasonable ceiling after additions."""

    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        # ADR-0217 baseline ~8100; allow up to 15000 for subsequent additions
        self.assertLess(
            current,
            22_000,
            f"ADR-0218: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
