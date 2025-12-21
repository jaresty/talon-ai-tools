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

        with (
            patch.object(
                provider_module,
                "try_begin_request",
                return_value=(False, "in_flight"),
            ) as try_begin,
            patch.object(
                provider_module,
                "drop_reason_message",
                return_value="Request running",
            ) as drop_message,
            patch.object(provider_module, "set_drop_reason") as set_reason,
            patch.object(provider_module, "notify") as notify_mock,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())
        try_begin.assert_called_once_with(source="providerCommands")
        drop_message.assert_called_once_with("in_flight")
        set_reason.assert_called_once_with("in_flight", "Request running")
        notify_mock.assert_called_once_with("Request running")

        with (
            patch.object(
                provider_module,
                "try_begin_request",
                return_value=(False, "unknown_reason"),
            ),
            patch.object(provider_module, "drop_reason_message", return_value=""),
            patch.object(provider_module, "set_drop_reason") as set_reason,
            patch.object(provider_module, "notify") as notify_mock,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())
        set_reason.assert_called_once_with(
            "unknown_reason", "GPT: Request blocked; reason=unknown_reason."
        )
        notify_mock.assert_called_once_with(
            "GPT: Request blocked; reason=unknown_reason."
        )

        with (
            patch.object(
                provider_module, "try_begin_request", return_value=(True, "")
            ) as try_begin,
            patch.object(provider_module, "set_drop_reason") as set_reason,
            patch.object(provider_module, "notify") as notify_mock,
        ):
            self.assertFalse(provider_module._reject_if_request_in_flight())
        try_begin.assert_called_once_with(source="providerCommands")
        set_reason.assert_called_once_with("")
        notify_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
