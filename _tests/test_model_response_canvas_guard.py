import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelResponseCanvas as canvas_module
    from talon_user.lib.modelResponseCanvas import ResponseCanvasState, UserActions


class ModelResponseCanvasGuardTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
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
            UserActions.model_response_canvas_refresh()
            UserActions.model_response_canvas_open()
            UserActions.model_response_canvas_toggle()
            UserActions.model_response_canvas_close()
        ensure.assert_not_called()
        self.assertFalse(ResponseCanvasState.showing)

    def test_reject_if_request_in_flight_records_drop_reason(self):
        with (
            patch.object(
                canvas_module, "try_begin_request", return_value=(False, "in_flight")
            ),
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertTrue(canvas_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(canvas_module, "try_begin_request", return_value=(True, "")),
            patch.object(canvas_module, "set_drop_reason") as set_reason,
            patch.object(canvas_module, "notify") as notify_mock,
        ):
            self.assertFalse(canvas_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
