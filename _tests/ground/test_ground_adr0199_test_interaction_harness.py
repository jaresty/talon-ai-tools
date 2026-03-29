"""Test-interaction failure classified as harness error, not behavioral failure (ADR-0199 Thread 5)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestInteractionHarnessClass(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_test_interaction_failure_is_harness_error(self):
        self.assertIn(
            "test-interaction-failure",
            self.prompt,
            "Protocol must classify test-interaction failure as a harness error class",
        )

    def test_test_interaction_failure_blocks_gap_sentinel(self):
        self.assertIn(
            "pointer-events: none",
            self.prompt,
            "Protocol must name pointer-events: none as an example of test-interaction failure",
        )

    def test_test_interaction_failure_valid_next_token(self):
        # ADR-0215: compact routing table routes test-interaction-failure → EV repair
        self.assertIn(
            "EV repair",
            self.prompt,
            "Protocol must route test-interaction-failure to EV repair",
        )


if __name__ == "__main__":
    unittest.main()
