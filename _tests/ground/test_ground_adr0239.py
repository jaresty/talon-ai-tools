"""Tests for ADR-0239: rung label must be re-emitted on upward return.

T1 rung-label-re-emission-on-upward-return: when returning upward to a rung,
   the rung label must be re-emitted before any revised artifact content;
   re-entering a rung without re-emitting its label is a protocol violation
   that voids the revised artifact and all rungs below it.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_RungLabelReEmissionOnUpwardReturn(unittest.TestCase):
    """Rung label must be re-emitted when returning upward to a rung."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_rung_label_re_emitted_on_upward_return(self):
        self.assertIn(
            "rung label must be re-emitted before any revised artifact content",
            self.core,
        )

    def test_re_entry_without_label_is_violation(self):
        self.assertIn(
            "re-entering a rung without re-emitting its label is a protocol violation",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "rung label must be re-emitted before any revised artifact content",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
