import inspect
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
    from talon import actions
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelDestination import ModelDestination
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.GPT import gpt as gpt_module

    class GPTActionPromptSessionTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            GPTState.last_response = "assistant output"
            actions.user.gpt_insert_response = MagicMock()
            self._original_pipeline = gpt_module._prompt_pipeline
            self.pipeline = MagicMock()
            self.pipeline.complete.return_value = PromptResult.from_messages(
                [format_message("analysis")]
            )
            self.pipeline.run.return_value = PromptResult.from_messages(
                [format_message("result")]
            )
            gpt_module._prompt_pipeline = self.pipeline
            self._original_orchestrator = gpt_module._recursive_orchestrator
            self.orchestrator = MagicMock()
            self.orchestrator.run.return_value = PromptResult.from_messages(
                [format_message("orchestrated")]
            )
            gpt_module._recursive_orchestrator = self.orchestrator

        def tearDown(self):
            gpt_module._prompt_pipeline = self._original_pipeline
            gpt_module._recursive_orchestrator = self._original_orchestrator

        def test_gpt_analyze_prompt_uses_prompt_session(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value

                gpt_module.UserActions().gpt_analyze_prompt()

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                mock_session.add_messages.assert_called_once()
                self.pipeline.complete.assert_called_once_with(mock_session)
                actions.user.gpt_insert_response.assert_called_once_with(
                    self.pipeline.complete.return_value,
                    session_cls.call_args.args[0],
                )

        def test_gpt_apply_prompt_uses_recursive_orchestrator(self):
            configuration = MagicMock(
                please_prompt="do something",
                model_source=MagicMock(),
                additional_model_source=None,
                model_destination=MagicMock(),
            )
            delegate_result = PromptResult.from_messages(
                [format_message("delegated output")]
            )
            result_text = gpt_module.UserActions.gpt_apply_prompt(configuration)

            self.orchestrator.run.assert_called_once_with(
                configuration.please_prompt,
                configuration.model_source,
                configuration.model_destination,
                configuration.additional_model_source,
            )
            actions.user.gpt_insert_response.assert_called_once_with(
                self.orchestrator.run.return_value,
                configuration.model_destination,
            )
            self.assertEqual(result_text, "orchestrated")

        def test_gpt_replay_uses_prompt_session_output(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session._destination = "paste"
                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [format_message("replayed")]
                )

                gpt_module.UserActions.gpt_replay("paste")

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                self.pipeline.complete.assert_called_once_with(mock_session)
                actions.user.gpt_insert_response.assert_called_once_with(
                    self.pipeline.complete.return_value,
                    "paste",
                )

        def test_gpt_reformat_last_uses_prompt_pipeline(self):
            actions.user.get_last_phrase = lambda: "spoken"
            actions.user.clear_last_phrase = lambda: None

            with patch.object(gpt_module, "create_model_source") as create_source:
                source = MagicMock()
                create_source.return_value = source
                self.pipeline.run.return_value = PromptResult.from_messages(
                    [format_message("formatted")]
                )

                result = gpt_module.UserActions.gpt_reformat_last("as code")

                create_source.assert_called_once_with("last")
                self.pipeline.run.assert_called_once()
                self.assertEqual(result, "formatted")

        def test_gpt_run_prompt_returns_pipeline_text(self):
            source = MagicMock()

            text = gpt_module.UserActions.gpt_run_prompt("question", source)

            self.pipeline.run.assert_called_once()
            args, kwargs = self.pipeline.run.call_args
            self.assertEqual(args[0:2], ("question", source))
            self.assertEqual(kwargs.get("destination"), "")
            self.assertIsNone(kwargs.get("additional_source"))
            self.assertEqual(text, "result")

        def test_gpt_suggest_prompt_recipes_parses_suggestions(self):
            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source:
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                # Arrange a suggestion-style response.
                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog\n"
                            "Name: Quick scan | Recipe: dependency · gist · relations · steps · plain · fog"
                        )
                    ]
                )

                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

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
            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source:
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [
                        format_message(
                            "Relational Overview | Recipe: describe · full · relations · cluster · plain · jog"
                        )
                    ]
                )

                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

                self.assertEqual(
                    GPTState.last_suggested_recipes,
                    [
                        {
                            "name": "Relational Overview",
                            "recipe": "describe · full · relations · cluster · plain · jog",
                        }
                    ],
                )

        def test_gpt_suggest_prompt_recipes_allows_empty_source_when_subject_given(self):
            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source:
                source = MagicMock()
                source.get_text.return_value = ""
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                # Arrange a suggestion-style response so parsing succeeds.
                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [
                        format_message(
                            "Relational Overview | Recipe: describe · full · relations · cluster · plain · jog"
                        )
                    ]
                )

                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

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
            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source, patch.object(
                actions.user, "model_prompt_recipe_suggestions_gui_open"
            ) as open_gui:
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                # Arrange a suggestion-style response.
                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [
                        format_message(
                            "Name: Deep map | Recipe: describe · full · relations · cluster · bullets · fog"
                        )
                    ]
                )

                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

                open_gui.assert_called_once()

        def test_gpt_suggest_prompt_recipes_uses_prompt_session(self):
            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source:
                source = MagicMock()
                source.get_text.return_value = "content"
                create_source.return_value = source
                mock_session = session_cls.return_value
                mock_session._destination = "paste"

                gpt_module.UserActions().gpt_suggest_prompt_recipes("subject")

                create_source.assert_called_once()
                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                mock_session.add_messages.assert_called_once()
                self.pipeline.complete.assert_called_once_with(mock_session)
                actions.user.gpt_insert_response.assert_called_once_with(
                    self.pipeline.complete.return_value,
                    mock_session._destination,
                )


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
                self.pipeline.complete.return_value = PromptResult.from_messages(
                    [format_message("threaded")]
                )

                gpt_module.UserActions.gpt_replay("thread")

                session_cls.assert_called_once()
                session.begin.assert_called_once_with(reuse_existing=True)
                self.pipeline.complete.assert_called_with(session)

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
            orchestrator.run.return_value = delegate_result
            with patch.object(gpt_module, "_recursive_orchestrator", orchestrator):
                source = MagicMock()
                destination = MagicMock()

                result = gpt_module.UserActions.gpt_recursive_prompt(
                    "controller prompt", source, destination=destination
                )

            orchestrator.run.assert_called_once_with(
                "controller prompt",
                source,
                destination,
                None,
            )
            actions.user.gpt_insert_response.assert_called_once_with(
                delegate_result,
                destination,
            )
            self.assertEqual(result, "recursive result")
else:
    if not TYPE_CHECKING:
        class GPTActionPromptSessionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
