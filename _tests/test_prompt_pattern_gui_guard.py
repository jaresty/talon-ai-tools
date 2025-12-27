import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelPromptPatternGUI as prompt_pattern_module
    from talon_user.lib.modelPromptPatternGUI import UserActions as PromptPatternActions


class PromptPatternGUIGuardTests(unittest.TestCase):
    def test_prompt_pattern_gui_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                prompt_pattern_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(
                prompt_pattern_module, "_open_prompt_pattern_canvas"
            ) as open_canvas,
            patch.object(
                prompt_pattern_module, "_close_prompt_pattern_canvas"
            ) as close_canvas,
        ):
            PromptPatternActions.prompt_pattern_gui_open_for_static_prompt("describe")
            PromptPatternActions.prompt_pattern_gui_close()
            PromptPatternActions.prompt_pattern_run_preset("analysis")
            PromptPatternActions.prompt_pattern_save_source_to_file()
        open_canvas.assert_not_called()
        close_canvas.assert_not_called()

    def test_request_is_in_flight_delegates_to_request_gating(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with patch.object(
            prompt_pattern_module, "request_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(prompt_pattern_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            prompt_pattern_module, "request_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(prompt_pattern_module._request_is_in_flight())
        helper.assert_called_once_with()

    def test_reject_if_request_in_flight_notifies_with_drop_message(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        captured_kwargs: dict[str, object] = {}

        def guard_blocks(**kwargs):
            captured_kwargs.update(kwargs)
            on_block = kwargs.get("on_block")
            self.assertTrue(callable(on_block))
            on_block("in_flight", "Request running")
            return True

        with (
            patch.object(
                prompt_pattern_module, "guard_surface_request", side_effect=guard_blocks
            ) as guard,
            patch.object(prompt_pattern_module, "notify") as notify_mock,
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(prompt_pattern_module._reject_if_request_in_flight())

        guard.assert_called_once()
        self.assertEqual(captured_kwargs.get("surface"), "model_prompt_pattern_gui")
        self.assertEqual(captured_kwargs.get("source"), "modelPromptPatternGUI")
        self.assertTrue(callable(captured_kwargs.get("notify_fn")))
        notify_mock.assert_called_once_with("Request running")
        set_reason.assert_not_called()

        def guard_fallback(**kwargs):
            captured_kwargs.update(kwargs)
            kwargs.get("on_block")("unknown_reason", "")
            return True

        with (
            patch.object(
                prompt_pattern_module,
                "guard_surface_request",
                side_effect=guard_fallback,
            ),
            patch.object(prompt_pattern_module, "notify") as notify_mock,
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(prompt_pattern_module._reject_if_request_in_flight())

        fallback = "GPT: Request blocked; reason=unknown_reason."
        notify_mock.assert_called_once_with(fallback)
        set_reason.assert_called_once_with("unknown_reason", fallback)

    def test_reject_if_request_in_flight_preserves_drop_reason_on_success(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        def guard_allows(**kwargs):
            return False

        with (
            patch.object(
                prompt_pattern_module, "guard_surface_request", side_effect=guard_allows
            ) as guard,
            patch.object(prompt_pattern_module, "last_drop_reason", return_value=""),
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(prompt_pattern_module._reject_if_request_in_flight())

        guard.assert_called_once()
        set_reason.assert_called_once_with("")

        with (
            patch.object(
                prompt_pattern_module, "guard_surface_request", side_effect=guard_allows
            ),
            patch.object(
                prompt_pattern_module, "last_drop_reason", return_value="drop_pending"
            ),
            patch.object(prompt_pattern_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(prompt_pattern_module._reject_if_request_in_flight())
        set_reason.assert_not_called()

    def test_prompt_pattern_close_allows_inflight(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with patch.object(
            prompt_pattern_module, "guard_surface_request", return_value=False
        ) as guard:
            PromptPatternActions.prompt_pattern_gui_close()

        guard.assert_called_once()
        self.assertTrue(guard.call_args.kwargs.get("allow_inflight"))


if __name__ == "__main__":
    unittest.main()
