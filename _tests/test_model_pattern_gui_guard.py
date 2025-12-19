import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelPatternGUI as pattern_module
    from talon_user.lib.modelPatternGUI import UserActions as PatternActions


class ModelPatternGUIGuardTests(unittest.TestCase):
    def test_pattern_gui_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                pattern_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(pattern_module, "_open_pattern_canvas") as open_canvas,
            patch.object(pattern_module, "_close_pattern_canvas") as close_canvas,
            patch.object(pattern_module, "_run_pattern") as run_pattern,
            patch.object(
                pattern_module.actions.user, "confirmation_gui_save_to_file"
            ) as save_file,
            patch.object(
                pattern_module, "pattern_debug_view", create=True
            ) as debug_view,
        ):
            PatternActions.model_pattern_gui_open()
            PatternActions.model_pattern_gui_open_coding()
            PatternActions.model_pattern_gui_open_writing()
            PatternActions.model_pattern_gui_close()
            PatternActions.model_pattern_run_name("any")
            PatternActions.model_pattern_save_source_to_file()
            PatternActions.model_pattern_debug_name("any")
        open_canvas.assert_not_called()
        close_canvas.assert_not_called()
        run_pattern.assert_not_called()
        save_file.assert_not_called()
        debug_view.assert_not_called()

    def test_reject_if_request_in_flight_records_drop_reason(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with (
            patch.object(
                pattern_module, "try_begin_request", return_value=(False, "in_flight")
            ),
            patch.object(pattern_module, "set_drop_reason") as set_reason,
            patch.object(pattern_module, "notify") as notify_mock,
        ):
            self.assertTrue(pattern_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with("in_flight")
        notify_mock.assert_called_once()

        with (
            patch.object(pattern_module, "try_begin_request", return_value=(True, "")),
            patch.object(pattern_module, "set_drop_reason") as set_reason,
            patch.object(pattern_module, "notify") as notify_mock,
        ):
            self.assertFalse(pattern_module._reject_if_request_in_flight())
        set_reason.assert_not_called()
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
