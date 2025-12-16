import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


class OverlayBlockingTests(unittest.TestCase):
    if bootstrap is None and not TYPE_CHECKING:

        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
    else:

        class DummyCanvas:
            def __init__(self) -> None:
                self.blocks_mouse = False
                self.block_mouse = False
                self.blocks_keyboard = False
                self.block_keyboard = False

        def test_mouse_and_keyboard_block_helpers_set_all_known_attrs(self) -> None:
            from talon_user.lib import overlayHelpers

            canvas = self.DummyCanvas()
            overlayHelpers.set_canvas_block_mouse(canvas)
            overlayHelpers.set_canvas_block_keyboard(canvas)

            self.assertTrue(canvas.blocks_mouse)
            self.assertTrue(canvas.block_mouse)
            self.assertTrue(canvas.blocks_keyboard)
            self.assertTrue(canvas.block_keyboard)

        def test_apply_canvas_blocking_sets_mouse_and_keyboard(self) -> None:
            from talon_user.lib import overlayHelpers

            canvas = self.DummyCanvas()
            overlayHelpers.apply_canvas_blocking(canvas)

            self.assertTrue(canvas.blocks_mouse)
            self.assertTrue(canvas.block_mouse)
            self.assertTrue(canvas.blocks_keyboard)
            self.assertTrue(canvas.block_keyboard)

        def test_apply_canvas_blocking_noop_on_none(self) -> None:
            from talon_user.lib import overlayHelpers

            overlayHelpers.apply_canvas_blocking(None)

        def test_apply_canvas_blocking_noop_on_missing_attrs(self) -> None:
            from talon_user.lib import overlayHelpers

            class MinimalCanvas:
                """Canvas stub without mouse/keyboard attrs."""

                pass

            canvas = MinimalCanvas()
            overlayHelpers.apply_canvas_blocking(canvas)
            self.assertFalse(hasattr(canvas, "blocks_mouse"))
            self.assertFalse(hasattr(canvas, "block_mouse"))
            self.assertFalse(hasattr(canvas, "blocks_keyboard"))
            self.assertFalse(hasattr(canvas, "block_keyboard"))

        def test_scroll_helpers_match_help_ui(self) -> None:
            from talon_user.lib import overlayHelpers, helpUI

            self.assertEqual(overlayHelpers.clamp_scroll(5, 10), helpUI.clamp_scroll(5, 10))
            self.assertEqual(
                overlayHelpers.apply_scroll_delta(0, 5, 10), helpUI.apply_scroll_delta(0, 5, 10)
            )
            self.assertEqual(overlayHelpers.scroll_fraction(5, 10), helpUI.scroll_fraction(5, 10))


if bootstrap is not None:
    from talon_user.lib import overlayHelpers, helpUI

    class OverlayScrollTests(unittest.TestCase):
        def test_clamp_scroll_matches_help_ui(self):
            for value, max_scroll in (
                (-5, 10),
                (0, 0),
                (5, 10),
                (15, 10),
            ):
                self.assertEqual(
                    overlayHelpers.clamp_scroll(value, max_scroll),
                    helpUI.clamp_scroll(value, max_scroll),
                )

        def test_apply_scroll_delta_matches_help_ui(self):
            cases = [
                (0, 5, 10),
                (9, 5, 10),
                (10, -3, 10),
            ]
            for value, delta, max_scroll in cases:
                self.assertEqual(
                    overlayHelpers.apply_scroll_delta(value, delta, max_scroll),
                    helpUI.apply_scroll_delta(value, delta, max_scroll),
                )

        def test_scroll_fraction_matches_help_ui(self):
            for value, max_scroll in (
                (0, 0),
                (0, 10),
                (5, 10),
                (15, 10),
            ):
                self.assertEqual(
                    overlayHelpers.scroll_fraction(value, max_scroll),
                    helpUI.scroll_fraction(value, max_scroll),
                )
else:
    if not TYPE_CHECKING:

        class OverlayScrollTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
