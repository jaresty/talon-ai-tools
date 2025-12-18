import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelConfirmationGUI as confirm_module
    from talon_user.lib.modelConfirmationGUI import (
        ConfirmationGUIState,
        UserActions as ConfirmActions,
    )
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon_user.lib.modelState import GPTState


class ConfirmationGUIGuardTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        GPTState.text_to_confirm = ""
        ConfirmationGUIState.current_presentation = None
        ConfirmationGUIState.display_thread = False
        ConfirmationGUIState.last_item_text = ""
        ConfirmationGUIState.show_advanced_actions = False

    def test_confirmation_actions_respect_in_flight_guard(self):
        with (
            patch.object(
                confirm_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(
                confirm_module.actions.user, "model_response_canvas_open"
            ) as canvas_open,
        ):
            ConfirmActions.confirmation_gui_append("text")
            ConfirmActions.confirmation_gui_close()
            ConfirmActions.confirmation_gui_pass_context()
            ConfirmActions.confirmation_gui_pass_query()
            ConfirmActions.confirmation_gui_pass_thread()
            ConfirmActions.confirmation_gui_open_browser()
            ConfirmActions.confirmation_gui_analyze_prompt()
            ConfirmActions.confirmation_gui_save_to_file()
            ConfirmActions.confirmation_gui_copy()
            ConfirmActions.confirmation_gui_paste()
            ConfirmActions.confirmation_gui_refresh_thread()
            ConfirmActions.confirmation_gui_open_pattern_menu_for_prompt()
        canvas_open.assert_not_called()
        self.assertEqual(GPTState.text_to_confirm, "")
        self.assertIsNone(ConfirmationGUIState.current_presentation)

    def test_confirmation_append_respects_guard_with_presentation(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        presentation = ResponsePresentation(display_text="out", paste_text="out")
        with (
            patch.object(
                confirm_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(
                confirm_module.actions.user, "model_response_canvas_open"
            ) as canvas_open,
        ):
            ConfirmActions.confirmation_gui_append(presentation)
        canvas_open.assert_not_called()
        self.assertIsNone(ConfirmationGUIState.current_presentation)
        self.assertEqual(GPTState.text_to_confirm, "")

    def test_reject_if_request_in_flight_records_drop_reason(self):
        with (
            patch.object(
                confirm_module, "try_start_request", return_value=(False, "in_flight")
            ),
            patch.object(confirm_module, "current_state"),
            patch.object(confirm_module, "set_drop_reason") as set_reason,
            patch.object(confirm_module, "notify") as notify_mock,
        ):
            self.assertTrue(confirm_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(confirm_module, "try_start_request", return_value=(True, "")),
            patch.object(confirm_module, "current_state"),
            patch.object(confirm_module, "set_drop_reason") as set_reason,
            patch.object(confirm_module, "notify") as notify_mock,
        ):
            self.assertFalse(confirm_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
