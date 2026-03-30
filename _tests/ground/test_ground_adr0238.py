"""Tests for ADR-0238: rung label must be emitted before any artifact content.

T1 rung-label-before-artifact: emitting artifact content for a rung before
   its label has been emitted is a protocol violation that voids that artifact
   and all rungs below it.
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestThread1_RungLabelBeforeArtifact(unittest.TestCase):
    """Rung label must precede artifact content."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_rung_label_must_precede_artifact(self):
        self.assertIn(
            "rung label must be emitted before any artifact content",
            self.core,
        )

    def test_artifact_without_label_is_violation(self):
        self.assertIn(
            "producing artifact content before the rung label is a protocol violation",
            self.core,
        )

    def test_violation_voids_artifact_and_below(self):
        self.assertIn(
            "voids that artifact and all rungs below it",
            self.core,
        )

    def test_propagated_to_prompt(self):
        self.assertIn(
            "rung label must be emitted before any artifact content",
            build_ground_prompt(),
        )


if __name__ == "__main__":
    unittest.main()
