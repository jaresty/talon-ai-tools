import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.helpUI import apply_scroll_delta, clamp_scroll, scroll_fraction

    class HelpUITests(unittest.TestCase):
        def test_clamp_scroll_bounds(self) -> None:
            self.assertEqual(clamp_scroll(-10.0, 100.0), 0.0)
            self.assertEqual(clamp_scroll(150.0, 100.0), 100.0)
            self.assertEqual(clamp_scroll(50.0, 100.0), 50.0)

        def test_apply_scroll_delta_clamps(self) -> None:
            self.assertEqual(apply_scroll_delta(90.0, 20.0, 100.0), 100.0)
            self.assertEqual(apply_scroll_delta(10.0, -50.0, 100.0), 0.0)

        def test_scroll_fraction_handles_zero_max(self) -> None:
            self.assertEqual(scroll_fraction(10.0, 0.0), 0.0)
            self.assertEqual(scroll_fraction(50.0, 100.0), 0.5)

else:
    if not TYPE_CHECKING:

        class HelpUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
