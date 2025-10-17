import unittest
from unittest.mock import ANY, MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.GPT import gpt as gpt_module

    class GPTActionPromptSessionTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            GPTState.last_response = "assistant output"
            actions.user.gpt_insert_response = MagicMock()

        def test_gpt_analyze_prompt_uses_prompt_session(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session.execute.return_value = {"type": "text", "text": "analysis"}

                gpt_module.UserActions().gpt_analyze_prompt()

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                mock_session.add_messages.assert_called_once()
                mock_session.execute.assert_called_once()
                actions.user.gpt_insert_response.assert_called_once()
                call_args = actions.user.gpt_insert_response.call_args
                self.assertEqual(
                    call_args.args[0], [mock_session.execute.return_value]
                )

        def test_gpt_apply_prompt_uses_prompt_session(self):
            configuration = MagicMock(
                please_prompt="do something",
                model_source=MagicMock(),
                additional_model_source=None,
                model_destination=MagicMock(),
            )

            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session.execute.return_value = {"type": "text", "text": "result"}

                result = gpt_module.UserActions.gpt_apply_prompt(configuration)

                session_cls.assert_called_once()
                mock_session.prepare_prompt.assert_called_once_with(
                    configuration.please_prompt,
                    configuration.model_source,
                    configuration.additional_model_source,
                )
                mock_session.execute.assert_called_once()
                actions.user.gpt_insert_response.assert_called_once_with(
                    [mock_session.execute.return_value],
                    configuration.model_destination,
                )
                self.assertEqual(result, mock_session.execute.return_value)

        def test_gpt_replay_uses_prompt_session_output(self):
            with patch.object(gpt_module, "PromptSession") as session_cls:
                mock_session = session_cls.return_value
                mock_session.execute.return_value = {"type": "text", "text": "replayed"}

                gpt_module.UserActions.gpt_replay("paste")

                session_cls.assert_called_once()
                mock_session.begin.assert_called_once_with(reuse_existing=True)
                mock_session.execute.assert_called_once()
                actions.user.gpt_insert_response.assert_called_once_with(
                    mock_session.execute.return_value,
                    "paste",
                )

        def test_gpt_reformat_last_uses_prompt_session(self):
            actions.user.get_last_phrase = lambda: "spoken"
            actions.user.clear_last_phrase = lambda: None

            with patch.object(gpt_module, "PromptSession") as session_cls, patch.object(
                gpt_module, "create_model_source"
            ) as create_source, patch.object(
                gpt_module, "extract_message", side_effect=lambda msg: msg["text"]
            ):
                source = MagicMock()
                create_source.return_value = source
                session = session_cls.return_value
                session.execute.return_value = {"type": "text", "text": "formatted"}

                result = gpt_module.UserActions.gpt_reformat_last("as code")

                session_cls.assert_called_once()
                create_source.assert_called_once_with("last")
                session.prepare_prompt.assert_called_once_with(ANY, source)
                session.execute.assert_called_once()
                self.assertEqual(result, "formatted")

        def test_gpt_pass_uses_prompt_session(self):
            configuration = MagicMock(
                model_source=MagicMock(),
                model_destination=MagicMock(),
            )

            with patch.object(gpt_module, "PromptSession") as session_cls:
                session = session_cls.return_value

                gpt_module.UserActions.gpt_pass(configuration)

                session_cls.assert_called_once()
                session.prepare_prompt.assert_not_called()
                session.begin.assert_called_once_with(reuse_existing=True)
                session.execute.assert_not_called()
                actions.user.gpt_insert_response.assert_called_once_with(
                    configuration.model_source.format_messages(),
                    configuration.model_destination,
                )
else:
    class GPTActionPromptSessionTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
