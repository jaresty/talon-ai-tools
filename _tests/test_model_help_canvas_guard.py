import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelHelpCanvas as help_canvas_module
    from talon_user.lib.modelHelpCanvas import (
        HelpCanvasState,
        UserActions as HelpActions,
    )
    import talon_user.lib.dropReasonUtils as drop_reason_module


class ModelHelpCanvasGuardTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        HelpCanvasState.showing = False
        HelpCanvasState.focus = "all"
        HelpCanvasState.static_prompt_focus = None

    def test_help_canvas_actions_respect_in_flight_guard(self):
        with (
            patch.object(
                help_canvas_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(help_canvas_module, "_open_canvas") as open_canvas,
            patch.object(help_canvas_module, "_reset_help_state") as reset_help,
        ):
            HelpActions.model_help_canvas_open()
            HelpActions.model_help_canvas_close()
            HelpActions.model_help_canvas_open_for_last_recipe()
            HelpActions.model_help_canvas_open_for_static_prompt("describe")
            HelpActions.model_help_canvas_open_completeness()
            HelpActions.model_help_canvas_open_scope()
            HelpActions.model_help_canvas_open_method()
            HelpActions.model_help_canvas_open_form()
            HelpActions.model_help_canvas_open_channel()
            HelpActions.model_help_canvas_open_directional()
            HelpActions.model_help_canvas_open_examples()
            HelpActions.model_help_canvas_open_who()
            HelpActions.model_help_canvas_open_why()
            HelpActions.model_help_canvas_open_how()

        open_canvas.assert_not_called()
        reset_help.assert_not_called()
        self.assertFalse(HelpCanvasState.showing)

    def test_request_is_in_flight_delegates_to_request_gating(self):
        with patch.object(
            help_canvas_module, "request_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(help_canvas_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            help_canvas_module, "request_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(help_canvas_module._request_is_in_flight())
        helper.assert_called_once_with()

    def test_reject_if_request_in_flight_notifies_with_drop_message(self):
        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(False, "in_flight"),
            ) as try_begin,
            patch(
                "talon_user.lib.surfaceGuidance.render_drop_reason",
                return_value="Request running",
            ) as render_message,
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
            patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
        ):
            self.assertTrue(help_canvas_module._reject_if_request_in_flight())
        try_begin.assert_called_once_with(source="modelHelpCanvas")
        render_message.assert_called_once_with("in_flight")
        set_reason.assert_called_once_with("in_flight", "Request running")
        notify_mock.assert_called_once_with("Request running")

    def test_reject_if_request_in_flight_falls_back_to_reason_text(self):
        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(False, "unknown_reason"),
            ),
            patch.object(
                drop_reason_module,
                "drop_reason_message",
                return_value="",
            ),
            patch(
                "talon_user.lib.surfaceGuidance.render_drop_reason",
                return_value="Rendered fallback",
            ) as render_message,
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
            patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
        ):
            self.assertTrue(help_canvas_module._reject_if_request_in_flight())
        render_message.assert_called_once_with("unknown_reason")
        set_reason.assert_called_once_with("unknown_reason", "Rendered fallback")
        notify_mock.assert_called_once_with("Rendered fallback")

    def test_reject_if_request_in_flight_clears_drop_reason_on_success(self):
        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(True, ""),
            ),
            patch(
                "talon_user.lib.surfaceGuidance.last_drop_reason",
                return_value="",
            ),
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
            patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
        ):
            self.assertFalse(help_canvas_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("")
        notify_mock.assert_not_called()

        with (
            patch(
                "talon_user.lib.surfaceGuidance.try_begin_request",
                return_value=(True, ""),
            ),
            patch(
                "talon_user.lib.surfaceGuidance.last_drop_reason",
                return_value="drop_pending",
            ),
            patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
        ):
            self.assertFalse(help_canvas_module._reject_if_request_in_flight())
        set_reason.assert_not_called()

    def test_help_canvas_close_allows_inflight(self):
        with (
            patch(
                "talon_user.lib.modelHelpCanvas.guard_surface_request",
                return_value=False,
            ) as guard,
            patch.object(help_canvas_module, "_reset_help_state"),
            patch.object(help_canvas_module, "_close_canvas"),
        ):
            HelpActions.model_help_canvas_close()

        guard.assert_called_once()
        self.assertTrue(guard.call_args.kwargs.get("allow_inflight"))

    def test_help_canvas_open_toggle_closing_allows_inflight(self):
        HelpCanvasState.showing = True
        with (
            patch(
                "talon_user.lib.modelHelpCanvas.guard_surface_request",
                return_value=False,
            ) as guard,
            patch.object(help_canvas_module, "_reset_help_state"),
            patch.object(help_canvas_module, "_close_canvas"),
        ):
            HelpActions.model_help_canvas_open()

        guard.assert_called_once()
        self.assertTrue(guard.call_args.kwargs.get("allow_inflight"))
        HelpCanvasState.showing = False


if __name__ == "__main__":
    unittest.main()
