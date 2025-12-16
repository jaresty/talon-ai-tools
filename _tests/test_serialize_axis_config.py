import unittest
from lib.axisCatalog import serialize_axis_config


class SerializeAxisConfigTests(unittest.TestCase):
    def test_includes_static_prompt_sections_by_default(self):
        payload = serialize_axis_config()
        self.assertIn("axes", payload)
        self.assertIn("axis_list_tokens", payload)
        self.assertIn("static_prompts", payload)
        self.assertIn("static_prompt_descriptions", payload)
        self.assertIn("static_prompt_profiles", payload)
        self.assertTrue(payload["static_prompts"].get("profiled"), "static_prompts.profiled should not be empty")


if __name__ == "__main__":
    unittest.main()
