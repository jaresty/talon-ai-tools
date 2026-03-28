"""Meta-test: ADR-0200 test file must assert the new positive framing, not old prohibition phrases."""
import unittest
import sys
import ast
sys.path.insert(0, '.')


class TestADR0200TestFileAssertions(unittest.TestCase):
    def setUp(self):
        with open("_tests/ground/test_ground_adr0200_criteria_boundary.py") as f:
            self.source = f.read()

    def test_adr0200_does_not_assert_old_prohibition(self):
        self.assertNotIn(
            "no formal notation content may appear until the formal notation rung label has been emitted",
            self.source,
            "ADR-0200 test must not assert old prohibition phrase — use positive framing",
        )

    def test_adr0200_asserts_new_positive_framing(self):
        self.assertIn(
            "each rung label opens a content-type context",
            self.source,
            "ADR-0200 test must assert new positive type-discipline phrase",
        )


if __name__ == "__main__":
    unittest.main()
