"""Each rung has a fixed content type; wrong-type content before label = A2 violation (ADR-0201 Thread 1)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestRungContentTypeDiscipline(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_each_rung_has_fixed_content_type(self):
        self.assertIn(
            "each rung label opens a content-type context",
            self.prompt,
            "Protocol must state that each rung label opens a fixed content-type context",
        )

    def test_wrong_type_content_is_a2_violation(self):
        self.assertIn(
            "type violation under A2",
            self.prompt,
            "Protocol must classify wrong-type content as a type violation under A2",
        )

    def test_eventually_follows_does_not_satisfy(self):
        self.assertIn(
            "eventually follows",
            self.prompt,
            "Protocol must state that the correct label eventually following does not satisfy the gate",
        )


if __name__ == "__main__":
    unittest.main()
