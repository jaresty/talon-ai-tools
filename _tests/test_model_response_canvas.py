import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelResponseCanvas import (
        ResponseCanvasState,
        UserActions,
        _ensure_response_canvas,
        register_response_draw_handler,
        unregister_response_draw_handler,
    )
    from talon_user.lib.modelState import GPTState

    class ModelResponseCanvasTests(unittest.TestCase):
        def setUp(self) -> None:
            ResponseCanvasState.showing = False
            ResponseCanvasState.scroll_y = 0.0

        def test_open_and_close_toggle_canvas(self) -> None:
            GPTState.last_response = "line one\nline two"
            _ensure_response_canvas()

            UserActions.model_response_canvas_open()
            self.assertTrue(ResponseCanvasState.showing)

            UserActions.model_response_canvas_open()
            self.assertFalse(ResponseCanvasState.showing)

        def test_open_without_answer_is_safe(self) -> None:
            GPTState.last_response = ""
            _ensure_response_canvas()

            UserActions.model_response_canvas_open()
            self.assertTrue(ResponseCanvasState.showing)

            UserActions.model_response_canvas_close()
            self.assertFalse(ResponseCanvasState.showing)

        def test_custom_draw_handler_invoked_on_show(self) -> None:
            GPTState.last_response = "test"
            calls: list[object] = []

            def handler(c) -> None:
                calls.append(c)

            register_response_draw_handler(handler)
            try:
                canvas_obj = _ensure_response_canvas()
                canvas_obj.show()
                self.assertGreaterEqual(len(calls), 1)
            finally:
                unregister_response_draw_handler(handler)

        def test_mouse_scroll_adjusts_scroll_offset(self) -> None:
            GPTState.last_response = "line one\nline two\nline three"
            ResponseCanvasState.scroll_y = 0.0
            canvas_obj = _ensure_response_canvas()
            # In the Talon stub, Canvas.from_rect does not set rect; provide
            # a minimal rect so the mouse handler does not early-return.
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type("R", (), {"x": 0, "y": 0, "width": 400, "height": 300})()
            # Access the registered mouse handler from the stub canvas.
            callbacks = getattr(canvas_obj, "_callbacks", {})
            mouse_cbs = callbacks.get("mouse") or []
            if not mouse_cbs:
                self.skipTest("Canvas stub does not expose mouse callbacks")
            mouse_cb = mouse_cbs[0]

            class _Evt:
                def __init__(self, dy: float):
                    self.event = "mouse_scroll"
                    self.dy = dy
                    # Minimal pos/gpos for handler hit-testing.
                    self.pos = type("P", (), {"x": 10, "y": 50})()
                    self.gpos = type("P", (), {"x": 10, "y": 50})()
                    self.button = None

            # Simulate scroll down.
            mouse_cb(_Evt(-1.0))
            self.assertGreater(ResponseCanvasState.scroll_y, 0.0)

            # Simulate scroll up enough to clamp back to zero.
            mouse_cb(_Evt(100.0))
            self.assertEqual(ResponseCanvasState.scroll_y, 0.0)

else:
    if not TYPE_CHECKING:
        class ModelResponseCanvasTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
