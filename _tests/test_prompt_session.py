import unittest
from typing import TYPE_CHECKING
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
    from talon_user.lib.modelHelpers import MAX_TOTAL_CALLS, format_message

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
                intent="p",
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
            self.assertTrue(
                any(msg.get("role") == "system" for msg in request["messages"])
            )
            user_messages = [m for m in request["messages"] if m.get("role") == "user"]
            self.assertEqual(len(user_messages), 1)
            self.assertTrue(
                any(
                    item.get("text") == "primary"
                    for item in user_messages[0]["content"]
                )
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

        @patch.object(prompt_session_module, "send_request_async")
        def test_execute_async_returns_send_request_async_handle(
            self, mock_send_request_async
        ):
            class DummyHandle:
                pass

            mock_handle = DummyHandle()
            mock_send_request_async.return_value = mock_handle
            source = _StaticSource("input")
            session = PromptSession(destination="paste")
            session.prepare_prompt("run", source)

            handle = session.execute_async()

            self.assertIs(handle, mock_handle)
            mock_send_request_async.assert_called_once()

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

        def test_begin_without_existing_request_builds_once(self):
            session = PromptSession(destination="paste")
            session.begin()
            first_request = GPTState.request

            session.begin(reuse_existing=True)

            self.assertIs(GPTState.request, first_request)

        def test_append_thread_records_assistant_message(self):
            GPTState.enable_thread()
            session = PromptSession(destination="paste")

            assistant_item = format_message("assistant reply")

            session.append_thread(assistant_item)

            self.assertTrue(GPTState.thread)
            last_message = GPTState.thread[-1]
            self.assertEqual(last_message["role"], "assistant")
            self.assertEqual(last_message["content"][0], assistant_item)

        def test_add_system_prompt_attaches_hydrated_persona_and_axes(self):
            GPTState.reset_all()
            GPTState.system_prompt = GPTSystemPrompt(
                voice="as programmer",
                audience="to stakeholders",
                tone="directly",
                intent="for appreciation",
                completeness="full",
                scope="actions",
                method="plan",
                form="bullets",
                channel="slack",
            )
            session = PromptSession(destination="paste")
            session.begin()

            session.add_system_prompt()

            system_messages = [
                msg
                for msg in GPTState.request.get("messages", [])
                if msg.get("role") == "system"
            ]
            self.assertGreaterEqual(len(system_messages), 1)
            content_raw = system_messages[-1].get("content", [])
            hydrated = " ".join([item.get("text", "") for item in content_raw])
            self.assertIn("Voice: Act as a programmer", hydrated)
            self.assertIn(
                "Audience: The audience for this is the stakeholders", hydrated
            )
            self.assertIn(
                "Tone: The response speaks directly and straightforwardly while remaining respectful.",
                hydrated,
            )
            self.assertIn(
                "Intent: The response expresses appreciation or thanks.", hydrated
            )
            self.assertIn(
                "Completeness: The response provides a thorough answer for normal use, covering all major aspects without needing every micro-detail.",
                hydrated,
            )
            self.assertIn(
                "Scope: The response stays within the selected target and focuses only on concrete actions or tasks a user or team could take, leaving out background analysis or explanation.",
                hydrated,
            )
            self.assertIn(
                "Method: The response offers a short plan first and then carries it out, clearly separating the plan from the execution.",
                hydrated,
            )
            self.assertIn(
                "Form: The response presents the main answer as concise bullet points only, avoiding long paragraphs.",
                hydrated,
            )
            self.assertIn(
                "Channel: The response formats the answer for Slack using appropriate Markdown, mentions, and code blocks while avoiding channel-irrelevant decoration.",
                hydrated,
            )
else:
    if not TYPE_CHECKING:

        class PromptSessionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
