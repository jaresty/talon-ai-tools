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
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.providerRegistry import ProviderConfig

    class ProviderStreamingWarningTests(unittest.TestCase):
        def setUp(self) -> None:
            os.environ["OPENAI_API_KEY"] = "openai-key"
            GPTState.request = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "hi"}],
                    }
                ]
            }
            GPTState.thread = []
            GPTState.request_provider = None

        def test_streaming_disabled_warns_and_falls_back(self) -> None:
            provider = ProviderConfig(
                id="offline",
                display_name="Offline",
                aliases=["local"],
                endpoint="http://localhost:8080/v1/chat/completions",
                api_key_env="OPENAI_API_KEY",
                default_model="local-model",
                features={"streaming": False},
            )

            warnings: list[str] = []

            def fake_canvas(_provider):
                warnings.append(f"warn:{getattr(_provider, 'id', '')}")

            def fake_bound_provider():
                return provider

            def fake_get(key, default=None):
                if key == "user.model_streaming":
                    return True
                if key == "user.model_request_timeout_seconds":
                    return 1
                if key == "user.model_endpoint":
                    return provider.endpoint
                if key == "user.openai_model":
                    return provider.default_model
                return default

            def fake_post(url, headers=None, data=None, timeout=None, stream=False, json=None):
                class Resp:
                    status_code = 200

                    def json(self_inner):
                        return {
                            "choices": [
                                {"message": {"content": "ok", "tool_calls": []}},
                            ]
                        }

                    def close(self_inner):
                        return None

                    headers = {"content-type": "application/json"}
                    text = "{}"

                return Resp()

            with (
                patch.object(modelHelpers, "bound_provider", side_effect=fake_bound_provider),
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(modelHelpers, "_warn_streaming_disabled", side_effect=fake_canvas),
                patch.object(modelHelpers.requests, "post", side_effect=fake_post),
            ):
                result = modelHelpers.send_request(max_attempts=1)
            self.assertEqual(result["text"], "ok")
            self.assertTrue(any("warn" in w for w in warnings))
