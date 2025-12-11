import inspect
import os
import tempfile
import unittest
from typing import TYPE_CHECKING
from unittest.mock import ANY, MagicMock, patch

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

            gpt_module.UserActions.gpt_show_last_meta()

            # The stub app namespace records notify calls.
            self.assertTrue(
                any(
                    "Last meta interpretation:" in call[1][0]
                    for call in actions.app.calls
                ),
                "Expected a notification containing the last meta interpretation",
            )

        def test_gpt_show_last_meta_notifies_when_missing(self):
            GPTState.last_meta = ""

            gpt_module.UserActions.gpt_show_last_meta()

            self.assertTrue(
                any(
                    "No last meta interpretation available" in call[1][0]
                    for call in actions.app.calls
                ),
                "Expected a notification when no last meta is available",
            )

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

        def test_gpt_replay_non_blocking_calls_handle_async_with_block_false(self):
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
            gpt_module.UserActions.gpt_set_async_blocking(1)
            self.assertTrue(gpt_module.settings.get("user.model_async_blocking"))
            self.assertTrue(
                any(call[0] == "notify" for call in actions.app.calls),
                "Expected a notification when toggling async mode",
            )

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
                    gpt_module.UserActions.gpt_replay("thread")

            session_cls.assert_called_once()
            session.begin.assert_called_once_with(reuse_existing=True)
            self.pipeline.complete_async.assert_called_with(session)
            handle_async.assert_called_once_with(handle, "thread", block=False)

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
            GPTState.last_style = "hydrated style"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor"],
                "style": ["plain"],
            }

            with patch.object(actions.app, "notify") as app_notify:
                gpt_module.UserActions.gpt_show_last_recipe()

            app_notify.assert_called_once_with(
                "Last recipe: describe · full · bound edges · rigor · plain · fog"
            )

        def test_gpt_rerun_last_recipe_without_state_notifies_and_returns(self):
            GPTState.reset_all()

            with (
                patch.object(gpt_module, "notify") as notify_mock,
                patch.object(actions.user, "gpt_apply_prompt") as apply_mock,
                patch.object(gpt_module, "modelPrompt") as model_prompt,
            ):
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", "", "", "", "")

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
            GPTState.last_style = "bullets"
            GPTState.last_directional = "fog"

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
                # last scope/method/style. No explicit subject.
                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "todo", "gist", [], [], [], "rog"
                )

                # Axis mapping should be invoked for all non-empty axes.
                axis_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("gist", axis_tokens)
                self.assertIn("relations", axis_tokens)
                self.assertIn("cluster", axis_tokens)
                self.assertIn("bullets", axis_tokens)
                self.assertIn("rog", axis_tokens)

                # modelPrompt should receive a match object with merged axes.
                model_prompt.assert_called_once()
                match = model_prompt.call_args.args[0]
                self.assertEqual(match.staticPrompt, "todo")
                self.assertEqual(match.completenessModifier, "gist")
                self.assertEqual(match.scopeModifier, "relations")
                self.assertEqual(match.methodModifier, "cluster")
                self.assertEqual(match.styleModifier, "bullets")
                self.assertEqual(match.directionalModifier, "rog")

                # Execution should go through the normal apply_prompt path.
                apply_prompt.assert_called_once()
                config = apply_prompt.call_args.args[0]
                self.assertEqual(config.please_prompt, "PROMPT")
                self.assertIs(config.model_source, source)
                self.assertIs(config.model_destination, destination)

        def test_gpt_rerun_last_recipe_merges_multi_tag_axes_with_canonicalisation(
            self,
        ):
            """Seed multi-token last_* axes and ensure rerun respects canonicalisation."""
            GPTState.reset_all()
            # Simulate a previous multi-tag axis state.
            GPTState.last_recipe = (
                "describe · full · narrow focus · cluster · jira story"
            )
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "narrow focus"
            GPTState.last_method = "cluster"
            GPTState.last_style = "jira story"
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

                # Override scope and style with additional tokens; method left unchanged.
                gpt_module.UserActions.gpt_rerun_last_recipe(
                    "todo",
                    "",  # completeness override (none)
                    ["bound"],  # new scope token to merge
                    [],  # method unchanged
                    ["bullets"],  # additional style token to merge
                    "rog",  # new directional
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
                # Style should merge "jira story" with "bullets" under the style cap.
                self.assertIsInstance(match.styleModifier, str)
                self.assertTrue(match.styleModifier)
                for token in match.styleModifier.split():
                    self.assertIn(token, {"jira", "story", "bullets"})
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

                self.assertTrue(GPTState.last_style)
                for token in GPTState.last_style.split():
                    self.assertIn(token, {"jira", "story", "bullets"})

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
            GPTState.last_style = "hydrated-style"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor"],
                "style": ["plain"],
            }
            # Inject some hydrated/unknown tokens to ensure they are dropped.
            GPTState.last_axes["scope"].append("Hydrated scope")
            GPTState.last_axes["method"].append("Unknown method")
            GPTState.last_axes["style"].append("Fancy hydrated style")

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

                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], [], "rog")

                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("full", mapped_tokens)
                self.assertIn("bound edges", mapped_tokens)
                self.assertIn("rigor", mapped_tokens)
                self.assertIn("plain", mapped_tokens)

                match = model_prompt.call_args.args[0]
                self.assertEqual(match.staticPrompt, "infer")
                self.assertEqual(match.completenessModifier, "full")
                self.assertEqual(match.scopeModifier, "bound edges")
                self.assertEqual(match.methodModifier, "rigor")
                self.assertEqual(match.styleModifier, "plain")

                self.assertEqual(
                    GPTState.last_recipe, "infer · full · bound edges · rigor · plain"
                )
                self.assertEqual(GPTState.last_completeness, "full")
                self.assertEqual(GPTState.last_scope, "bound edges")
                self.assertEqual(GPTState.last_method, "rigor")
                self.assertEqual(GPTState.last_style, "plain")
                self.assertEqual(
                    GPTState.last_axes,
                    {
                        "completeness": ["full"],
                        "scope": ["bound", "edges"],
                        "method": ["rigor"],
                        "style": ["plain"],
                    },
                )

        def test_history_then_rerun_keeps_last_axes_token_only(self):
            """End-to-end guardrail: history ingest + rerun keeps axes token-only."""
            GPTState.reset_all()
            clear_history()
            axes = {
                "completeness": ["full", "Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "style": ["plain", "Fancy hydrated style"],
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
                    "style": ["plain"],
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

                gpt_module.UserActions.gpt_rerun_last_recipe("", "", [], [], [], "rog")

                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertTrue(
                    {"full", "bound", "rigor", "plain"}.issubset(set(mapped_tokens))
                )
                self.assertEqual(
                    GPTState.last_axes,
                    {
                        "completeness": ["full"],
                        "scope": ["bound"],
                        "method": ["rigor"],
                        "style": ["plain"],
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
            GPTState.last_style = "plain"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["xp"],
                "style": ["plain"],
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
                    [],
                    "",
                )

                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("rigor xp", mapped_tokens)

                match = model_prompt.call_args.args[0]
                self.assertEqual(match.methodModifier, "rigor xp")

                self.assertEqual(
                    GPTState.last_axes,
                    {
                        "completeness": ["full"],
                        "scope": ["bound"],
                        "method": ["rigor", "xp"],
                        "style": ["plain"],
                    },
                )

        def test_gpt_rerun_last_recipe_filters_unknown_override_tokens(self):
            """Overrides containing unknown/hydrated tokens should be dropped, preserving known tokens."""
            GPTState.reset_all()
            GPTState.last_recipe = "infer · full · bound · rigor · plain"
            GPTState.last_static_prompt = "infer"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "bound"
            GPTState.last_method = "rigor"
            GPTState.last_style = "plain"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["bound"],
                "method": ["rigor"],
                "style": ["plain"],
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
                    ["plain", "UnknownStyle"],  # one valid, one invalid
                    "",
                )

                # Only known tokens should be mapped.
                mapped_tokens = [call.args[0] for call in axis_value.call_args_list]
                self.assertIn("full", mapped_tokens)
                self.assertIn("bound", mapped_tokens)
                self.assertIn("rigor", mapped_tokens)
                self.assertIn("plain", mapped_tokens)
                self.assertNotIn("invalid-scope", mapped_tokens)
                self.assertNotIn("hydrated-method", mapped_tokens)
                self.assertNotIn("UnknownStyle", mapped_tokens)

                match = model_prompt.call_args.args[0]
                self.assertEqual(match.scopeModifier, "bound")
                self.assertEqual(match.methodModifier, "rigor")
                self.assertEqual(match.styleModifier, "plain")

                self.assertEqual(
                    GPTState.last_axes,
                    {
                        "completeness": ["full"],
                        "scope": ["bound"],
                        "method": ["rigor"],
                        "style": ["plain"],
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
            # Seed a last recipe that includes incompatible style tokens.
            GPTState.last_recipe = "describe · full · narrow · steps · jira adr"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "narrow"
            GPTState.last_method = "steps"
            GPTState.last_style = "jira adr"
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

                # No overrides; rerun should apply incompatibility rules to
                # the existing style axis and surface a hint.
                gpt_module.UserActions.gpt_rerun_last_recipe("", "", "", "", "", "rog")

                notify_mock.assert_called()
                message = notify_mock.call_args.args[0]
                self.assertIn("Axes normalised", message)
                self.assertIn("style=jira adr", message)
else:
    if not TYPE_CHECKING:

        class GPTActionPromptSessionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
