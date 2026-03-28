"""Tests for ADR-0197: OBR why-sentence — why test output cannot substitute for live-process output."""

import unittest

from lib.groundPrompt import build_ground_prompt


class TestADR0197OBRWhySentence(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_why_sentence_present(self):
        """The prompt must explain why passing tests are not live-process evidence."""
        self.assertIn(
            "a passing test proves the test harness\u2019s assertions pass",
            self.prompt,
        )

    def test_obr_why_sentence_near_obr_type_rule(self):
        """The why-sentence must appear near the OBR type rule."""
        why_pos = self.prompt.find(
            "a passing test proves the test harness\u2019s assertions pass"
        )
        obr_pos = self.prompt.find(
            "OBR-type is produced by a tool call that performs live-process invocation"
        )
        self.assertGreater(why_pos, -1, "OBR why-sentence absent")
        self.assertGreater(obr_pos, -1, "OBR type rule absent")
        self.assertLess(
            abs(why_pos - obr_pos),
            500,
            "OBR why-sentence must be near OBR type rule",
        )


if __name__ == "__main__":
    unittest.main()
