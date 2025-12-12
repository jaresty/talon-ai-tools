import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelHelpers
    from talon_user.lib.modelHelpers import ClipboardImageUnsupportedProvider
    from talon_user.lib.providerRegistry import ProviderConfig

    class ClipboardImageGuardTests(unittest.TestCase):
        def test_clipboard_guard_blocks_non_vision_provider(self) -> None:
            provider = ProviderConfig(
                id="gemini",
                display_name="Gemini",
                aliases=["gemeni"],
                endpoint="https://example.com",
                api_key_env="GEMINI_API_KEY",
                default_model="gemini-1.5-pro",
                features={"vision": False},
            )

            def fake_provider():
                return provider

            with patch.object(modelHelpers, "bound_provider", side_effect=fake_provider):
                with self.assertRaises(ClipboardImageUnsupportedProvider):
                    modelHelpers.get_clipboard_image()
