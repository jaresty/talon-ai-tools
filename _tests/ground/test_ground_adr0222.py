"""Tests for ADR-0222: pre-entry enforcement — Ground entered must precede all artifacts.

Run 56 showed the model producing an entire implementation without emitting any
sentinel. P14 blocks gates once inside the protocol but nothing blocked artifact
production before Ground entered. This ADR closes that gap.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_PreEntryEnforcement(unittest.TestCase):
    """✅ Ground entered must be the first emitted content; preceding content voids the session."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_ground_entered_must_be_first_content(self):
        self.assertIn(
            "\u2705 Ground entered must be the first emitted content",
            self.core,
        )

    def test_preceding_content_voids_session(self):
        self.assertIn(
            "any artifact, reasoning, or content of any type produced before \u2705 Ground entered is a pre-entry violation",
            self.core,
        )

    def test_pre_entry_violation_voids_all_work(self):
        self.assertIn(
            "it voids the sentinel and all work that follows in that response",
            self.core,
        )


class TestThread1_SentinelGateStrengthened(unittest.TestCase):
    """ground_entered sentinel gate annotation must state the pre-entry constraint."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_gate_says_no_content_may_precede(self):
        self.assertIn(
            "no artifact, code, prose, or reasoning may precede this sentinel",
            self.prompt,
        )

    def test_gate_says_preceding_content_voids_session(self):
        self.assertIn(
            "preceding content voids the session",
            self.prompt,
        )


class TestADR0222CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            15_500,
            f"ADR-0222: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
