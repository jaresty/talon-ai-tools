import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.GPT import gpt as gpt_module

    class ThreadingIntegrationTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            actions.user.confirmation_gui_refresh_thread = MagicMock()

        @patch.object(gpt_module, "PromptSession")
        def test_thread_enable_and_replay(self, session_cls):
            session = session_cls.return_value
            session.execute.return_value = {"type": "text", "text": "reply"}

            gpt_module.UserActions.gpt_enable_threading()
            GPTState.query = []
            GPTState.last_directional = "fog"
            gpt_module.UserActions.gpt_replay("paste")

            session_cls.assert_called()
            self.assertTrue(GPTState.thread_enabled)

else:
    if not TYPE_CHECKING:
        class ThreadingIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass


if __name__ == "__main__":
    unittest.main()
