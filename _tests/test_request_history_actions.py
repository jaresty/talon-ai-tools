import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestHistoryActions import UserActions as HistoryActions
    from talon_user.lib.requestLog import append_entry, clear_history
    from talon_user.lib.modelState import GPTState
    from talon import actions

    class RequestHistoryActionTests(unittest.TestCase):
        def setUp(self):
            clear_history()
            actions.user.calls.clear()
            actions.app.calls.clear()
            GPTState.last_response = ""
            GPTState.last_meta = ""
            GPTState.text_to_confirm = ""

            # Stub canvas open to record invocation.
            def _open_canvas():
                actions.user.calls.append(("model_response_canvas_open", tuple(), {}))

            actions.user.model_response_canvas_open = _open_canvas  # type: ignore[attr-defined]

        def test_show_latest_populates_state_and_opens_canvas(self):
            append_entry("rid-1", "prompt text", "answer text", "meta text")
            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(GPTState.last_response, "answer text")
            self.assertEqual(GPTState.last_meta, "meta text")
            self.assertEqual(GPTState.text_to_confirm, "answer text")
            self.assertIn(
                ("model_response_canvas_open", tuple(), {}),
                actions.user.calls,
            )

        def test_show_previous_uses_offset(self):
            append_entry("rid-1", "p1", "resp1", "meta1")
            append_entry("rid-2", "p2", "resp2", "meta2")

            HistoryActions.gpt_request_history_show_previous(1)
            self.assertEqual(GPTState.last_response, "resp1")
            self.assertEqual(GPTState.last_meta, "meta1")

        def test_empty_history_notifies(self):
            HistoryActions.gpt_request_history_show_latest()
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)

        def test_prev_next_navigation(self):
            append_entry("rid-1", "p1", "resp1", "meta1")
            append_entry("rid-2", "p2", "resp2", "meta2")
            append_entry("rid-3", "p3", "resp3", "meta3")

            HistoryActions.gpt_request_history_show_latest()
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp2")
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp1")
            # Attempting to go past oldest should not change.
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp1")
            # Step forward to newer entries.
            HistoryActions.gpt_request_history_next()
            self.assertEqual(GPTState.last_response, "resp2")
            HistoryActions.gpt_request_history_next()
            self.assertEqual(GPTState.last_response, "resp3")
            # Already at latest.
            HistoryActions.gpt_request_history_next()

        def test_history_list_notifies(self):
            append_entry("rid-1", "prompt one", "resp1", duration_ms=7)
            actions.user.calls.clear()
            actions.app.calls.clear()
            HistoryActions.gpt_request_history_list(2)
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)
else:
    if not TYPE_CHECKING:
        class RequestHistoryActionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
