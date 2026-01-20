import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import talon_user.lib.modelResponseCanvas as mrc  # type: ignore
    from talon import actions
    from talon_user.lib.requestState import RequestPhase

    class ModelResponseCanvasCloseTests(unittest.TestCase):
        def test_close_clears_fallback_and_hides_canvas(self):
            class DummyCanvas:
                def __init__(self):
                    self.hidden = False

                def hide(self):
                    self.hidden = True

            # Seed state and dummy canvas.
            mrc.ResponseCanvasState.showing = True
            dummy = DummyCanvas()
            mrc._response_canvas = dummy  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-close"
            mrc.GPTState.suppress_response_canvas_close = True

            with patch.object(mrc, "clear_response_fallback") as clear_fallback_mock:
                # Call the action implementation directly to avoid action plumbing.
                mrc.UserActions.model_response_canvas_close()

            clear_fallback_mock.assert_called_with("rid-close")
            self.assertFalse(mrc.ResponseCanvasState.showing)
            # Canvas is released (set to None) after close; check saved reference.
            self.assertTrue(dummy.hidden)
            self.assertFalse(mrc.GPTState.suppress_response_canvas_close)

        def test_toggle_close_clears_fallback(self):
            class DummyCanvas:
                def __init__(self):
                    self.hidden = False

                def hide(self):
                    self.hidden = True

            mrc.ResponseCanvasState.showing = True
            dummy = DummyCanvas()
            mrc._response_canvas = dummy  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-toggle"
            mrc.GPTState.suppress_response_canvas_close = True

            with patch.object(mrc, "clear_response_fallback") as clear_fallback_mock:
                mrc.UserActions.model_response_canvas_toggle()

            clear_fallback_mock.assert_called_with("rid-toggle")
            self.assertFalse(mrc.ResponseCanvasState.showing)
            # Canvas is released (set to None) after close; check saved reference.
            self.assertTrue(dummy.hidden)
            self.assertFalse(mrc.GPTState.suppress_response_canvas_close)

        def test_close_restores_previous_focus(self):
            class DummyWindow:
                def __init__(self):
                    self.focused = False

                def focus(self):
                    self.focused = True

            window = DummyWindow()
            mrc.ResponseCanvasState.showing = False
            mrc.ResponseCanvasState.previous_window = None
            mrc.GPTState.text_to_confirm = "focus"
            mrc._response_canvas = None  # ensure the stub canvas is created
            mrc._response_handlers_registered = False

            class DummyState:
                phase = RequestPhase.IDLE

            with (
                patch.object(mrc.ui, "active_window", return_value=window),
                patch.object(mrc, "close_common_overlays"),
                patch.object(mrc, "_guard_response_canvas", return_value=False),
            ):
                mrc.UserActions.model_response_canvas_open()

            self.assertIs(mrc.ResponseCanvasState.previous_window, window)

            with (
                patch.object(mrc, "clear_response_fallback"),
                patch.object(mrc, "_current_request_state", return_value=DummyState()),
                patch.object(mrc, "_guard_response_canvas", return_value=False),
            ):
                mrc.UserActions.model_response_canvas_close()

            self.assertTrue(window.focused)
            self.assertIsNone(mrc.ResponseCanvasState.previous_window)
            mrc.GPTState.text_to_confirm = ""

        def test_canvas_hide_clears_fallback(self):
            class DummyCanvas:
                def __init__(self):
                    self.handlers = {}

                def register(self, name, fn):
                    self.handlers[name] = fn

                def hide(self):
                    handler = self.handlers.get("hide") or getattr(
                        self, "_on_hide_handler", None
                    )
                    if handler:
                        handler()

            dummy_canvas = DummyCanvas()
            mrc.ResponseCanvasState.showing = True
            mrc._response_canvas = dummy_canvas  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-hide"

            with patch.object(mrc, "clear_response_fallback") as clear_fallback_mock:
                # Register handlers (including hide) and trigger hide.
                mrc._response_handlers_registered = False
                mrc._ensure_response_canvas()
                handler = (
                    dummy_canvas.handlers.get("hide")
                    or getattr(dummy_canvas, "_on_hide_handler", None)
                    or getattr(mrc, "_last_hide_handler", None)
                )
                self.assertIsNotNone(handler)
                handler()

            clear_fallback_mock.assert_called_with("rid-hide")
            self.assertFalse(mrc.ResponseCanvasState.showing)
            self.assertEqual(mrc.ResponseCanvasState.scroll_y, 0.0)
            self.assertFalse(mrc.ResponseCanvasState.meta_expanded)

        def test_hide_handler_restores_previous_focus(self):
            class DummyWindow:
                def __init__(self):
                    self.focused = False

                def focus(self):
                    self.focused = True

            window = DummyWindow()
            mrc.ResponseCanvasState.previous_window = window
            mrc.ResponseCanvasState.showing = True
            mrc._response_canvas = None  # ensure a fresh canvas is created
            mrc._response_handlers_registered = False

            with patch.object(mrc, "clear_response_fallback"):
                mrc._ensure_response_canvas()
                handler = getattr(mrc, "_last_hide_handler", None)
                self.assertIsNotNone(handler)
                handler()

            self.assertTrue(window.focused)
            self.assertIsNone(mrc.ResponseCanvasState.previous_window)

        def test_close_streaming_shows_pill(self):
            class DummyCanvas:
                def __init__(self):
                    self.hidden = False

                def hide(self):
                    self.hidden = True

            mrc.ResponseCanvasState.showing = True
            mrc._response_canvas = DummyCanvas()  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-stream"

            class DummyState:
                phase = RequestPhase.STREAMING

            with (
                patch.object(mrc, "clear_response_fallback"),
                patch.object(mrc, "_guard_response_canvas", return_value=False),
                patch.object(mrc, "_current_request_state", return_value=DummyState()),
                patch("talon_user.lib.pillCanvas.show_pill") as show_pill,
            ):
                mrc.UserActions.model_response_canvas_close()

            show_pill.assert_called_with("Model: streaming…", RequestPhase.STREAMING)

else:

    class ModelResponseCanvasCloseTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
