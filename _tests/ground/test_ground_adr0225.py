"""Tests for ADR-0225 (revised by ADR-0226): observation is the session control mechanism, not a rung.

The OBR-bookends approach (each cycle begins/ends with an OBR rung) was superseded.
Observation is outside the derived ladder — it is the meta-loop's control mechanism.
The ladder handles only the declared gap; observation determines whether to descend or complete.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_ObservationOutsideLadder(unittest.TestCase):
    """Observation is not a rung — it is the session meta-loop control mechanism."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]
        self.prompt = build_ground_prompt()

    def test_observation_not_a_rung(self):
        self.assertIn(
            "this observation is not a rung in the derived ladder",
            self.core,
        )

    def test_no_obr_bookends(self):
        self.assertNotIn(
            "cycle begins with an observed-running-behavior rung",
            self.core,
        )
        self.assertNotIn(
            "each cycle ends with an observed-running-behavior rung",
            self.core,
        )

    def test_thread_complete_gate_uses_meta_observation(self):
        self.assertIn(
            "meta exec_observed after executable implementation",
            self.prompt,
        )


class TestADR0225CharCount(unittest.TestCase):
    def test_char_count_below_ceiling(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertLess(
            current,
            20_000,
            f"ADR-0225: core string ({current} chars) unexpectedly large",
        )


if __name__ == "__main__":
    unittest.main()
