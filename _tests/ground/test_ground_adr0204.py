"""ADR-0204: harness error does not trigger the Thread N complete block."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestHarnessErrorNotABlock(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_harness_error_exempt_from_thread_complete_block(self):
        self.assertIn(
            "this block does not apply when the most recent exec_observed is a harness error",
            self.prompt,
            "Protocol must exempt harness errors from the Thread N complete block rule",
        )

    def test_harness_error_routes_to_repair_not_block(self):
        self.assertIn(
            "repair the harness",
            self.prompt,
            "Protocol must route harness errors to harness repair, not treat them as permanent blocks",
        )


if __name__ == "__main__":
    unittest.main()
