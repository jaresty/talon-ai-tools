import unittest
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelConfirmationGUI as confirmation_module
    from talon_user.lib.modelConfirmationGUI import UserActions as ConfirmationActions


class ModelConfirmationGUIGuardTests(unittest.TestCase):
    def test_reject_if_request_in_flight_delegates_to_surface_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        captured_kwargs: dict[str, object] = {}

        def fake_guard(**kwargs):
            captured_kwargs.update(kwargs)
            return True

        with patch(
            "talon_user.lib.modelConfirmationGUI.guard_surface_request",
            side_effect=fake_guard,
        ):
            self.assertTrue(confirmation_module._reject_if_request_in_flight())

        self.assertEqual(captured_kwargs["surface"], "confirmation_gui")
        self.assertEqual(captured_kwargs["source"], "modelConfirmationGUI")
        self.assertIn("on_block", captured_kwargs)
        self.assertFalse(captured_kwargs.get("allow_inflight"))

    def test_confirmation_gui_close_allows_inflight(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        gui_mock = MagicMock()
        gui_mock.hide = MagicMock()

        with (
            patch.object(confirmation_module, "confirmation_gui", gui_mock),
            patch(
                "talon_user.lib.modelConfirmationGUI.guard_surface_request",
                return_value=False,
            ) as guard,
            patch(
                "talon_user.lib.modelConfirmationGUI.close_common_overlays"
            ) as closer,
        ):
            ConfirmationActions.confirmation_gui_close()

        guard.assert_called_once()
        self.assertTrue(guard.call_args.kwargs.get("allow_inflight"))
        gui_mock.hide.assert_called_once()
        closer.assert_called_once()


if __name__ == "__main__":
    unittest.main()
