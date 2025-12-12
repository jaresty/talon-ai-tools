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
    from talon_user.lib import modelHelpers
    from talon_user.lib.modelHelpers import UnsupportedProviderCapability
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.providerRegistry import ProviderConfig

    class ProviderCapabilityGuardTests(unittest.TestCase):
        def setUp(self) -> None:
            os.environ["OPENAI_API_KEY"] = "openai-key"
            os.environ["GEMINI_API_KEY"] = "gemini-key"
            GPTState.request_provider = ProviderConfig(
                id="gemini",
                display_name="Gemini",
                aliases=["gemeni"],
                endpoint="https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
                api_key_env="GEMINI_API_KEY",
                default_model="gemini-1.5-pro",
                features={"vision": False, "streaming": True},
            )
            GPTState.request = {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "hello"},
                            {"type": "image_url", "image_url": {"url": "http://example.com/image.png"}},
                        ],
                    }
                ]
            }

        def test_vision_guard_blocks_send(self) -> None:
            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return False
                if key == "user.model_request_timeout_seconds":
                    return 1
                if key == "user.model_endpoint":
                    return GPTState.request_provider.endpoint
                if key == "user.openai_model":
                    return "gpt-5"
                return default

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(modelHelpers.requests, "post", side_effect=AssertionError("should not post")),
            ):
                with self.assertRaises(UnsupportedProviderCapability):
                    modelHelpers.send_request(max_attempts=1)
