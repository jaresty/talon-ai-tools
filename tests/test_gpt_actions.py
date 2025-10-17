import unittest
from unittest.mock import patch, MagicMock

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
else:
    class GPTActionPromptSessionTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
