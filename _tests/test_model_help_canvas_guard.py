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

    def test_reject_if_request_in_flight_records_drop_reason(self):
        with (
            patch.object(
                help_canvas_module,
                "try_start_request",
                return_value=(False, "in_flight"),
            ),
            patch.object(help_canvas_module, "current_state"),
            patch.object(help_canvas_module, "set_drop_reason") as set_reason,
            patch.object(help_canvas_module, "notify") as notify_mock,
        ):
            self.assertTrue(help_canvas_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(
                help_canvas_module, "try_start_request", return_value=(True, "")
            ),
            patch.object(help_canvas_module, "current_state"),
            patch.object(help_canvas_module, "set_drop_reason") as set_reason,
            patch.object(help_canvas_module, "notify") as notify_mock,
        ):
            self.assertFalse(help_canvas_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
