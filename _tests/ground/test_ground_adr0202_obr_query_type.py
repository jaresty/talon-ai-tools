"""OBR query step must be HTTP request or browser navigation, not test runner (ADR-0202)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRQueryType(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_valid_query_is_http_or_browser(self):
        self.assertIn(
            "HTTP request or browser navigation",
            self.prompt,
            "Protocol must specify that a valid OBR query is an HTTP request or browser navigation",
        )

    def test_test_runner_is_not_valid_query(self):
        self.assertIn(
            "test runner invocation is not a valid query",
            self.prompt,
            "Protocol must explicitly state that a test runner is not a valid OBR query",
        )

    def test_test_runner_after_dev_server_still_vro(self):
        self.assertIn(
            "test runner after dev server start",
            self.prompt,
            "Protocol must address the specific case of test runner after dev server start",
        )


if __name__ == "__main__":
    unittest.main()
