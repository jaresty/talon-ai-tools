"""Thread 1: GROUND_PARTS_MINIMAL core is rewritten — shorter, two new rules added."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt

ORIGINAL_CHARS = 14036
# The two new rules (rung-type constraint + ORB all-criteria) add ~710 chars.
# Redundancy removal should prevent unbounded growth — cap at original + 800.
MAX_CHARS = ORIGINAL_CHARS + 800


class TestGroundRewrite(unittest.TestCase):

    def setUp(self):
        self.prompt = build_ground_prompt(minimal=True)

    def test_prompt_does_not_grow_beyond_additions(self):
        self.assertLess(
            len(self.prompt),
            MAX_CHARS,
            f"Rewritten prompt ({len(self.prompt)} chars) must be < original + 800 ({MAX_CHARS}); "
            f"additions added ~710 chars, so net redundancy removal is required",
        )

    def test_rung_type_constraint_present(self):
        self.assertIn(
            "artifact type",
            self.prompt,
            "Rung-type constraint must state tool output must match the rung's artifact type",
        )

    def test_orb_all_criteria_present(self):
        self.assertTrue(
            "each criterion" in self.prompt or "every criterion" in self.prompt,
            "ORB gate must require demonstrating each/every criterion before Thread N complete",
        )

    def test_rung_type_restatement_removed_1(self):
        self.assertNotIn(
            "tests are never a valid consumer at this rung",
            self.prompt,
            "Restatement of rung-type constraint must be removed; axiom-level statement covers this",
        )

    def test_rung_type_restatement_removed_2(self):
        self.assertNotIn(
            "test pass/fail report is not valid OBS output",
            self.prompt,
            "Restatement of rung-type constraint must be removed; axiom-level statement covers this",
        )


if __name__ == "__main__":
    unittest.main()
