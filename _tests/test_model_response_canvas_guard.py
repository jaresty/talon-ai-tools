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
    import talon_user.lib.dropReasonUtils as drop_reason_module


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

    def test_reject_if_request_in_flight_records_drop_reason(self):
        with (
            patch.object(
                canvas_module, "try_begin_request", return_value=(False, "in_flight")
            ),
            patch.object(
                canvas_module,
                "render_drop_reason",
                return_value="Request running",
                create=True,
            ) as render_message,
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertTrue(canvas_module._reject_if_request_in_flight())
        render_message.assert_called_once_with("in_flight")
        set_reason.assert_called_once_with("in_flight", "Request running")
        notify_mock.assert_called_once_with("Request running")

        with (
            patch.object(
                canvas_module,
                "try_begin_request",
                return_value=(False, "rate_limited"),
            ),
            patch.object(
                drop_reason_module,
                "drop_reason_message",
                return_value="",
            ),
            patch.object(
                canvas_module,
                "render_drop_reason",
                return_value="Rendered fallback",
                create=True,
            ) as render_message,
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertTrue(canvas_module._reject_if_request_in_flight())
        render_message.assert_called_once_with("rate_limited")
        set_reason.assert_called_once_with("rate_limited", "Rendered fallback")
        notify_mock.assert_called_once_with("Rendered fallback")

        with (
            patch.object(canvas_module, "try_begin_request", return_value=(True, "")),
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertFalse(canvas_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("")
        notify_mock.assert_not_called()

    def test_reject_if_request_in_flight_preserves_drop_reason_on_success(self):
        if bootstrap is None or canvas_module is None:
            self.skipTest("Talon runtime not available")

        with (
            patch.object(canvas_module, "try_begin_request", return_value=(True, "")),
            patch.object(
                canvas_module,
                "last_drop_reason",
                return_value="",
                create=True,
            ),
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertFalse(canvas_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("")
        notify_mock.assert_not_called()

        with (
            patch.object(canvas_module, "try_begin_request", return_value=(True, "")),
            patch.object(
                canvas_module,
                "last_drop_reason",
                return_value="drop_pending",
                create=True,
            ),
            patch.object(canvas_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(canvas_module._reject_if_request_in_flight())
        set_reason.assert_not_called()


if __name__ == "__main__":
    unittest.main()
