"""Criteria rung content-type discipline: notation content requires notation rung label first (ADR-0200/0201)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestCriteriaBoundary(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_notation_content_requires_rung_label_first(self):
        # Each rung label opens a content-type context; notation-type content
        # belongs to the formal notation rung, not the criteria rung.
        self.assertIn(
            "each rung label opens a content-type context",
            self.prompt,
            "Protocol must state that each rung label opens a content-type context",
        )

    def test_criteria_rung_stops_after_criterion(self):
        # Emitting content of a different rung's type before its label is an A2 violation.
        self.assertIn(
            "type violation under A2",
            self.prompt,
            "Protocol must classify wrong-type content as a type violation under A2",
        )


if __name__ == "__main__":
    unittest.main()
