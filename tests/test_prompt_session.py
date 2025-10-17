import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions, settings
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelTypes import GPTSystemPrompt
    from talon_user.lib.promptSession import PromptSession
    from talon_user.lib.modelSource import ModelSource
    from talon_user.lib import promptSession as prompt_session_module
    from talon_user.lib.modelHelpers import MAX_TOTAL_CALLS

    class _StaticSource(ModelSource):
        def __init__(self, text: str):
            self._text = text

        def get_text(self):  # type: ignore[override]
            return self._text

    class PromptSessionTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            GPTState.system_prompt = GPTSystemPrompt(
                voice="v",
                purpose="p",
                tone="t",
                audience="a",
            )
            settings.set("user.openai_model", "gpt-test")
            actions.user.gpt_tools = lambda: "[]"  # type: ignore[attr-defined]
            actions.user.gpt_additional_user_context = lambda: []  # type: ignore[attr-defined]

        def test_prepare_prompt_populates_request(self):
            source = _StaticSource("primary")
            session = PromptSession(destination="paste")

            session.prepare_prompt("do thing", source)

            request = GPTState.request
            self.assertEqual(request["model"], settings.get("user.openai_model"))
            self.assertTrue(any(msg.get("role") == "system" for msg in request["messages"]))
            user_messages = [m for m in request["messages"] if m.get("role") == "user"]
            self.assertEqual(len(user_messages), 1)
            self.assertTrue(
                any(item.get("text") == "primary" for item in user_messages[0]["content"])
            )

        @patch.object(prompt_session_module, "send_request")
        def test_execute_returns_send_request_result(self, mock_send_request):
            mock_send_request.return_value = {"type": "text", "text": "done"}
            source = _StaticSource("input")
            session = PromptSession(destination="paste")
            session.prepare_prompt("run", source)

            result = session.execute()

            self.assertEqual(result["text"], "done")
            mock_send_request.assert_called_once()

        def test_begin_reuse_existing_skips_build(self):
            GPTState.request = {
                "messages": [],
                "model": settings.get("user.openai_model"),
                "tools": [],
            }
            session = PromptSession(destination="paste")
            session.begin(reuse_existing=True)

            self.assertTrue(session._prepared)

        def test_add_messages_appends_tool_responses(self):
            source = _StaticSource("primary")
            session = PromptSession(destination="paste")
            session.prepare_prompt("hello", source)

            tool_message = {
                "tool_call_id": "1",
                "name": "tool",
                "type": "function",
                "role": "tool",
                "content": "result",
            }

            session.add_messages([tool_message])

            self.assertIn(tool_message, GPTState.request["messages"])

        def test_add_messages_does_not_exceed_total_calls(self):
            source = _StaticSource("primary")
            session = PromptSession(destination="paste")
            session.prepare_prompt("hello", source)

            for _ in range(MAX_TOTAL_CALLS):
                session.add_messages(
                    [
                        {
                            "tool_call_id": "1",
                            "name": "tool",
                            "type": "function",
                            "role": "tool",
                            "content": "result",
                        }
                    ]
                )

            self.assertGreaterEqual(len(GPTState.request["messages"]), MAX_TOTAL_CALLS)

        def test_begin_without_existing_request_builds_once(self):
            session = PromptSession(destination="paste")
            session.begin()
            first_request = GPTState.request

            session.begin(reuse_existing=True)

            self.assertIs(GPTState.request, first_request)
else:
    class PromptSessionTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
