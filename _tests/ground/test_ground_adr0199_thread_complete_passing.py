"""Thread N complete requires zero failures for declared criterion in OBR step-5 run (ADR-0199 Thread 2)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestThreadCompletePassingRun(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_thread_complete_requires_zero_failures_for_criterion(self):
        # Acknowledging failing tests does not permit Thread N complete.
        # The step-5 run must show zero failures for the declared criterion.
        self.assertIn(
            "zero failures for the criterion declared in this thread",
            self.prompt,
            "Protocol must require zero failures for the declared criterion before Thread N complete",
        )

    def test_acknowledging_failures_does_not_permit_thread_complete(self):
        # The existing "must be explicitly acknowledged" rule is a floor, not a ceiling.
        self.assertIn(
            "does not permit",
            self.prompt,
            "Protocol must state that acknowledging failures does not permit Thread N complete",
        )


if __name__ == "__main__":
    unittest.main()
