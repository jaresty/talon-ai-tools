import unittest
from typing import Any
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

canvas_module: Any = None
ResponseCanvasState: Any = None
UserActions: Any = None

if bootstrap is not None:
    from talon_user.lib import modelResponseCanvas as canvas_module
    from talon_user.lib.modelResponseCanvas import ResponseCanvasState, UserActions
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.requestState import RequestPhase, RequestState


class ModelResponseCanvasGuardTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None or ResponseCanvasState is None:
            self.skipTest("Talon runtime not available")
        ResponseCanvasState.showing = False
        ResponseCanvasState.scroll_y = 0.0
        ResponseCanvasState.meta_expanded = False

    def test_response_canvas_actions_respect_in_flight_guard(self):
        with (
            patch.object(
                canvas_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(canvas_module, "_ensure_response_canvas") as ensure,
        ):
            UserActions.model_response_canvas_open()
        ensure.assert_not_called()
        self.assertFalse(ResponseCanvasState.showing)

    def test_reset_meta_signature_initialises_attribute(self):
        if canvas_module is None:
            self.skipTest("Talon runtime not available")
        original_present = hasattr(canvas_module, "_last_meta_signature")
        original_value = getattr(canvas_module, "_last_meta_signature", None)
        if original_present:
            delattr(canvas_module, "_last_meta_signature")
        try:
            canvas_module._reset_meta_if_new_signature({}, {}, "req-init")
            self.assertTrue(hasattr(canvas_module, "_last_meta_signature"))
        finally:
            if original_present:
                setattr(canvas_module, "_last_meta_signature", original_value)
            elif hasattr(canvas_module, "_last_meta_signature"):
                delattr(canvas_module, "_last_meta_signature")

    def test_reject_if_request_in_flight_delegates_to_surface_guard(self):
        state = RequestState()
        captured_kwargs: dict[str, Any] = {}

        def fake_guard(**kwargs):
            captured_kwargs.update(kwargs)
            state_getter = kwargs.get("state_getter")
            self.assertTrue(callable(state_getter))
            self.assertIs(state_getter(), state)
            return True

        with (
            patch.object(canvas_module, "_current_request_state", return_value=state),
            patch(
                "talon_user.lib.modelResponseCanvas.guard_surface_request",
                side_effect=fake_guard,
            ) as guard,
        ):
            self.assertTrue(canvas_module._reject_if_request_in_flight())

        guard.assert_called_once()
        self.assertEqual(captured_kwargs["surface"], "response_canvas")
        self.assertEqual(captured_kwargs["source"], "modelResponseCanvas")
        self.assertIn("on_block", captured_kwargs)

    def test_reject_if_request_in_flight_handles_inflight_block(self):
        if bootstrap is None or canvas_module is None:
            self.skipTest("Talon runtime not available")

        state = RequestState(phase=RequestPhase.STREAMING)

        def fake_guard(**kwargs):
            on_block = kwargs["on_block"]
            on_block("in_flight", "Model streaming…")
            return True

        with (
            patch.object(canvas_module, "_current_request_state", return_value=state),
            patch(
                "talon_user.lib.modelResponseCanvas.guard_surface_request",
                side_effect=fake_guard,
            ),
            patch("talon_user.lib.pillCanvas.show_pill") as show_pill,
        ):
            GPTState.suppress_response_canvas_close = True
            self.assertTrue(canvas_module._reject_if_request_in_flight())

        self.assertFalse(getattr(GPTState, "suppress_response_canvas_close", True))
        show_pill.assert_called_once()
        GPTState.suppress_response_canvas_close = False


if __name__ == "__main__":
    unittest.main()
