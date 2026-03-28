"""Old ADR-0200 prohibition phrases must be absent — subsumed by positive type rule (ADR-0201 Thread 2)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestProhibitionAbsent(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_old_prohibition_phrase_absent(self):
        self.assertNotIn(
            "no formal notation content may appear until the formal notation rung label has been emitted",
            self.prompt,
            "Old ADR-0200 prohibition phrase must be absent — subsumed by positive type-discipline rule",
        )

    def test_old_violation_phrase_absent(self):
        self.assertNotIn(
            "emitting notation content before the formal notation rung label is a protocol violation",
            self.prompt,
            "Old ADR-0200 violation phrase must be absent — subsumed by A2 type violation rule",
        )


if __name__ == "__main__":
    unittest.main()
