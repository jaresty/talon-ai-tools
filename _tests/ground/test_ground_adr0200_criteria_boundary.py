"""Criteria rung content-type discipline: notation content requires notation rung label first (ADR-0200/0201)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestCriteriaBoundary(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_notation_content_requires_rung_label_first_prose_absent(self):
        # ADR-0215: A2 type-context prose at criteria rung removed (derivable from gate formula)
        self.assertNotIn(
            "each rung label opens a content-type context",
            self.prompt,
            "ADR-0215: per-rung A2 restatement must be absent",
        )

    def test_criteria_rung_stops_after_criterion_prose_absent(self):
        # ADR-0215: "type violation under A2" per-rung restatement removed
        self.assertNotIn(
            "type violation under A2",
            self.prompt,
            "ADR-0215: per-rung A2 type violation restatement must be absent",
        )


if __name__ == "__main__":
    unittest.main()
