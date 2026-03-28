"""Integration thread required when manifest has 2+ behavioral threads (ADR-0199 Thread 6)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestIntegrationThreadRequired(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_integration_thread_required_for_two_or_more_threads(self):
        self.assertIn(
            "two or more behavioral threads",
            self.prompt,
            "Protocol must require an integration thread when manifest has 2+ behavioral threads",
        )

    def test_integration_thread_must_be_final_entry(self):
        self.assertIn(
            "integration thread",
            self.prompt,
            "Protocol must define an integration thread requirement",
        )

    def test_integration_thread_cannot_complete_before_others(self):
        self.assertIn(
            "integration thread may not be declared complete until all other threads are complete",
            self.prompt,
            "Protocol must block integration thread completion until all other threads close",
        )


if __name__ == "__main__":
    unittest.main()
