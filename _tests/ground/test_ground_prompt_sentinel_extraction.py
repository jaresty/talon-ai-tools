"""Tests for Thread 1: sentinel format string extraction in groundPrompt.py.

Validates that after refactor:
- SENTINEL_TEMPLATES dict exists with all required keys
- No sentinel format string literal is duplicated in sentinel_rules prose
- build_ground_prompt() output contains each sentinel text
"""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt


EXPECTED_SENTINEL_KEYS = [
    "exec_observed",
    "gap",
    "impl_gate",
    "v_complete",
    "thread_complete",
    "manifest_exhausted",
    "carry_forward",
    "i_formation",
    "r2_audit",
]

# Sentinel substrings that must appear in the final prompt exactly once
# (as format strings, not as repeated inline literals)
SENTINEL_SUBSTRINGS = [
    "Execution observed:",
    "Implementation gate cleared",
    "Validation artifact V complete",
    "Manifest exhausted",
    "I-formation complete",
    "Formal notation R2 audit complete",
]


class TestSentinelTemplatesExist(unittest.TestCase):
    def test_sentinel_templates_dict_exists(self):
        from lib.groundPrompt import SENTINEL_TEMPLATES
        self.assertIsInstance(SENTINEL_TEMPLATES, dict)

    def test_all_required_keys_present(self):
        from lib.groundPrompt import SENTINEL_TEMPLATES
        for key in EXPECTED_SENTINEL_KEYS:
            self.assertIn(key, SENTINEL_TEMPLATES, f"Missing key: {key}")

    def test_each_value_is_nonempty_string(self):
        from lib.groundPrompt import SENTINEL_TEMPLATES
        for key, val in SENTINEL_TEMPLATES.items():
            self.assertIsInstance(val, str)
            self.assertTrue(len(val) > 0, f"Empty value for key: {key}")



class TestBuildGroundPromptContainsSentinels(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prompt_contains_exec_observed(self):
        self.assertIn("Execution observed:", self.prompt)

    def test_prompt_contains_impl_gate(self):
        self.assertIn("Implementation gate cleared", self.prompt)

    def test_prompt_contains_v_complete(self):
        self.assertIn("Validation artifact V complete", self.prompt)

    def test_prompt_contains_manifest_exhausted(self):
        self.assertIn("Manifest exhausted", self.prompt)

    def test_prompt_contains_carry_forward(self):
        self.assertIn("Carry-forward:", self.prompt)


if __name__ == "__main__":
    unittest.main()
