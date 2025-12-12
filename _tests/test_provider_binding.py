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
    from talon_user.lib.modelHelpers import build_request, send_request
    from talon_user.lib.modelState import GPTState

    class ProviderBindingTests(unittest.TestCase):
        def setUp(self) -> None:
            os.environ["OPENAI_API_KEY"] = "openai-key"
            os.environ["GEMINI_API_KEY"] = "gemini-key"
            GPTState.request = {"messages": [], "tools": []}
            GPTState.thread = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "hi"}],
                }
            ]
            GPTState.request_provider = None
            GPTState.current_destination_kind = ""

        def test_provider_binding_survives_setting_change(self) -> None:
            current_provider = {"id": "openai"}

            def fake_get(key, default=None):
                if key == "user.model_provider_current":
                    return current_provider["id"]
                if key == "user.model_streaming":
                    return False
                if key == "user.model_endpoint":
                    if current_provider["id"] == "openai":
                        return "https://api.openai.com/v1/chat/completions"
                    return "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
                if key == "user.model_request_timeout_seconds":
                    return 1
                if key == "user.openai_model":
                    return "gpt-5"
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

                self.assertIn("openai", url)
                self.assertEqual(headers.get("Authorization"), "Bearer openai-key")
                return Resp()

            with (
                patch.object(modelHelpers.settings, "get", side_effect=fake_get),
                patch.object(modelHelpers.requests, "post", side_effect=fake_post),
            ):
                build_request("default")
                current_provider["id"] = "gemini"
                send_request(max_attempts=1)
                self.assertEqual(GPTState.request_provider.id, "openai")
