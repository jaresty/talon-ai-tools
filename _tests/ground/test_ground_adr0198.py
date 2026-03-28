"""Tests for ADR-0198: Ground prompt minimum-viable refactor.

Asserts that derivable corollary prose has been removed from GROUND_PARTS_MINIMAL["core"]
while axioms and non-derivable rules are preserved.
"""

import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0198P1EnumerationRemoved(unittest.TestCase):
    """Thread 1: p1-tightened — P1 no-other-event enumeration is shortened."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_model_recall_absent_from_p1_enumeration(self):
        """P1 enumeration 'model recall' is derivable from P1 itself and must be removed."""
        self.assertNotIn(
            "model recall",
            self.core,
            "ADR-0198: 'model recall' in P1 enumeration is derivable from P1 and must be absent",
        )

    def test_inference_prediction_anchor_retained(self):
        """'inference, prediction' anchor phrase must remain as the tested residue."""
        self.assertIn(
            "inference, prediction",
            self.core,
            "ADR-0198: 'inference, prediction' anchor must remain after P1 tightening",
        )


class TestADR0198SentinelSentenceRemoved(unittest.TestCase):
    """Thread 2: sentinel-sentence-removed — 'A sentinel is not a summary' restates P1."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_sentinel_summary_sentence_absent(self):
        """'A sentinel is not a summary' restates the why-sentence above it and must be absent."""
        self.assertNotIn(
            "A sentinel is not a summary of what you believe happened",
            self.core,
            "ADR-0198: 'A sentinel is not a summary' is a P1 restatement and must be absent",
        )

    def test_p1_why_sentence_retained(self):
        """Protocol why-sentence must remain as the opening motivation."""
        self.assertIn(
            "This protocol exists because a model\u2019s description of completed work is indistinguishable",
            self.core,
        )


class TestADR0198CharCountReduced(unittest.TestCase):
    """Thread 3: baselines-updated — total char count reflects full corollary removal."""

    def test_char_count_below_pre_adr0198_phase1_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        PRE_ADR0198_BASELINE = 31700  # ADR-0204: harness-error exemption added (~31602 chars)
        self.assertLess(
            current,
            PRE_ADR0198_BASELINE,
            f"ADR-0198: core string ({current} chars) must be shorter than pre-ADR-0198 baseline ({PRE_ADR0198_BASELINE})",
        )

    def test_char_count_below_full_refactor_target(self):
        """Full ADR-0198 refactor: axioms + tables + compact non-derivable escape-route-closers."""
        current = len(GROUND_PARTS_MINIMAL["core"])
        TARGET = 31700  # ADR-0204: harness-error exemption added (~31602 chars)
        self.assertLess(
            current,
            TARGET,
            f"ADR-0198 full refactor: core string ({current} chars) must be < {TARGET} chars",
        )

    def test_core_opens_with_why_sentence(self):
        core = GROUND_PARTS_MINIMAL["core"]
        self.assertTrue(
            core.startswith("This protocol exists"),
            "ADR-0198: core must open with the why-sentence",
        )

    def test_obr_sequence_present(self):
        core = GROUND_PARTS_MINIMAL["core"]
        self.assertIn("OBR rung: (1) criterion re-emission", core)

    def test_thread_sequencing_policy_present(self):
        core = GROUND_PARTS_MINIMAL["core"]
        self.assertIn("Thread N+1", core)

    def test_obr_why_sentence_present(self):
        core = GROUND_PARTS_MINIMAL["core"]
        self.assertIn("a passing test proves the test harness\u2019s assertions pass", core)


if __name__ == "__main__":
    unittest.main()
