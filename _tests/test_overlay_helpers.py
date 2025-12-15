import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class DummyCanvas:
        def __init__(self) -> None:
            self.blocks_mouse = False
            self.block_mouse = False
            self.blocks_keyboard = False
            self.block_keyboard = False

    class OverlayHelpersTests(unittest.TestCase):
        def test_mouse_and_keyboard_block_helpers_set_all_known_attrs(self) -> None:
            from talon_user.lib import overlayHelpers

            canvas = DummyCanvas()
            overlayHelpers.set_canvas_block_mouse(canvas)
            overlayHelpers.set_canvas_block_keyboard(canvas)

            self.assertTrue(canvas.blocks_mouse)
            self.assertTrue(canvas.block_mouse)
            self.assertTrue(canvas.blocks_keyboard)
            self.assertTrue(canvas.block_keyboard)

        def test_apply_canvas_blocking_sets_mouse_and_keyboard(self) -> None:
            from talon_user.lib import overlayHelpers

            canvas = DummyCanvas()
            overlayHelpers.apply_canvas_blocking(canvas)

            self.assertTrue(canvas.blocks_mouse)
            self.assertTrue(canvas.block_mouse)
            self.assertTrue(canvas.blocks_keyboard)
            self.assertTrue(canvas.block_keyboard)

        def test_apply_canvas_blocking_noop_on_none(self) -> None:
            from talon_user.lib import overlayHelpers

            # Should not raise when passed None (callers sometimes guard late).
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
