"""Criteria rung must prohibit formal notation content before the notation rung label (ADR-0200)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestCriteriaBoundary(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_notation_content_requires_rung_label_first(self):
        # After the criterion is written, no notation content may appear
        # until the formal notation rung label has been emitted.
        self.assertIn(
            "no formal notation content may appear until the formal notation rung label has been emitted",
            self.prompt,
            "Protocol must prohibit notation content before the notation rung label",
        )

    def test_criteria_rung_stops_after_criterion(self):
        # The criteria rung artifact is exactly the criterion — nothing beyond it.
        self.assertIn(
            "emitting notation content before the formal notation rung label is a protocol violation",
            self.prompt,
            "Protocol must explicitly call this a protocol violation",
        )


if __name__ == "__main__":
    unittest.main()
