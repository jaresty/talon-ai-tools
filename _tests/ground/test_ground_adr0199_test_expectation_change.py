"""Test expectation change without prose re-emission is a protocol violation (ADR-0199 Thread 3)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestExpectationChangeRequiresProseReemission(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_test_expectation_update_matching_impl_requires_prose_reemission(self):
        # Changing a test assertion to match implementation output is a criterion change.
        self.assertIn(
            "test assertion is changed to match implementation output",
            self.prompt,
            "Protocol must identify test assertion updates matching implementation output as criterion changes",
        )

    def test_criterion_change_requires_prose_reemission(self):
        # A criterion change requires returning to prose, not just editing the test.
        self.assertIn(
            "return to the prose rung",
            self.prompt,
            "Protocol must require prose re-emission when a test expectation constitutes a criterion change",
        )

    def test_undeclared_test_assertion_change_is_protocol_violation(self):
        # Updating a test without prose re-emission in this case is a protocol violation.
        self.assertIn(
            "test expectation update made without re-emitting prose is a protocol violation",
            self.prompt,
            "Protocol must explicitly forbid undeclared test assertion changes",
        )


if __name__ == "__main__":
    unittest.main()
