import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelState import GPTState

    class GPTStateSuggestionResetTests(unittest.TestCase):
        def test_clear_all_resets_last_suggested_recipes(self):
            GPTState.last_suggested_recipes = [{"name": "n", "recipe": "r"}]

            GPTState.clear_all()

            self.assertEqual(GPTState.last_suggested_recipes, [])
            self.assertEqual(GPTState.last_meta, "")

        def test_reset_all_resets_last_suggested_recipes(self):
            GPTState.last_suggested_recipes = [{"name": "n", "recipe": "r"}]

            GPTState.reset_all()

            self.assertEqual(GPTState.last_suggested_recipes, [])
            self.assertEqual(GPTState.last_meta, "")
else:
    if not TYPE_CHECKING:
        class GPTStateSuggestionResetTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
