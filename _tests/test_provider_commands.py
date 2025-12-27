import unittest
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import providerCommands as provider_module
    from talon_user.lib.providerCommands import UserActions as ProviderActions
    from talon import actions


class ProviderCommandGuardTests(unittest.TestCase):
    def test_provider_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                provider_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(provider_module, "provider_registry") as registry,
            patch.object(provider_module, "show_provider_canvas") as show_canvas,
        ):
            ProviderActions.model_provider_list()
            ProviderActions.model_provider_status()
            ProviderActions.model_provider_use("openai")
            ProviderActions.model_provider_next()
            ProviderActions.model_provider_previous()
        registry.assert_not_called()
        show_canvas.assert_not_called()

    def test_provider_switch_respects_guard_through_use(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                provider_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(actions.user, "model_provider_use") as user_use,
        ):
            ProviderActions.model_provider_switch("openai")
        user_use.assert_not_called()

    def test_request_is_in_flight_delegates_to_request_gating(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with patch.object(
            provider_module, "request_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(provider_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            provider_module, "request_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(provider_module._request_is_in_flight())
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
                provider_module, "guard_surface_request", side_effect=guard_blocks
            ) as guard,
            patch.object(provider_module, "notify") as notify_mock,
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())

        guard.assert_called_once()
        self.assertEqual(captured_kwargs.get("surface"), "provider_commands")
        self.assertEqual(captured_kwargs.get("source"), "providerCommands")
        self.assertTrue(callable(captured_kwargs.get("notify_fn")))
        notify_mock.assert_called_once_with("Request running")
        set_reason.assert_not_called()

        def guard_fallback(**kwargs):
            captured_kwargs.update(kwargs)
            on_block = kwargs.get("on_block")
            on_block("unknown_reason", "")
            return True

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_fallback
            ),
            patch.object(provider_module, "notify") as notify_mock,
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())

        fallback = "GPT: Request blocked; reason=unknown_reason."
        notify_mock.assert_called_once_with(fallback)
        set_reason.assert_called_once_with("unknown_reason", fallback)

        def guard_allows(**kwargs):
            return False

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_allows
            ) as guard,
            patch.object(provider_module, "last_drop_reason", return_value=""),
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(provider_module._reject_if_request_in_flight())

        guard.assert_called_once()
        set_reason.assert_called_once_with("")

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_allows
            ),
            patch.object(
                provider_module, "last_drop_reason", return_value="drop_pending"
            ),
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(provider_module._reject_if_request_in_flight())
        set_reason.assert_not_called()


if __name__ == "__main__":
    unittest.main()
