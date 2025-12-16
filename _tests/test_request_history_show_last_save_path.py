import os
import tempfile
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
    from talon_user.lib import requestHistoryActions as history_actions
    from talon_user.lib.requestHistoryActions import UserActions as HistoryActions
    from talon_user.lib.modelState import GPTState

    class RequestHistoryShowPathTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.last_history_save_path = ""

        def test_show_last_save_path_notifies_when_missing(self) -> None:
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_show_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertIn("model history save exchange", str(notify_mock.call_args[0][0]))

        def test_show_last_save_path_notifies_and_returns_path(self) -> None:
            tmpdir = tempfile.mkdtemp()
            path = os.path.join(tmpdir, "saved-history.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = path
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_show_last_save_path()
            notify_mock.assert_called()
            self.assertEqual(result, os.path.realpath(path))

else:
    if not TYPE_CHECKING:
        class RequestHistoryShowPathTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
