import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelPatternGUI import (
        PATTERNS,
        Rect,
        _max_scroll_offset,
        _scroll_pattern_list,
    )

    class ModelPatternGUIScrollTests(unittest.TestCase):
        def test_max_scroll_offset_respects_visible_rows(self) -> None:
            rect = Rect(0, 0, 720, 600)
            patterns = [p for p in PATTERNS if p.domain == "coding"]

            max_offset = _max_scroll_offset(rect, patterns)

            self.assertGreaterEqual(max_offset, 0)
            self.assertLessEqual(max_offset, max(len(patterns) - 1, 0))

        def test_scroll_pattern_list_clamps_between_zero_and_max(self) -> None:
            rect = Rect(0, 0, 720, 600)
            patterns = [p for p in PATTERNS if p.domain == "coding"]
            max_offset = _max_scroll_offset(rect, patterns)

            below_zero = _scroll_pattern_list(-5.0, -1, rect, patterns)
            above_max = _scroll_pattern_list(max_offset + 5.0, 10, rect, patterns)

            self.assertEqual(below_zero, 0.0)
            self.assertEqual(above_max, float(max_offset))

else:
    if not TYPE_CHECKING:

        class ModelPatternGUIScrollTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
