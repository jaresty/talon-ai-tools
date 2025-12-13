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

        def test_reset_all_preserves_axis_keys(self):
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor", "xp"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            }

            GPTState.reset_all()

            for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
                self.assertIn(axis, GPTState.last_axes)
                self.assertEqual(GPTState.last_axes[axis], [])
else:
    if not TYPE_CHECKING:
        class GPTStateSuggestionResetTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
