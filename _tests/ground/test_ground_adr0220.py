"""Tests for ADR-0220: six structural escape routes closed.

T1 sentinel-closing-marker: completion sentinels close artifacts, not open them.
T2 rung-artifact-exclusivity: only rung artifact type between label and sentinel.
T3 ei-minimal-scope: EI is minimum change to flip the gap.
T4 hard-stop-first-cycle: HARD STOP invalid in thread's first cycle.
T5 obr-bookend: standard derivation begins with OBR; prose gated on prior OBR.
T6 manifest-ordering: rung table appears before Manifest declared in ladder rung.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_SentinelClosingMarker(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_sentinel_is_closing_marker(self):
        self.assertIn(
            "completion sentinel is a closing marker",
            self.core,
        )

    def test_sentinel_before_artifact_is_violation(self):
        self.assertIn(
            "emitting a completion sentinel before the artifact it closes is a protocol violation",
            self.core,
        )


class TestThread2_RungArtifactExclusivity(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_only_artifact_type_between_label_and_sentinel(self):
        self.assertIn(
            "only valid content before the completion sentinel is the rung\u2019s artifact",
            self.core,
        )

    def test_commentary_between_label_and_sentinel_is_violation(self):
        self.assertIn(
            "prose commentary, planning text, debugging narration",
            self.core,
        )


class TestThread3_ScopeDoesNotExpand(unittest.TestCase):
    """P17: artifacts address only the declared gap — scope does not expand between rungs."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_scope_does_not_expand_between_rungs(self):
        self.assertIn(
            "scope does not expand between rungs",
            self.core,
        )

    def test_beyond_declared_gap_is_derivation_violation(self):
        self.assertIn(
            "addresses behaviors beyond the declared gap is a derivation violation",
            self.core,
        )


class TestThread4_UpwardReturnRequiresPriorCycle(unittest.TestCase):
    """General upward-return principle: comparison gate requires prior cycle to exist."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_upward_return_requires_prior_cycle(self):
        self.assertIn(
            "upward return is valid only when a prior cycle for the current thread exists",
            self.core,
        )

    def test_comparison_gate_requires_prior_artifact(self):
        self.assertIn(
            "comparison gate requires a prior cycle artifact",
            self.core,
        )


class TestThread5_ToolExecutedOpeningObservation(unittest.TestCase):
    """P13 strengthened: opening observation must be tool-executed; intent derivable from it."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_opening_observation_must_be_tool_executed(self):
        self.assertIn(
            "opening observation must be tool-executed",
            self.core,
        )

    def test_intent_derivable_from_tool_output(self):
        self.assertIn(
            "intent declaration must be derivable from that tool-executed output",
            self.core,
        )

    def test_standard_derivation_begins_with_observation(self):
        # Session observation loop precedes every ladder descent
        self.assertIn(
            "Session observation loop",
            self.core,
        )


class TestThread6_ManifestOrdering(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_manifest_is_closing_sentinel_of_ladder_derivation_rung(self):
        self.assertIn(
            "closing sentinel of the ladder derivation rung",
            self.core,
        )

    def test_rung_table_before_manifest_explicit_ordering(self):
        self.assertIn(
            "rung table, then \u2705 Manifest declared",
            self.core,
        )


if __name__ == "__main__":
    unittest.main()
