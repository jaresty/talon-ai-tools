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

    class ModelResponseCanvasCloseTests(unittest.TestCase):
        def test_close_clears_fallback_and_hides_canvas(self):
            class DummyCanvas:
                def __init__(self):
                    self.hidden = False

                def hide(self):
                    self.hidden = True

            # Seed state and dummy canvas.
            mrc.ResponseCanvasState.showing = True
            mrc._response_canvas = DummyCanvas()  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-close"

            with patch.object(
                mrc, "clear_response_fallback"
            ) as clear_fallback_mock:
                # Call the action implementation directly to avoid action plumbing.
                mrc.UserActions.model_response_canvas_close()

            clear_fallback_mock.assert_called_with("rid-close")
            self.assertFalse(mrc.ResponseCanvasState.showing)
            self.assertTrue(getattr(mrc._response_canvas, "hidden", False))

        def test_toggle_close_clears_fallback(self):
            class DummyCanvas:
                def __init__(self):
                    self.hidden = False

                def hide(self):
                    self.hidden = True

            mrc.ResponseCanvasState.showing = True
            mrc._response_canvas = DummyCanvas()  # type: ignore[attr-defined]
            mrc.GPTState.last_request_id = "rid-toggle"

            with patch.object(
                mrc, "clear_response_fallback"
            ) as clear_fallback_mock:
                mrc.UserActions.model_response_canvas_toggle()

            clear_fallback_mock.assert_called_with("rid-toggle")
            self.assertFalse(mrc.ResponseCanvasState.showing)
            self.assertTrue(getattr(mrc._response_canvas, "hidden", False))

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

            with patch.object(
                mrc, "clear_response_fallback"
            ) as clear_fallback_mock:
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
else:
    class ModelResponseCanvasCloseTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
