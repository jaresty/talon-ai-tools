import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisJoin import axis_join

    class AxisJoinHelperTests(unittest.TestCase):
        def test_axis_join_prefers_list_tokens(self) -> None:
            axes_tokens = {"scope": ["narrow", "focus"]}
            joined = axis_join(axes_tokens, "scope", "fallback")
            self.assertEqual(joined, "narrow focus")

        def test_axis_join_uses_fallback_for_empty_list(self) -> None:
            axes_tokens = {"scope": []}
            joined = axis_join(axes_tokens, "scope", "fallback")
            self.assertEqual(joined, "fallback")

        def test_axis_join_passthroughs_string_values(self) -> None:
            axes_tokens = {"completeness": "full"}
            joined = axis_join(axes_tokens, "completeness", "gist")
            self.assertEqual(joined, "full")

        def test_axis_join_handles_missing_axes(self) -> None:
            joined = axis_join(None, "form", "plain")
            self.assertEqual(joined, "plain")

else:
    if not TYPE_CHECKING:

        class AxisJoinHelperTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
