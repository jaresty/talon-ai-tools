import os
import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import talon_user.Images.ai_images as ai_images  # type: ignore # noqa: F401,E402
    from talon_user.Images.ai_images import _image_endpoint_for, Actions  # type: ignore # noqa: E402
    from talon_user.lib.modelHelpers import UnsupportedProviderCapability
    from talon_user.lib.providerRegistry import ProviderConfig
    from talon_user.lib import modelHelpers

    class ProviderImagesGuardTests(unittest.TestCase):
        def setUp(self) -> None:
            os.environ["OPENAI_API_KEY"] = "openai-key"

        def test_image_endpoint_derivation(self) -> None:
            self.assertEqual(
                _image_endpoint_for("https://api.openai.com/v1/chat/completions"),
                "https://api.openai.com/v1/images/generations",
            )
            self.assertEqual(
                _image_endpoint_for("http://localhost:8080/v1"),
                "http://localhost:8080/v1/images/generations",
            )

        def test_images_capability_guard(self) -> None:
            provider = ProviderConfig(
                id="gemini",
                display_name="Gemini",
                aliases=[],
                endpoint="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                api_key_env="GEMINI_API_KEY",
                default_model="gemini-1.5-pro",
                features={"images": False},
            )

            def fake_active_provider():
                return provider

            with (
            patch.object(ai_images, "active_provider", side_effect=fake_active_provider),
            patch.object(ai_images, "get_token", side_effect=AssertionError("should not fetch token")),
            patch.object(ai_images.requests, "post", side_effect=AssertionError("should not post")),
        ):
                with self.assertRaises(UnsupportedProviderCapability):
                    Actions.image_generate("hello")
