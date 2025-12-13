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
            patch.object(provider_module, "_reject_if_request_in_flight", return_value=True),
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
        with patch.object(
            provider_module, "_reject_if_request_in_flight", return_value=True
        ), patch.object(actions.user, "model_provider_use") as user_use:
            ProviderActions.model_provider_switch("openai")
        user_use.assert_not_called()


if __name__ == "__main__":
    unittest.main()
