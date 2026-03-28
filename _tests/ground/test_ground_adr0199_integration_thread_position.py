"""Integration thread rule must appear after the manifest lifecycle block (ADR-0199 Thread 6 position)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestIntegrationThreadPosition(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_integration_thread_rule_after_manifest_lifecycle(self):
        lifecycle_idx = self.prompt.find(
            "Completed threads are closed and may not be re-opened by a revision"
        )
        integration_idx = self.prompt.find("two or more behavioral threads")
        self.assertGreater(
            integration_idx,
            lifecycle_idx,
            "Integration thread rule must appear after the manifest lifecycle rule",
        )

    def test_integration_thread_rule_before_criteria_rung_rules(self):
        criteria_idx = self.prompt.find(
            "The gap names a specific behavior currently absent or wrong"
        )
        integration_idx = self.prompt.find("two or more behavioral threads")
        self.assertLess(
            integration_idx,
            criteria_idx,
            "Integration thread rule must appear before the criteria rung rules",
        )


if __name__ == "__main__":
    unittest.main()
