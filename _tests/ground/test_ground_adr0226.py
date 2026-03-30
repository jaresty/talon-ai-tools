"""Tests for ADR-0226: meta-loop observation principle; P5 verification artifact; Ground complete sentinel.

T1 observation-is-meta-loop: observation is the session control mechanism, not a ladder rung.
T2 failing-observation-in-ev: P5 — running automation immediately after writing it is part of the
   verification artifact; EI derives from EV and sees both test file and failure output (P17).
T3 ground-complete-sentinel: ✅ Ground complete emitted when meta-observation finds no remaining gap.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, SENTINEL_TEMPLATES, build_ground_prompt


class TestThread1_ObservationIsMetaLoop(unittest.TestCase):
    """Observation is the session control mechanism, not a ladder rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_session_observation_loop_described(self):
        self.assertIn(
            "Session observation loop",
            self.core,
        )

    def test_observation_not_a_rung(self):
        self.assertIn(
            "this observation is not a rung in the derived ladder",
            self.core,
        )

    def test_no_gap_emits_ground_complete(self):
        self.assertIn(
            "if no gap remains, emit \u2705 Ground complete",
            self.core,
        )

    def test_obr_bookends_removed(self):
        self.assertNotIn(
            "Each cycle begins with an observed-running-behavior rung",
            self.core,
        )

    def test_obr_bookends_end_removed(self):
        self.assertNotIn(
            "each cycle ends with an observed-running-behavior rung",
            self.core,
        )


class TestThread2_FailingObservationInEV(unittest.TestCase):
    """P5: failing-state observation is part of the verification artifact, not a separate rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_failing_observation_part_of_verification_artifact(self):
        self.assertIn(
            "the observation of failing state is produced by running the automation immediately after writing it",
            self.core,
        )

    def test_failure_output_part_of_artifact_not_separate_rung(self):
        self.assertIn(
            "it is part of the verification artifact, not a separate rung",
            self.core,
        )

    def test_p8_argument_for_merge(self):
        self.assertIn(
            "a reviewer cannot determine from the test file alone what the implementation must do",
            self.core,
        )


class TestThread3_GroundCompleteSentinel(unittest.TestCase):
    """✅ Ground complete sentinel exists with correct gate."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_ground_complete_in_templates(self):
        self.assertIn("ground_complete", SENTINEL_TEMPLATES)

    def test_ground_complete_format_string(self):
        self.assertIn("\u2705 Ground complete \u2014 intent achieved", self.prompt)

    def test_ground_complete_gate(self):
        self.assertIn(
            "no gap between observed running behavior and declared intent",
            self.prompt,
        )


class TestADR0226CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            19_000,
            f"ADR-0226: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
