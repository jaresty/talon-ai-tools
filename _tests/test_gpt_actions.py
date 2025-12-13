import inspect
import os
import tempfile
import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions, clip
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelDestination import ModelDestination
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.GPT import gpt as gpt_module
    from talon_user.lib.requestBus import set_controller, current_state
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import RequestPhase
    from talon_user.lib.talonSettings import ApplyPromptConfiguration
    from talon_user.lib.requestHistoryActions import UserActions as HistoryActions
    from talon_user.lib.requestLog import append_entry, clear_history

    class GPTActionPromptSessionTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            GPTState.last_response = "assistant output"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": [],
                "scope": [],
                "method": [],
                "form": [],
                "channel": [],
                "directional": ["fog"],
            }
            gpt_module.settings.set("user.model_async_blocking", False)
            actions.user.gpt_insert_response = MagicMock()
            self._original_pipeline = gpt_module._prompt_pipeline
            self.pipeline = MagicMock()
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message("analysis")]
            )

            class _Handle:
                def __init__(self, result):
                    self.result = result

                def wait(self, timeout=None):
                    return True

            self.pipeline.complete_async.return_value = _Handle(
                PromptResult.from_messages([format_message("async analysis")])
            )
            self.pipeline.run_async.return_value = _Handle(
                PromptResult.from_messages([format_message("async run")])
            )
            self.pipeline.run.return_value = PromptResult.from_messages(
                [format_message("result")]
            )
            gpt_module._prompt_pipeline = self.pipeline
            self._original_orchestrator = gpt_module._recursive_orchestrator
            self.orchestrator = MagicMock()

            class _AsyncHandle:
                def __init__(self, result):
                    self.result = result

                def wait(self, timeout=None):
                    return True

            self.orchestrator.run_async.return_value = _AsyncHandle(
                PromptResult.from_messages([format_message("async delegated output")])
            )
            self.orchestrator.run.return_value = PromptResult.from_messages(
                [format_message("orchestrated")]
            )
            gpt_module._recursive_orchestrator = self.orchestrator

        def tearDown(self):
            gpt_module._prompt_pipeline = self._original_pipeline
            gpt_module._recursive_orchestrator = self._original_orchestrator
            actions.app.calls.clear()

        def test_gpt_save_source_to_file_writes_markdown_with_source_text(self):
            GPTState.reset_all()
            tmpdir = tempfile.mkdtemp()
            gpt_module.settings.set("user.model_source_save_directory", tmpdir)
            actions.app.calls.clear()
            actions.user.calls.clear()

            # Seed a simple last_source_messages snapshot.
            GPTState.last_source_messages = [format_message("hello world")]
            GPTState.last_source_key = "clipboard"
            GPTState.last_recipe = "describe · full"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"

            before = set(os.listdir(tmpdir))
            gpt_module.UserActions.gpt_save_source_to_file()
            after = set(os.listdir(tmpdir))
            new_files = list(after - before)
            self.assertEqual(len(new_files), 1, new_files)
            path = os.path.join(tmpdir, new_files[0])
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("# Source", content)
            self.assertIn("hello world", content)

            # Ensure we notified the user about the save.
            self.assertTrue(
                any(
                    call[0] == "notify"
                    and call[1]
                    and "Saved model source to" in str(call[1][0])
                    for call in actions.user.calls + actions.app.calls
                ),
                "Expected a notification about saving the model source",
            )

        def test_gpt_save_source_respects_in_flight_guard(self):
            GPTState.reset_all()
            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(gpt_module, "_save_source_snapshot_to_file") as saver,
            ):
                gpt_module.UserActions.gpt_save_source_to_file()

            saver.assert_not_called()

        def test_debug_toggles_respect_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(GPTState, "start_debug") as start_debug, patch.object(
                GPTState, "stop_debug"
            ) as stop_debug:
                gpt_module.UserActions.gpt_start_debug()
                gpt_module.UserActions.gpt_stop_debug()
            start_debug.assert_not_called()
            stop_debug.assert_not_called()

        def test_gpt_cancel_request_emits_cancel(self):
            set_controller(RequestUIController())
            actions.user.calls.clear()
            gpt_module.UserActions.gpt_cancel_request()
            self.assertEqual(current_state().phase, RequestPhase.CANCELLED)
            # Expect a user-level notify
            self.assertTrue(
                any(
                    call[0] == "notify"
                    for call in actions.user.calls + actions.app.calls
                )
            )

        def test_safe_model_prompt_surfaces_style_guard(self):
            """Legacy style tokens should trigger a migration hint, not crash."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.notify = MagicMock()

            class Match:
                staticPrompt = "fix"
                styleModifier = "plain"
                directionalModifier = "fog"

            prompt = gpt_module._safe_model_prompt(Match)

            self.assertEqual(prompt, "")
            self.assertTrue(actions.user.notify.called or actions.app.notify.called)

        def test_beta_paste_prompt_handles_style_guard(self):
            """Beta pass path should surface migration hint instead of pasting."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.paste = MagicMock()

            class Match:
                staticPrompt = "fix"
                styleModifier = "plain"
                directionalModifier = "fog"

            with patch.object(gpt_module, "safe_model_prompt", side_effect=ValueError("style axis is removed")):
                gpt_module.gpt_beta_paste_prompt(Match)

            actions.user.paste.assert_not_called()
            notifications = [
                call for call in actions.user.calls + actions.app.calls if call[0] == "notify"
            ]
            self.assertTrue(
                any("style axis is removed" in str(args[0]) for _name, args, _kwargs in notifications),
                f"Expected migration hint notification, got: {notifications}",
            )

        def test_beta_paste_prompt_honors_in_flight_guard(self):
            """Beta pass should no-op when a request is already in flight."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.paste = MagicMock()
            actions.user.notify = MagicMock()

            class Match:
                staticPrompt = "fix"
                directionalModifier = "fog"

            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                gpt_module.gpt_beta_paste_prompt(Match)

            actions.user.paste.assert_not_called()
            # No notify expected when simply guarded.
            self.assertFalse(actions.user.notify.called)

        def test_gpt_apply_prompt_skips_empty_prompt(self):
            """Empty prompts should be rejected with a notification."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.notify = MagicMock()
            actions.user.gpt_insert_response = MagicMock()

            class DummySource:
                modelSimpleSource = "clipboard"

                def format_messages(self):
                    return []

            class DummyDestination:
                pass

            config = ApplyPromptConfiguration(
                please_prompt="",
                model_source=DummySource(),
                additional_model_source=None,
                model_destination=DummyDestination(),
            )

            result = gpt_module.UserActions.gpt_apply_prompt(config)

            self.assertEqual(result, "")
            actions.user.gpt_insert_response.assert_not_called()
            self.assertTrue(actions.user.notify.called)

        def test_gpt_run_prompt_skips_empty_prompt(self):
            """gpt_run_prompt should reject empty prompts and notify."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.notify = MagicMock()

            class DummySource:
                modelSimpleSource = "clipboard"

                def format_messages(self):
                    return []

            result = gpt_module.UserActions.gpt_run_prompt("", DummySource())

            self.assertEqual(result, "")
            self.assertTrue(actions.user.notify.called)

        def test_gpt_recursive_prompt_skips_empty_prompt(self):
            """gpt_recursive_prompt should reject empty prompts and notify."""
            actions.user.calls.clear()
            actions.app.calls.clear()
            actions.user.notify = MagicMock()

            class DummySource:
                modelSimpleSource = "clipboard"

                def format_messages(self):
                    return []

            class DummyDestination:
                pass

            result = gpt_module.UserActions.gpt_recursive_prompt(
                "", DummySource(), DummyDestination(), None
            )

            self.assertEqual(result, "")
            self.assertTrue(actions.user.notify.called)

        def test_gpt_analyze_prompt_uses_prompt_session(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                async_result = PromptResult.from_messages([format_message("analysis")])
                handle.result = async_result

                with patch.object(gpt_module, "_handle_async_result") as handle_async:
                    gpt_module.UserActions().gpt_analyze_prompt()

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                mock_session.add_messages.assert_called_once()
                self.pipeline.complete_async.assert_called_once_with(mock_session)
                handle_async.assert_called_once_with(
                    handle, session_cls.call_args.args[0], block=False
                )
                actions.user.gpt_insert_response.assert_called_once_with(
                    async_result,
                    session_cls.call_args.args[0],
                )

        def test_gpt_apply_prompt_uses_recursive_orchestrator(self):
            configuration = MagicMock(
                please_prompt="do something",
                model_source=MagicMock(),
                additional_model_source=None,
                model_destination=MagicMock(),
            )
            with patch.object(gpt_module, "_handle_async_result") as handle_async:
                handle_async.side_effect = lambda h, d, block=True: setattr(
                    h, "result", h.result
                )
                result_text = gpt_module.UserActions.gpt_apply_prompt(configuration)

            self.orchestrator.run_async.assert_called_once_with(
                configuration.please_prompt,
                configuration.model_source,
                configuration.model_destination,
                configuration.additional_model_source,
            )
            self.orchestrator.run.assert_not_called()
            handle_async.assert_called_once()
            actions.user.gpt_insert_response.assert_called_once_with(
                self.orchestrator.run_async.return_value.result,
                configuration.model_destination,
            )
            self.assertEqual(result_text, "async delegated output")

        def test_gpt_replay_uses_prompt_session_output(self):
            GPTState.last_directional = "fog"
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session._destination = "paste"
                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                result = PromptResult.from_messages([format_message("replayed")])
                handle.result = result

                with patch.object(gpt_module, "_handle_async_result") as handle_async:
                    gpt_module.UserActions.gpt_replay("paste")

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                self.pipeline.complete_async.assert_called_once_with(mock_session)
                handle_async.assert_called_once_with(handle, "paste", block=False)

        def test_gpt_show_last_meta_notifies_when_present(self):
            GPTState.last_meta = "Interpreted as: summarise the design tradeoffs."

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_meta()

            app_notify.assert_called_once()
            self.assertIn(
                "Last meta interpretation:",
                str(app_notify.call_args[0][0]),
            )

        def test_gpt_show_last_meta_notifies_when_missing(self):
            GPTState.last_meta = ""

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_meta()

            app_notify.assert_called_once()
            self.assertIn(
                "No last meta interpretation available",
                str(app_notify.call_args[0][0]),
            )

        def test_gpt_show_last_recipe_respects_in_flight_guard(self):
            GPTState.reset_all()
            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(actions.app, "notify") as app_notify,
            ):
                gpt_module.UserActions.gpt_show_last_recipe()

            app_notify.assert_not_called()

        def test_gpt_clear_last_recap_respects_in_flight_guard(self):
            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(gpt_module, "clear_recap_state") as clear_recap,
            ):
                gpt_module.UserActions.gpt_clear_last_recap()

            clear_recap.assert_not_called()

        def test_gpt_show_last_meta_respects_in_flight_guard(self):
            GPTState.reset_all()
            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(actions.app, "notify") as app_notify,
            ):
                gpt_module.UserActions.gpt_show_last_meta()

            app_notify.assert_not_called()

        def test_gpt_show_pattern_debug_respects_in_flight_guard(self):
            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(actions.app, "notify") as app_notify,
            ):
                gpt_module.UserActions.gpt_show_pattern_debug("foo")
            app_notify.assert_not_called()

        def test_insert_helpers_respect_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.user, "gpt_insert_response") as insert_resp:
                gpt_module.UserActions.gpt_insert_text("hello")
                gpt_module.UserActions.gpt_open_browser("hello")
            insert_resp.assert_not_called()

        def test_gpt_select_last_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.edit, "extend_up") as extend_up, patch.object(
                actions.edit, "extend_line_end"
            ) as extend_line_end:
                gpt_module.UserActions.gpt_select_last()
            extend_up.assert_not_called()
            extend_line_end.assert_not_called()

        def test_source_and_prepare_helpers_respect_in_flight_guard(self):
            source = MagicMock()
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "PromptSession") as session_cls:
                text = gpt_module.UserActions.gpt_get_source_text("clipboard")
                session = gpt_module.UserActions.gpt_prepare_message(
                    source, None, "prompt"
                )
            self.assertEqual(text, "")
            session_cls.assert_called_once()
            # When short-circuiting, prepare_prompt should not be invoked.
            session_cls.return_value.prepare_prompt.assert_not_called()

        def test_additional_user_context_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ):
                ctx = gpt_module.UserActions.gpt_additional_user_context()
            self.assertEqual(ctx, [])

        def test_gpt_tools_and_call_tool_respect_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ):
                tools = gpt_module.UserActions.gpt_tools()
                result = gpt_module.UserActions.gpt_call_tool("dummy", "{}")
            self.assertEqual(tools, "[]")
            self.assertEqual(result, "")

        def test_gpt_copy_last_raw_exchange_copies_when_available(self):
            GPTState.last_raw_request = {"foo": "bar"}
            GPTState.last_raw_response = {"baz": "qux"}
            clip.set_text("")

            gpt_module.UserActions.gpt_copy_last_raw_exchange()

            copied = clip.text()
            self.assertIsInstance(copied, str)
            self.assertIn("foo", copied)
            self.assertIn("baz", copied)
            self.assertTrue(
                any(
                    call[0] == "notify"
                    and call[1]
                    and "Copied last raw request/response JSON to clipboard"
                    in str(call[1][0])
                    for call in actions.user.calls
                ),
                "Expected a user notification about copying the raw exchange",
            )

        def test_gpt_copy_last_raw_exchange_notifies_when_missing(self):
            GPTState.last_raw_request = {}
            GPTState.last_raw_response = {}
            actions.app.calls.clear()

            gpt_module.UserActions.gpt_copy_last_raw_exchange()

            self.assertTrue(
                any(
                    call[0] == "notify"
                    and call[1]
                    and "No last raw exchange available" in str(call[1][0])
                    for call in actions.user.calls
                ),
                "Expected a user notification when no raw exchange is available",
            )

        def test_gpt_copy_last_raw_exchange_respects_in_flight_guard(self):
            clip.set_text("sentinel")

            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                gpt_module.UserActions.gpt_copy_last_raw_exchange()

            # Clipboard should remain unchanged and no copy attempt made.
            self.assertEqual(clip.text(), "sentinel")

        def test_persona_set_preset_updates_persona_axes(self) -> None:
            GPTState.reset_all()
            # Start from a neutral system prompt so we can see changes clearly.
            GPTState.system_prompt = gpt_module.GPTSystemPrompt()

            gpt_module.UserActions.persona_set_preset("teach_junior_dev")

            prompt = GPTState.system_prompt
            self.assertIsInstance(prompt, gpt_module.GPTSystemPrompt)
            self.assertEqual(prompt.voice, "as teacher")
            self.assertEqual(prompt.audience, "to junior engineer")
            self.assertEqual(prompt.tone, "kindly")

        def test_intent_set_preset_updates_purpose_axis(self) -> None:
            GPTState.reset_all()
            GPTState.system_prompt = gpt_module.GPTSystemPrompt()

            gpt_module.UserActions.intent_set_preset("decide")

            prompt = GPTState.system_prompt
            self.assertIsInstance(prompt, gpt_module.GPTSystemPrompt)
            self.assertEqual(prompt.purpose, "for deciding")

        def test_persona_and_intent_reset_restore_defaults(self) -> None:
            GPTState.reset_all()
            # Seed a non-default stance first.
            GPTState.system_prompt = gpt_module.GPTSystemPrompt(
                voice="as teacher",
                audience="to junior engineer",
                purpose="for teaching",
                tone="kindly",
            )

            gpt_module.UserActions.persona_reset()
            gpt_module.UserActions.intent_reset()

            prompt = GPTState.system_prompt
            self.assertIsInstance(prompt, gpt_module.GPTSystemPrompt)
            self.assertEqual(prompt.voice, "")
            self.assertEqual(prompt.audience, "")
            self.assertEqual(prompt.tone, "")
            self.assertEqual(prompt.purpose, "")

        def test_persona_and_intent_status_notify(self) -> None:
            GPTState.reset_all()
            GPTState.system_prompt = gpt_module.GPTSystemPrompt(
                voice="as teacher",
                audience="to junior engineer",
                purpose="for teaching",
                tone="kindly",
            )
            actions.app.calls.clear()
            actions.user.calls.clear()

            gpt_module.UserActions.persona_status()
            gpt_module.UserActions.intent_status()

            persona_notifies = [
                call
                for call in actions.user.calls + actions.app.calls
                if call[0] == "notify"
                and call[1]
                and "Persona stance" in str(call[1][0])
            ]
            intent_notifies = [
                call
                for call in actions.user.calls + actions.app.calls
                if call[0] == "notify"
                and call[1]
                and "Intent stance" in str(call[1][0])
            ]
            self.assertTrue(persona_notifies, "Expected persona_status to notify")
            self.assertTrue(intent_notifies, "Expected intent_status to notify")

        def test_persona_status_respects_in_flight_guard(self) -> None:
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.persona_status()
            notify_mock.assert_not_called()

        def test_intent_status_respects_in_flight_guard(self) -> None:
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.intent_status()
            notify_mock.assert_not_called()

        def test_gpt_help_respects_in_flight_guard(self) -> None:
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "open", side_effect=AssertionError("should not open")):
                gpt_module.UserActions.gpt_help()

        def test_clear_context_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module.GPTState, "clear_context") as clear_ctx:
                gpt_module.UserActions.gpt_clear_context()
            clear_ctx.assert_not_called()

        def test_clear_stack_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module.GPTState, "clear_stack") as clear_stack:
                gpt_module.UserActions.gpt_clear_stack("a")
            clear_stack.assert_not_called()

        def test_clear_all_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module.GPTState, "clear_all") as clear_all:
                gpt_module.UserActions.gpt_clear_all()
            clear_all.assert_not_called()

        def test_persona_set_preset_respects_in_flight_guard(self) -> None:
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.persona_set_preset("teach_junior_dev")
            notify_mock.assert_not_called()

        def test_intent_set_preset_respects_in_flight_guard(self) -> None:
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.intent_set_preset("decide")
            notify_mock.assert_not_called()

        def test_persona_reset_respects_in_flight_guard(self) -> None:
            GPTState.system_prompt = gpt_module.GPTSystemPrompt(
                voice="as teacher", audience="to junior engineer", tone="kindly"
            )
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.persona_reset()
            notify_mock.assert_not_called()
            prompt = GPTState.system_prompt
            self.assertEqual(prompt.voice, "as teacher")
            self.assertEqual(prompt.audience, "to junior engineer")
            self.assertEqual(prompt.tone, "kindly")

        def test_intent_reset_respects_in_flight_guard(self) -> None:
            GPTState.system_prompt = gpt_module.GPTSystemPrompt(purpose="for teaching")
            with patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True):
                with patch.object(gpt_module, "notify") as notify_mock:
                    gpt_module.UserActions.intent_reset()
            notify_mock.assert_not_called()
            self.assertEqual(GPTState.system_prompt.purpose, "for teaching")

        def test_gpt_reset_system_prompt_respects_in_flight_guard(self) -> None:
            GPTState.system_prompt = gpt_module.GPTSystemPrompt(
                voice="as teacher", audience="to junior engineer", tone="kindly"
            )
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "_set_setting") as set_setting, patch.object(
                gpt_module, "GPTSystemPrompt"
            ) as prompt_cls:
                gpt_module.UserActions.gpt_reset_system_prompt()
            set_setting.assert_not_called()
            prompt_cls.assert_not_called()
            prompt = GPTState.system_prompt
            self.assertEqual(prompt.voice, "as teacher")
            self.assertEqual(prompt.audience, "to junior engineer")
            self.assertEqual(prompt.tone, "kindly")

        def test_gpt_replay_non_blocking_calls_handle_async_with_block_false(self):
            GPTState.last_directional = "fog"
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session._destination = "paste"
                handle = self.pipeline.complete_async.return_value
                handle.result = PromptResult.from_messages([format_message("replayed")])
                with patch.object(gpt_module, "_handle_async_result") as handle_async:
                    gpt_module.UserActions.gpt_replay("paste")
                    handle_async.assert_called_once_with(handle, "paste", block=False)

        def test_gpt_set_async_blocking_sets_setting_and_notifies(self):
            actions.app.calls.clear()
            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_set_async_blocking(1)
            self.assertTrue(gpt_module.settings.get("user.model_async_blocking"))
            app_notify.assert_called_once()
            self.assertIn(
                "async mode set to",
                str(app_notify.call_args[0][0]),
            )

        def test_gpt_set_async_blocking_respects_in_flight_guard(self):
            gpt_module.settings.set("user.model_async_blocking", False)
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "_set_setting") as set_setting, patch.object(
                actions.app, "notify"
            ) as app_notify:
                gpt_module.UserActions.gpt_set_async_blocking(1)
            set_setting.assert_not_called()
            app_notify.assert_not_called()
            self.assertFalse(gpt_module.settings.get("user.model_async_blocking"))

        def test_default_setters_update_settings_and_flags(self):
            gpt_module.settings.set("user.model_default_completeness", "")
            gpt_module.settings.set("user.model_default_scope", "")
            gpt_module.settings.set("user.model_default_method", "")
            gpt_module.settings.set("user.model_default_form", "")
            gpt_module.settings.set("user.model_default_channel", "")
            GPTState.user_overrode_completeness = False
            GPTState.user_overrode_scope = False
            GPTState.user_overrode_method = False
            GPTState.user_overrode_form = False
            GPTState.user_overrode_channel = False

            gpt_module.UserActions.gpt_set_default_completeness("full")
            gpt_module.UserActions.gpt_set_default_scope("narrow")
            gpt_module.UserActions.gpt_set_default_method("steps")
            gpt_module.UserActions.gpt_set_default_form("bullets")
            gpt_module.UserActions.gpt_set_default_channel("slack")

            self.assertEqual(
                gpt_module.settings.get("user.model_default_completeness"), "full"
            )
            self.assertEqual(gpt_module.settings.get("user.model_default_scope"), "narrow")
            self.assertEqual(gpt_module.settings.get("user.model_default_method"), "steps")
            self.assertEqual(gpt_module.settings.get("user.model_default_form"), "bullets")
            self.assertEqual(gpt_module.settings.get("user.model_default_channel"), "slack")
            self.assertTrue(GPTState.user_overrode_completeness)
            self.assertTrue(GPTState.user_overrode_scope)
            self.assertTrue(GPTState.user_overrode_method)
            self.assertTrue(GPTState.user_overrode_form)
            self.assertTrue(GPTState.user_overrode_channel)

        def test_gpt_run_prompt_returns_pipeline_text(self):
            source = MagicMock()

            text = gpt_module.UserActions.gpt_run_prompt("question", source)

            # Async path preferred; fallback to sync when needed.
            self.pipeline.run_async.assert_called_once_with(
                "question", source, destination="", additional_source=None
            )
            self.assertEqual(text, "async run")

        def test_gpt_run_prompt_uses_async_and_blocks_setting(self):
            source = MagicMock()
            handle = self.pipeline.run_async.return_value
            handle.wait = MagicMock(return_value=True)
            async_result = PromptResult.from_messages(
                [format_message("async run result")]
            )
            handle.result = async_result
            actions.user.calls.clear()

            text = gpt_module.UserActions.gpt_run_prompt("question", source)

            handle.wait.assert_called_once()
            self.assertEqual(text, "async run result")

        def test_gpt_search_engine_respects_in_flight_guard(self):
            source = MagicMock()
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.user, "gpt_run_prompt") as run_prompt:
                result = gpt_module.UserActions.gpt_search_engine("google", source)
            self.assertEqual(result, "")
            run_prompt.assert_not_called()

        def test_default_resets_respect_in_flight_guard(self):
            GPTState.user_overrode_completeness = True
            GPTState.user_overrode_scope = True
            GPTState.user_overrode_method = True
            GPTState.user_overrode_form = True
            GPTState.user_overrode_channel = True
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "_set_setting") as set_setting:
                gpt_module.UserActions.gpt_reset_default_completeness()
                gpt_module.UserActions.gpt_reset_default_scope()
                gpt_module.UserActions.gpt_reset_default_method()
                gpt_module.UserActions.gpt_reset_default_form()
                gpt_module.UserActions.gpt_reset_default_channel()
            set_setting.assert_not_called()
            self.assertTrue(GPTState.user_overrode_completeness)
            self.assertTrue(GPTState.user_overrode_scope)
            self.assertTrue(GPTState.user_overrode_method)
            self.assertTrue(GPTState.user_overrode_form)
            self.assertTrue(GPTState.user_overrode_channel)

        def test_default_setters_respect_in_flight_guard(self):
            gpt_module.settings.set("user.model_default_completeness", "")
            gpt_module.settings.set("user.model_default_scope", "")
            gpt_module.settings.set("user.model_default_method", "")
            gpt_module.settings.set("user.model_default_form", "")
            gpt_module.settings.set("user.model_default_channel", "")
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "_set_setting") as set_setting:
                gpt_module.UserActions.gpt_set_default_completeness("full")
                gpt_module.UserActions.gpt_set_default_scope("narrow")
                gpt_module.UserActions.gpt_set_default_method("steps")
                gpt_module.UserActions.gpt_set_default_form("bullets")
                gpt_module.UserActions.gpt_set_default_channel("slack")
            set_setting.assert_not_called()
            self.assertEqual(gpt_module.settings.get("user.model_default_completeness"), "")
            self.assertEqual(gpt_module.settings.get("user.model_default_scope"), "")
            self.assertEqual(gpt_module.settings.get("user.model_default_method"), "")
            self.assertEqual(gpt_module.settings.get("user.model_default_form"), "")
            self.assertEqual(gpt_module.settings.get("user.model_default_channel"), "")

        def test_gpt_help_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.app, "open") as app_open:
                gpt_module.UserActions.gpt_help()
            app_open.assert_not_called()

        def test_default_resets_clear_flags(self):
            GPTState.user_overrode_completeness = True
            GPTState.user_overrode_scope = True
            GPTState.user_overrode_method = True
            GPTState.user_overrode_form = True
            GPTState.user_overrode_channel = True
            gpt_module.settings.set("user.model_default_completeness", "full")
            gpt_module.settings.set("user.model_default_scope", "narrow")
            gpt_module.settings.set("user.model_default_method", "steps")
            gpt_module.settings.set("user.model_default_form", "bullets")
            gpt_module.settings.set("user.model_default_channel", "slack")

            gpt_module.UserActions.gpt_reset_default_completeness()
            gpt_module.UserActions.gpt_reset_default_scope()
            gpt_module.UserActions.gpt_reset_default_method()
            gpt_module.UserActions.gpt_reset_default_form()
            gpt_module.UserActions.gpt_reset_default_channel()

            self.assertFalse(GPTState.user_overrode_completeness)
            self.assertFalse(GPTState.user_overrode_scope)
            self.assertFalse(GPTState.user_overrode_method)
            self.assertFalse(GPTState.user_overrode_form)
            self.assertFalse(GPTState.user_overrode_channel)

        def test_gpt_suggest_prompt_recipes_parses_suggestions(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                # Arrange a suggestion-style response.
                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog\n"
                            "Name: Quick scan | Recipe: dependency · gist · relations · steps · plain · fog"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Deep map",
                            "recipe": "describe · full · relations · cluster · bullets · fog",
                        },
                        {
                            "name": "Quick scan",
                            "recipe": "dependency · gist · relations · steps · plain · fog",
                        },
                    ],
                )

        def test_gpt_suggest_prompt_recipes_parses_stance_and_why(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Teach junior dev | Recipe: describe · gist · focus · scaffold · plain · fog | Stance: model write as teacher to junior engineer kindly for teaching | Why: Kind, stepwise explanation for less-experienced devs"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Teach junior dev",
                            "recipe": "describe · gist · focus · scaffold · plain · fog",
                            "stance_command": "model write as teacher to junior engineer kindly for teaching",
                            "why": "Kind, stepwise explanation for less-experienced devs",
                        }
                    ],
                )

        def test_gpt_suggest_prompt_recipes_accepts_label_without_name_prefix(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Relational Overview | Recipe: describe · full · relations · cluster · plain · jog"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Relational Overview",
                            "recipe": "describe · full · relations · cluster · plain · jog",
                        }
                    ],
                )

        def test_gpt_suggest_prompt_recipes_accepts_missing_recipe_label_with_axes_tokens(
            self,
        ):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Credit-card model quick scan | describe · skim · focus · direct · plain · jog"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Credit-card model quick scan",
                            "recipe": "describe · skim · focus · direct · plain · jog",
                        }
                    ],
                )

        def test_gpt_suggest_prompt_recipes_allows_empty_source_when_subject_given(
            self,
        ):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = ""
                create_source.return_value = source
            mock_session = session_cls.return_value
            mock_session._destination = "paste"

            # Arrange a suggestion-style response so parsing succeeds.
            handle = self.pipeline.complete_async.return_value
            handle.wait = MagicMock(return_value=True)
            handle.result = PromptResult.from_messages(
                [
                    format_message(
                        "Relational Overview | Recipe: describe · full · relations · cluster · plain · jog"
                    )
                ]
            )

            gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Even with an empty source, providing a subject should still
            # drive a suggestion request and populate suggestions.
            self.assertEqual(
                GPTState.last_suggested_recipes,
                [
                    {
                        "name": "Relational Overview",
                        "recipe": "describe · full · relations · cluster · plain · jog",
                    }
                ],
            )

        def test_gpt_suggest_prompt_recipes_opens_suggestion_gui_when_available(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    actions.user, "model_prompt_recipe_suggestions_gui_open"
                ) as open_gui,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                # Arrange a suggestion-style response.
                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                open_gui.assert_called_once()

        def test_gpt_suggest_prompt_recipes_uses_prompt_session(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                create_source.assert_called_once()
                session_cls.assert_called_once()
            # Suggestion flow starts a fresh request rather than reusing
            # any in-flight GPTState.request to avoid leaking prior
            # prompt content into the meta-prompt.
            mock_session.begin.assert_called_once_with()
            mock_session.add_messages.assert_called_once()
            self.pipeline.complete_async.assert_called_once_with(mock_session)

        def test_gpt_suggest_prompt_recipes_opens_progress_pill(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(gpt_module, "emit_begin_send") as begin_send,
                patch.object(gpt_module, "emit_complete") as emit_complete,
                patch.object(gpt_module, "emit_fail") as emit_fail,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Quick idea | Recipe: describe · gist · actions · flow · plain · rog"
                        )
                    ]
                )
                begin_send.return_value = "req-suggest"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                begin_send.assert_called_once()
                emit_complete.assert_called_once_with(request_id="req-suggest")
                emit_fail.assert_not_called()

        def test_gpt_suggest_prompt_recipes_canonicalises_static_prompt(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Multi static | Recipe: ticket describe · full · relations · flow · plain · fog"
                        )
                    ]
                )

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

                # Static prompt should be collapsed to the first token ("ticket").
                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Multi static",
                            "recipe": "ticket · full · relations · flow · plain · fog",
                        }
                    ],
                )

        def test_gpt_suggest_prompt_recipes_requires_directional(self):
            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                handle.result = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Missing directional | Recipe: describe · full · relations · flow · plain"
                        )
                    ]
                )

            gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Suggestion should be dropped because it lacks a directional token.
            self.assertEqual(GPTState.last_suggested_recipes, [])

        def test_gpt_suggest_prompt_recipes_preserves_cache_on_source_error(self):
            cached = [
                {
                    "name": "Previous",
                    "recipe": "describe · full · relations · flow · plain · fog",
                }
            ]
            GPTState.last_suggested_recipes = list(cached)
            GPTState.last_suggest_source = "clipboard"

            with patch.object(gpt_module, "create_model_source") as create_source:
                source = MagicMock()
                source.get_text.side_effect = RuntimeError("no content")
                create_source.return_value = source

                gpt_module.UserActions.gpt_suggest_prompt_recipes("")

            # Cached suggestions should remain available when the source cannot be read.
            self.assertEqual(GPTState.last_suggested_recipes, cached)
            self.assertEqual(GPTState.last_suggest_source, "clipboard")
            self.pipeline.complete_async.assert_not_called()
            self.pipeline.complete.assert_not_called()

        def test_gpt_suggest_prompt_recipes_preserves_cache_when_no_input(self):
            cached = [
                {
                    "name": "Previous",
                    "recipe": "describe · full · relations · flow · plain · fog",
                }
            ]
            GPTState.last_suggested_recipes = list(cached)
            GPTState.last_suggest_source = "clipboard"

            with (
                patch.object(gpt_module, "PromptSession") as session_cls,
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                source.get_text.return_value = "   "
                create_source.return_value = source
                session_cls.return_value._destination = "paste"

                gpt_module.UserActions.gpt_suggest_prompt_recipes("")

            # When both subject and content are empty, leave the cached suggestions intact.
            self.assertEqual(GPTState.last_suggested_recipes, cached)
            self.assertEqual(GPTState.last_suggest_source, "clipboard")
            self.pipeline.complete_async.assert_not_called()
            self.pipeline.complete.assert_not_called()

        def test_gpt_suggest_prompt_recipes_honors_in_flight_guard(self):
            cached = [
                {
                    "name": "Previous",
                    "recipe": "describe · full · relations · flow · plain · fog",
                }
            ]
            GPTState.last_suggested_recipes = list(cached)
            GPTState.last_suggest_source = "clipboard"

            with (
                patch.object(gpt_module, "_reject_if_request_in_flight", return_value=True),
                patch.object(gpt_module, "create_model_source") as create_source,
            ):
                source = MagicMock()
                create_source.return_value = source

                gpt_module.UserActions.gpt_suggest_prompt_recipes("subject")

            # Guard should prevent new request; cached suggestions remain.
            self.assertEqual(GPTState.last_suggested_recipes, cached)
            self.pipeline.complete_async.assert_not_called()

        def test_gpt_pass_uses_prompt_session(self):
            configuration = MagicMock(
                model_source=MagicMock(),
                model_destination=MagicMock(),
            )
            configuration.model_source.format_messages.return_value = [
                format_message("pass")
            ]

            with patch.object(gpt_module, "PromptSession") as session_cls:
                session = session_cls.return_value

                gpt_module.UserActions.gpt_pass(configuration)

                session_cls.assert_called_once()
                session.prepare_prompt.assert_not_called()
                session.begin.assert_called_once_with(reuse_existing=True)
                session.execute.assert_not_called()
                actions.user.gpt_insert_response.assert_called_once()
                inserted_result = actions.user.gpt_insert_response.call_args.args[0]
                self.assertIsInstance(inserted_result, PromptResult)
                self.assertEqual(
                    inserted_result.messages,
                    configuration.model_source.format_messages.return_value,
                )
                self.assertIs(
                    actions.user.gpt_insert_response.call_args.args[1],
                    configuration.model_destination,
                )

        def test_gpt_pass_honors_in_flight_guard(self):
            configuration = MagicMock(
                model_source=MagicMock(),
                model_destination=MagicMock(),
            )
            configuration.model_source.format_messages.return_value = [
                format_message("pass")
            ]

            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ):
                gpt_module.UserActions.gpt_pass(configuration)

            actions.user.gpt_insert_response.assert_not_called()
            self.pipeline.run_async.assert_not_called()

        def test_gpt_query_honors_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(gpt_module, "send_request") as send_req:
                result = gpt_module.gpt_query()

            self.assertEqual(result, "")
            send_req.assert_not_called()

        def test_thread_toggle_does_not_build_session(self):
            actions.user.confirmation_gui_refresh_thread = MagicMock()
            with patch.object(gpt_module, "PromptSession") as session_cls:
                gpt_module.UserActions.gpt_enable_threading()
                session_cls.assert_not_called()

        def test_thread_push_uses_prompt_session(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                session = session_cls.return_value
                session._destination = "thread"
                handle = self.pipeline.complete_async.return_value
                handle.wait = MagicMock(return_value=True)
                result = PromptResult.from_messages([format_message("threaded")])
                handle.result = result

                with patch.object(gpt_module, "_handle_async_result") as handle_async:
                    GPTState.last_directional = "fog"
                    gpt_module.UserActions.gpt_replay("thread")

            session_cls.assert_called_once()
            session.begin.assert_called_once_with(reuse_existing=True)
            self.pipeline.complete_async.assert_called_with(session)
            handle_async.assert_called_once_with(handle, "thread", block=False)

        def test_thread_state_helpers_respect_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(GPTState, "new_thread") as new_thread:
                gpt_module.UserActions.gpt_clear_thread()
            new_thread.assert_not_called()

            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(GPTState, "enable_thread") as enable_thread, patch.object(
                GPTState, "disable_thread"
            ) as disable_thread:
                gpt_module.UserActions.gpt_enable_threading()
                gpt_module.UserActions.gpt_disable_threading()
            enable_thread.assert_not_called()
            disable_thread.assert_not_called()

        def test_context_push_respects_in_flight_guard(self):
            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(GPTState, "push_context") as push_ctx, patch.object(
                GPTState, "push_query"
            ) as push_query, patch.object(GPTState, "push_thread") as push_thread:
                gpt_module.UserActions.gpt_push_context("ctx")
                gpt_module.UserActions.gpt_push_query("q")
                gpt_module.UserActions.gpt_push_thread("t")
            push_ctx.assert_not_called()
            push_query.assert_not_called()
            push_thread.assert_not_called()

        def test_gpt_insert_response_has_type_annotations(self):
            sig = inspect.signature(gpt_module.UserActions.gpt_insert_response)
            param = sig.parameters["gpt_result"]
            self.assertIsNot(param.annotation, inspect._empty)
            destination_param = sig.parameters["destination"]
            self.assertIs(destination_param.annotation, ModelDestination)
            self.assertIs(sig.return_annotation, None)

        def test_gpt_recursive_prompt_uses_orchestrator(self):
            orchestrator = MagicMock()
            delegate_result = PromptResult.from_messages(
                [format_message("recursive result")]
            )

            class _Handle:
                def __init__(self, result):
                    self.result = result

                def wait(self, timeout=None):
                    return True

            orchestrator.run_async.return_value = _Handle(delegate_result)
            orchestrator.run.return_value = delegate_result
            with patch.object(gpt_module, "_recursive_orchestrator", orchestrator):
                source = MagicMock()
                destination = MagicMock()

                with patch.object(gpt_module, "_handle_async_result") as handle_async:
                    handle_async.side_effect = lambda h, d, block=False: setattr(
                        h, "result", h.result
                    )
                    result = gpt_module.UserActions.gpt_recursive_prompt(
                        "controller prompt", source, destination=destination
                    )

            orchestrator.run_async.assert_called_once_with(
                "controller prompt",
                source,
                destination,
                None,
            )
            orchestrator.run.assert_not_called()
            handle_async.assert_called_once()
            actions.user.gpt_insert_response.assert_called_once_with(
                delegate_result,
                destination,
            )
            self.assertEqual(result, "recursive result")

        def test_gpt_show_last_recipe_without_state_notifies_and_returns(self):
            GPTState.reset_all()
            with (
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(actions.app, "notify") as app_notify,
            ):
                gpt_module.UserActions.gpt_show_last_recipe()

                notify_mock.assert_called_once()
                app_notify.assert_not_called()

        def test_gpt_show_last_recipe_includes_directional_when_present(self):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · relations · cluster · bullets"
            GPTState.last_directional = "fog"

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_recipe()

                app_notify.assert_called_once_with(
                    "Last recipe: describe · full · relations · cluster · bullets · fog"
                )

        def test_gpt_show_last_recipe_omits_directional_when_absent(self):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · relations · cluster · bullets"
            GPTState.last_directional = ""

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_recipe()

                app_notify.assert_called_once_with(
                    "Last recipe: describe · full · relations · cluster · bullets"
                )

        def test_gpt_show_last_recipe_uses_last_axes_tokens_when_present(self):
            GPTState.reset_all()
            GPTState.last_recipe = "hydrated legacy string"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "hydrated"
            GPTState.last_scope = "hydrated scope"
            GPTState.last_method = "hydrated method"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
            }

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_recipe()

            app_notify.assert_called_once_with(
                "Last recipe: describe · full · bound edges · rigor · bullets · slack · fog"
            )

        def test_gpt_rerun_last_recipe_without_state_notifies_and_returns(self):
            GPTState.reset_all()

            with (
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(actions.user, "gpt_apply_prompt") as apply_mock,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
            ):
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], "", "", "")

                notify_mock.assert_called_once()
                apply_mock.assert_not_called()
                model_prompt.assert_not_called()

        def test_gpt_rerun_last_recipe_applies_overrides_on_last_tokens(self):
            # Seed last recipe state with token-based values.
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · relations · cluster · bullets"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "relations"
            GPTState.last_method = "cluster"
            GPTState.last_form = "bullets"
            GPTState.last_channel = "slack"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["relations"],
                "method": ["cluster"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
            }

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                # Override static prompt, completeness, and directional; reuse
                # last scope/method/form/channel. No explicit subject.
                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "todo", "gist", [], [], "rog", "", ""
                )

                # Axis mapping should be invoked for all non-empty axes.
                axis_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("gist", axis_tokens)
                self.assertIn("relations", axis_tokens)
                self.assertIn("cluster", axis_tokens)
                self.assertIn("rog", axis_tokens)

                # modelPrompt should receive a match object with merged axes.
                model_prompt.assert_called_once()
                match = model_prompt.call_args.args[0]
                self.assertEqual(match.staticPrompt, "todo")
                self.assertEqual(match.completenessModifier, "gist")
                self.assertEqual(match.scopeModifier, "relations")
                self.assertEqual(match.methodModifier, "cluster")
                self.assertEqual(match.formModifier, "bullets")
                self.assertEqual(match.channelModifier, "slack")
                self.assertEqual(match.directionalModifier, "rog")

                # Execution should go through the normal apply_prompt path.
                apply_prompt.assert_called_once()
                config = apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT")
                self.assertIs(config.model_source, source)
                self.assertIs(config.model_destination, destination)

        def test_gpt_rerun_last_recipe_honors_in_flight_guard(self):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": [],
                "method": [],
                "form": [],
                "channel": [],
                "directional": ["fog"],
            }

            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.user, "gpt_apply_prompt", MagicMock()) as apply_mock:
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], "fog", "", "")

            self.assertFalse(apply_mock.called)

        def test_gpt_rerun_last_recipe_with_source_honors_in_flight_guard(self):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": [],
                "method": [],
                "form": [],
                "channel": [],
                "directional": ["fog"],
            }

            class DummySource:
                modelSimpleSource = "clipboard"

            with patch.object(
                gpt_module, "_reject_if_request_in_flight", return_value=True
            ), patch.object(actions.user, "gpt_apply_prompt", MagicMock()) as apply_mock:
                gpt_module.UserActions.gpt_rerun_last_recipe_with_source(
                    DummySource(), "", "", [], [], "fog", "", ""
                )

            self.assertFalse(apply_mock.called)

        def test_gpt_rerun_last_recipe_merges_multi_tag_axes_with_canonicalisation(
            self,
        ):
            """Seed multi-token last_* axes and ensure rerun respects canonicalisation."""
            GPTState.reset_all()
            # Simulate a previous multi-tag axis state.
            GPTState.last_recipe = (
                "describe · full · narrow focus · cluster · adr table"
            )
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "narrow focus"
            GPTState.last_method = "cluster"
            GPTState.last_form = "adr table"
            GPTState.last_directional = "fog"

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ),
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT-MULTI"

                # Override scope and form with additional tokens; method left unchanged.
                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "todo",
                    "",  # completeness override (none)
                    ["bound"],  # new scope token to merge
                    [],  # method unchanged
                    "rog",  # new directional
                    "bullets",  # additional form token to merge
                    "",  # channel unchanged
                )

                # modelPrompt should receive a match with merged axis modifiers.
                model_prompt.assert_called_once()
                match = model_prompt.call_args.args[0]
                self.assertEqual(match.staticPrompt, "todo")
                # Completeness inherited from last state.
                self.assertEqual(match.completenessModifier, "full")
                # Scope should now be a canonicalised, capped set rendered as a string.
                # With a scope cap of 2 and base "narrow focus" plus "bound", we expect
                # the most recent two tokens, canonicalised; the exact policy is owned
                # by the normaliser, but we at least assert that:
                self.assertIsInstance(match.scopeModifier, str)
                self.assertTrue(match.scopeModifier)
                for token in match.scopeModifier.split():
                    self.assertIn(token, {"narrow", "focus", "bound"})
                # Method unchanged.
                self.assertEqual(match.methodModifier, "cluster")
                # Form should enforce singleton cap and use the latest token.
                self.assertEqual(match.formModifier, "bullets")
                self.assertEqual(match.directionalModifier, "rog")

                # State should be updated using the canonical serialisation helpers.
                self.assertEqual(GPTState.last_static_prompt, "todo")
                self.assertEqual(GPTState.last_completeness, "full")
                self.assertEqual(GPTState.last_directional, "rog")
                # Scope/method/style should be non-empty strings with tokens drawn from
                # the expected sets; exact ordering is owned by the normaliser.
                self.assertTrue(GPTState.last_scope)
                for token in GPTState.last_scope.split():
                    self.assertIn(token, {"narrow", "focus", "bound"})

                self.assertEqual(GPTState.last_method, "cluster")

                # Execution should still go through the normal apply_prompt path.
                apply_prompt.assert_called_once()
                config = apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT-MULTI")
                self.assertIs(config.model_source, source)
                self.assertIs(config.model_destination, destination)

        def test_gpt_rerun_last_recipe_prefers_last_axes_tokens(self):
            """Ensure rerun uses token-only last_axes even if legacy recipe is hydrated/mismatched."""
            GPTState.reset_all()
            GPTState.last_recipe = "hydrated legacy string"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "hydrated-completeness"
            GPTState.last_scope = "hydrated-scope"
            GPTState.last_method = "hydrated-method"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
            }
            # Inject some hydrated/unknown tokens to ensure they are dropped.
            GPTState.last_axes["scope"].append("Hydrated scope")
            GPTState.last_axes["method"].append("Unknown method")

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], "rog", "", "")

            mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
            self.assertIn("full", mapped_tokens)
            self.assertIn("bound edges", mapped_tokens)
            self.assertIn("rigor", mapped_tokens)
            self.assertIn("rog", mapped_tokens)

            match = model_prompt.call_args.args[0]
            self.assertEqual(match.staticPrompt, "infer")
            self.assertEqual(match.completenessModifier, "full")
            self.assertEqual(match.scopeModifier, "bound edges")
            self.assertEqual(match.methodModifier, "rigor")
            self.assertEqual(match.formModifier, "bullets")
            self.assertEqual(match.channelModifier, "slack")

            self.assertEqual(
                GPTState.last_recipe,
                "infer · full · bound edges · rigor · bullets · slack · rog",
            )

        def test_history_then_rerun_keeps_last_axes_token_only(self):
            """End-to-end guardrail: history ingest + rerun keeps axes token-only."""
            GPTState.reset_all()
            clear_history()
            axes = {
                "completeness": ["full", "Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["adr", "Hydrated form"],
            }
            append_entry(
                "rid-axes",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="legacy · should · be · ignored",
                axes=axes,
            )

            HistoryActions.gpt_request_history_show_latest()
            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor"],
                    "form": ["adr"],
                    "channel": [],
                    "directional": [],
                },
            )

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], "rog", "", "")

            mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
            self.assertTrue(
                {"full", "bound", "rigor", "rog"}.issubset(set(mapped_tokens))
            )
            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor"],
                    "form": ["adr"],
                    "channel": [],
                    "directional": ["rog"],
                },
            )

        def test_rerun_override_method_multi_tokens_preserved(self):
            """Overriding method with multiple tokens should preserve all known tokens."""
            GPTState.reset_all()
            GPTState.last_recipe = "infer · full · bound · xp"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "bound"
            GPTState.last_method = "xp"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["xp"],
                "form": ["code"],
                "channel": ["slack"],
                "directional": ["jog"],
            }

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "",
                    "",
                    [],
                    ["xp", "rigor"],
                    "",
                    "",
                )

                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("rigor xp", mapped_tokens)
                self.assertIn("jog", mapped_tokens)

            match = model_prompt.call_args.args[0]
            self.assertEqual(match.methodModifier, "rigor xp")
            self.assertEqual(match.formModifier, "code")
            self.assertEqual(match.channelModifier, "slack")

            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor", "xp"],
                    "form": ["code"],
                    "channel": ["slack"],
                    "directional": ["jog"],
                },
            )

        def test_rerun_requires_directional(self):
            """Guardrail: rerun should refuse when no directional is available."""
            GPTState.reset_all()
            GPTState.last_recipe = "infer · full · bound · rigor · plain"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "bound"
            GPTState.last_method = "rigor"
            GPTState.last_form = "plain"
            GPTState.last_channel = "slack"
            GPTState.last_directional = ""
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["rigor"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": [],
            }

            with patch.object(gpt_module, "modelPrompt") as model_prompt, patch.object(
                gpt_module.actions.user, "gpt_apply_prompt"
            ) as apply_prompt, patch.object(
                gpt_module.actions.user, "notify"
            ) as user_notify:
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], "", "", "")

            model_prompt.assert_not_called()
            apply_prompt.assert_not_called()
            self.assertTrue(
                any("directional" in str(call.args[0]).lower() for call in user_notify.call_args_list)
            )

        def test_gpt_rerun_last_recipe_filters_unknown_directional(self):
            """Directional overrides should be validated and capped to one token."""
            GPTState.reset_all()
            GPTState.last_recipe = "infer · full · bound · rigor · plain · fog"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "bound"
            GPTState.last_method = "rigor"
            GPTState.last_form = "plain"
            GPTState.last_channel = "slack"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["rigor"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            }

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "",
                    "",
                    [],
                    [],
                    "invalid-directional",
                    "",
                    "",
                )

            mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
            self.assertIn("fog", mapped_tokens)
            self.assertNotIn("invalid-directional", mapped_tokens)
            match = model_prompt.call_args.args[0]
            self.assertEqual(match.directionalModifier, "fog")
            self.assertEqual(GPTState.last_axes.get("directional"), ["fog"])

        def test_gpt_rerun_last_recipe_filters_unknown_override_tokens(self):
            """Overrides containing unknown/hydrated tokens should be dropped, preserving known tokens."""
            GPTState.reset_all()
            GPTState.last_recipe = "infer · full · bound · rigor · plain"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "bound"
            GPTState.last_method = "rigor"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["rigor"],
                "form": ["adr"],
                "channel": ["slack"],
                "directional": ["fog"],
            }

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ) as axis_value,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT"

                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "",
                    "full",  # valid completeness
                    ["bound", "invalid-scope"],  # one valid, one invalid
                    ["rigor", "hydrated-method"],  # one valid, one invalid
                    "fig",
                    "bullets",
                    "html",
                )

                # Only known tokens should be mapped.
                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("full", mapped_tokens)
                self.assertIn("bound", mapped_tokens)
                self.assertIn("rigor", mapped_tokens)
                self.assertIn("fig", mapped_tokens)
                self.assertNotIn("invalid-scope", mapped_tokens)
                self.assertNotIn("hydrated-method", mapped_tokens)
                self.assertNotIn("UnknownStyle", mapped_tokens)

                match = model_prompt.call_args.args[0]
                self.assertEqual(match.scopeModifier, "bound")
                self.assertEqual(match.methodModifier, "rigor")
            self.assertEqual(match.formModifier, "bullets")
            self.assertEqual(match.channelModifier, "html")

            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor"],
                    "form": ["bullets"],
                    "channel": ["html"],
                    "directional": ["fig"],
                },
            )

        def test_gpt_apply_prompt_refuses_when_request_in_flight(self):
            """A new request should be rejected if one is already running."""
            running_state = MagicMock()
            running_state.phase = RequestPhase.SENDING

            with (
                patch.object(gpt_module, "current_state", return_value=running_state),
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(
                    gpt_module._prompt_pipeline, "run_async"
                ) as run_async_mock,
            ):
                config = ApplyPromptConfiguration(
                    please_prompt="PROMPT",
                    model_source=MagicMock(),
                    additional_model_source=None,
                    model_destination=MagicMock(),
                )
                gpt_module.UserActions.gpt_apply_prompt(config)

                notify_mock.assert_called_once()
                run_async_mock.assert_not_called()

        def test_gpt_run_prompt_refuses_when_request_in_flight(self):
            """Direct prompt runs should be rejected if one is already running."""
            running_state = MagicMock()
            running_state.phase = RequestPhase.SENDING

            with (
                patch.object(gpt_module, "current_state", return_value=running_state),
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(
                    gpt_module._prompt_pipeline, "run_async"
                ) as run_async_mock,
            ):
                gpt_module.UserActions.gpt_run_prompt("PROMPT", MagicMock())

                notify_mock.assert_called_once()
                run_async_mock.assert_not_called()

        def test_gpt_recursive_prompt_refuses_when_request_in_flight(self):
            """Recursive prompt runs should be rejected if one is already running."""
            running_state = MagicMock()
            running_state.phase = RequestPhase.SENDING

            with (
                patch.object(gpt_module, "current_state", return_value=running_state),
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(
                    gpt_module._recursive_orchestrator, "run_async"
                ) as run_async_mock,
            ):
                gpt_module.UserActions.gpt_recursive_prompt("PROMPT", MagicMock())

                notify_mock.assert_called_once()
                run_async_mock.assert_not_called()

        def test_gpt_replay_refuses_when_request_in_flight(self):
            """Replays should be rejected if one is already running."""
            running_state = MagicMock()
            running_state.phase = RequestPhase.SENDING
            GPTState.last_directional = "fog"

            with (
                patch.object(gpt_module, "current_state", return_value=running_state),
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(
                    gpt_module._prompt_pipeline, "complete_async"
                ) as complete_async_mock,
            ):
                gpt_module.UserActions.gpt_replay(destination="window")

                notify_mock.assert_called_once()
                complete_async_mock.assert_not_called()

        def test_gpt_analyze_refuses_when_request_in_flight(self):
            """Analyze should be rejected if one is already running."""
            running_state = MagicMock()
            running_state.phase = RequestPhase.SENDING

            with (
                patch.object(gpt_module, "current_state", return_value=running_state),
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(
                    gpt_module._prompt_pipeline, "complete_async"
                ) as complete_async_mock,
            ):
                gpt_module.UserActions.gpt_analyze_prompt()

                notify_mock.assert_called_once()
                complete_async_mock.assert_not_called()

        def test_gpt_rerun_last_recipe_notifies_when_axis_tokens_are_dropped(
            self,
        ):
            """Rerun should surface a hint when axis tokens are dropped."""
            GPTState.reset_all()
            # Seed a last recipe that includes excess form tokens (cap 1).
            GPTState.last_recipe = "describe · full · narrow · steps · adr table"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "narrow"
            GPTState.last_method = "steps"
            GPTState.last_form = "adr table"
            GPTState.last_directional = "fog"

            with (
                patch.object(
                    gpt_module,
                    "_axis_value_from_token",
                    side_effect=lambda token, mapping: token,
                ),
                patch.object(gpt_module, "modelPrompt") as model_prompt,
                patch.object(gpt_module, "create_model_source") as create_source,
                patch.object(
                    gpt_module, "create_model_destination"
                ) as create_destination,
                patch.object(actions.user, "gpt_apply_prompt") as apply_prompt,
                patch.object(gpt_module, "notify") as notify_mock,
            ):
                source = MagicMock()
                destination = MagicMock()
                create_source.return_value = source
                create_destination.return_value = destination
                model_prompt.return_value = "PROMPT-CONFLICT"

                # No overrides; rerun should apply caps to form/channel and surface a hint.
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", "", "", "", "rog")

                notify_mock.assert_called()
                message = notify_mock.call_args.args[0]
                self.assertIn("Axes normalised", message)
                self.assertIn("form=", message)
else:
    if not TYPE_CHECKING:

        class GPTActionPromptSessionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
