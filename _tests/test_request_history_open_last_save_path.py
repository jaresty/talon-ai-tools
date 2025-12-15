import os
import sys
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

    class RequestHistoryOpenPathTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.last_history_save_path = ""

        def test_open_last_save_path_notifies_when_missing(self) -> None:
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_open_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertIn("model history save source", str(notify_mock.call_args[0][0]))

        def test_open_last_save_path_opens_when_available(self) -> None:
            tmpdir = tempfile.mkdtemp()
            path = os.path.join(tmpdir, "saved-history.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = path
            with patch("os.path.exists", return_value=True):
                with (
                    patch.object(history_actions.actions.app, "open") as open_mock,
                    patch.object(history_actions, "notify") as notify_mock,
                ):
                    result = HistoryActions.gpt_request_history_open_last_save_path()
            expected = os.path.realpath(path)
            open_mock.assert_called_once_with(expected)
            notify_mock.assert_called()
            self.assertEqual(result, expected)

        def test_open_last_save_path_handles_missing_file(self) -> None:
            GPTState.last_history_save_path = "/tmp/does-not-exist.md"
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_open_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertEqual(GPTState.last_history_save_path, "")

else:
    if not TYPE_CHECKING:
        class RequestHistoryOpenPathTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
