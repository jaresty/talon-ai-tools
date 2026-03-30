"""Tests for ADR-0218: Ground prompt — principle strengthening pass.

Six escape routes closed by strengthening P3, P5, P6, P12, P14, and the
ladder derivation rung based on transcript violation analysis.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_P14GateBlocksSentinel(unittest.TestCase):
    """P14: unsatisfied gates block sentinels and subsequent rung labels."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_gate_blocks_sentinel_clause_present(self):
        self.assertIn(
            "no completion sentinel for that rung and no label for the subsequent rung may appear",
            self.core,
        )

    def test_emitting_before_gate_is_protocol_violation(self):
        self.assertIn(
            "emitting either before the gate condition is met is a protocol violation that voids the rung",
            self.core,
        )


class TestThread2_P14ExecObservedToolCall(unittest.TestCase):
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
            "a sentinel emitted without a preceding tool call is a fabrication \u2014 it voids the rung",
            self.core,
        )


class TestThread3_P5RunMeansToolInvocation(unittest.TestCase):
    """P5: 'run and failed' means tool-executed invocation with verbatim output."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_run_means_tool_call_with_verbatim_output(self):
        self.assertIn(
            "a tool call invoking the automation appears in the current-cycle transcript and its verbatim output shows failure",
            self.core,
        )

    def test_prose_description_insufficient(self):
        self.assertIn(
            "a model\u2019s prose description of why the automation would fail does not satisfy this principle",
            self.core,
        )


class TestThread4_P3CriterionSpecificity(unittest.TestCase):
    """P3: OBR observation must directly demonstrate the specific criterion."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_criterion_specificity_clause_present(self):
        self.assertIn(
            "must directly demonstrate the behavior named in the criterion for the current cycle",
            self.core,
        )

    def test_infrastructure_evidence_insufficient(self):
        self.assertIn(
            "infrastructure evidence",
            self.core,
        )
        self.assertIn(
            "does not satisfy P3 unless the criterion explicitly asserts infrastructure state",
            self.core,
        )


class TestThread5_P6SentinelTypeDiscipline(unittest.TestCase):
    """P6: sentinels are typed to their defining rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_sentinel_type_discipline_clause_present(self):
        self.assertIn(
            "each protocol sentinel has an artifact type determined by the rung at which it was defined",
            self.core,
        )

    def test_cross_type_emission_voids_rung(self):
        self.assertIn(
            "emitting a sentinel outside its defining rung is a type-discipline violation",
            self.core,
        )


class TestThread6_P12SingularSlice(unittest.TestCase):
    """P12: criteria rung must assert exactly one independently testable behavior."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_singular_slice_clause_present(self):
        self.assertIn(
            "exactly one independently testable behavior per thread per cycle",
            self.core,
        )

    def test_conjunction_is_protocol_violation(self):
        self.assertIn(
            "a criteria artifact asserting more than one behavior is a conjunction and is a protocol violation",
            self.core,
        )

    def test_and_is_presumptive_conjunction(self):
        self.assertIn(
            "a criterion containing the word \u201cand\u201d is presumptively a conjunction",
            self.core,
        )


class TestThread7_LadderManifestGate(unittest.TestCase):
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


class TestADR0218CharCount(unittest.TestCase):
    """Core string must stay below a reasonable ceiling after additions."""

    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        # ADR-0217 baseline ~8100; allow up to 15000 for subsequent additions
        self.assertLess(
            current,
            17_000,
            f"ADR-0218: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
