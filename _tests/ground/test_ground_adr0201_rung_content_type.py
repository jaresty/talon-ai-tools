"""Each rung has a fixed content type; wrong-type content before label = A2 violation (ADR-0201 Thread 1)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestRungContentTypeDiscipline(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_each_rung_has_fixed_content_type_prose_absent(self):
        # ADR-0215: per-rung A2 restatement removed (gate formula states A2 globally)
        self.assertNotIn(
            "each rung label opens a content-type context",
            self.prompt,
            "ADR-0215: per-rung content-type context prose must be absent",
        )

    def test_wrong_type_content_prose_absent(self):
        # ADR-0215: "type violation under A2" per-rung restatement removed
        self.assertNotIn(
            "type violation under A2",
            self.prompt,
            "ADR-0215: per-rung A2 type violation restatement must be absent",
        )

    def test_eventually_follows_prose_absent(self):
        # ADR-0215: "eventually follows" clause removed with A2 restatement
        self.assertNotIn(
            "eventually follows",
            self.prompt,
            "ADR-0215: 'eventually follows' clause must be absent",
        )


if __name__ == "__main__":
    unittest.main()
