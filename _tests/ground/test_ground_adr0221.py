"""Tests for ADR-0221: ADR-0217 compliance — remove rung abbreviations from sentinel gates and P15.

Sentinel gates previously referenced derived-rung abbreviations (VRO, EI, OBR) that are
not guaranteed to appear in every derived rung table. Replaced with full artifact-type
descriptions from the standard derivation example. P15 referenced "prose rung" by name;
replaced with sentinel reference (✅ Ground entered).
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_SentinelGatesNoAbbreviations(unittest.TestCase):
    """Sentinel gates must not use rung abbreviations (VRO, EI, OBR)."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_no_vro_abbreviation(self):
        self.assertNotIn("VRO rung", self.prompt)

    def test_no_ei_abbreviation(self):
        self.assertNotIn("EI rung", self.prompt)

    def test_no_obr_abbreviation(self):
        self.assertNotIn("OBR rung", self.prompt)
        self.assertNotIn("OBR exec_observed", self.prompt)
        self.assertNotIn("OBR tool call", self.prompt)

    def test_no_validation_run_observation_rung_name(self):
        self.assertNotIn("validation-run-observation rung", self.prompt)

    def test_hard_stop_gate_uses_behavioral_description(self):
        self.assertIn(
            "exec_observed showing test suite failure",
            self.prompt,
        )

    def test_impl_gate_uses_behavioral_description(self):
        self.assertIn(
            "rung whose artifact type is executable implementation",
            self.prompt,
        )

    def test_thread_complete_gate_uses_meta_observation(self):
        self.assertIn(
            "meta exec_observed after executable implementation",
            self.prompt,
        )


class TestThread2_P15NoProseRungName(unittest.TestCase):
    """P15 must not reference 'prose rung' — cycle identity expressed via sentinel."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_no_prose_rung_emission(self):
        self.assertNotIn("prose rung emission", self.core)

    def test_no_prose_re_emission(self):
        self.assertNotIn("prose re-emission", self.core)

    def test_cycle_opens_on_ground_entered_sentinel(self):
        self.assertIn(
            "cycle opens when \u2705 Ground entered is emitted",
            self.core,
        )


class TestADR0221CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            20_000,
            f"ADR-0221: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
