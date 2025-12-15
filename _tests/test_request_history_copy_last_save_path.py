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

    class RequestHistoryCopyPathTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.last_history_save_path = ""

        def test_copy_last_save_path_notifies_when_missing(self) -> None:
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_copy_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertIn("model history save source", str(notify_mock.call_args[0][0]))

        def test_copy_last_save_path_copies_and_notifies(self) -> None:
            tmpdir = tempfile.mkdtemp()
            path = os.path.join(tmpdir, "saved-history.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = path
            with (
                patch.object(history_actions.actions, "clip", create=True) as clip_mock,
                patch.object(history_actions, "notify") as notify_mock,
            ):
                result = HistoryActions.gpt_request_history_copy_last_save_path()
            expected = os.path.realpath(path)
            clip_mock.set_text.assert_called_once_with(expected)  # type: ignore[attr-defined]
            notify_mock.assert_called()
            self.assertEqual(result, expected)

        def test_copy_last_save_path_falls_back_to_paste_on_clip_error(self) -> None:
            tmpdir = tempfile.mkdtemp()
            path = os.path.join(tmpdir, "saved-history.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = path
            with (
                patch.object(history_actions.actions, "clip", create=True) as clip_mock,
                patch.object(history_actions.actions.user, "paste", create=True) as paste_mock,
                patch.object(history_actions, "notify") as notify_mock,
            ):
                clip_mock.set_text.side_effect = Exception("clipboard unavailable")  # type: ignore[attr-defined]
                result = HistoryActions.gpt_request_history_copy_last_save_path()
            expected = os.path.realpath(path)
            paste_mock.assert_called_once_with(expected)  # type: ignore[attr-defined]
            notify_mock.assert_called()
            self.assertEqual(result, expected)

else:
    if not TYPE_CHECKING:
        class RequestHistoryCopyPathTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
