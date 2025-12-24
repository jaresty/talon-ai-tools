import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelHelpers
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelResponseCanvas import ResponseCanvasState
    from talon import actions

    class ResponseCanvasRefreshTests(unittest.TestCase):
        def setUp(self):
            actions.user.calls.clear()
            actions.app.calls.clear()
            GPTState.current_destination_kind = "window"
            GPTState.suppress_response_canvas = False  # type: ignore[attr-defined]
            if hasattr(GPTState, "response_canvas_manual_close"):
                delattr(GPTState, "response_canvas_manual_close")

        def tearDown(self):
            GPTState.current_destination_kind = ""
            if hasattr(GPTState, "suppress_response_canvas"):
                delattr(GPTState, "suppress_response_canvas")
            if hasattr(GPTState, "response_canvas_manual_close"):
                delattr(GPTState, "response_canvas_manual_close")

        def test_refresh_uses_ui_dispatch(self):
            run_calls = []

            def run_on_ui_thread(fn, delay_ms=0):
                run_calls.append(delay_ms)
                fn()

            with (
                patch.object(
                    modelHelpers, "run_on_ui_thread", side_effect=run_on_ui_thread
                ),
                patch.object(
                    modelHelpers.actions.user, "model_response_canvas_refresh"
                ) as refresh,
                patch.object(
                    modelHelpers.actions.user, "model_response_canvas_open"
                ) as open_canvas,
            ):
                modelHelpers._refresh_response_canvas()

            # One UI dispatch; open then refresh called once each.
            self.assertEqual(refresh.call_count, 1)
            open_canvas.assert_called_once()
            self.assertEqual(run_calls, [0])

        def test_refresh_swallow_exceptions(self):
            # Ensure no exception is raised if refresh/open throw.
            with (
                patch.object(modelHelpers, "run_on_ui_thread") as run_mock,
                patch.object(
                    modelHelpers.actions.user,
                    "model_response_canvas_refresh",
                    side_effect=Exception("boom"),
                ),
                patch.object(
                    modelHelpers.actions.user,
                    "model_response_canvas_open",
                    side_effect=Exception("boom"),
                ),
            ):
                run_mock.side_effect = lambda fn, delay_ms=0: fn()
                modelHelpers._refresh_response_canvas()

        def test_refresh_skips_after_manual_close(self):
            ResponseCanvasState.showing = False
            GPTState.response_canvas_manual_close = True

            def run_on_ui_thread(fn, delay_ms=0):
                fn()

            with (
                patch.object(
                    modelHelpers, "run_on_ui_thread", side_effect=run_on_ui_thread
                ),
                patch.object(
                    modelHelpers.actions.user, "model_response_canvas_open"
                ) as open_canvas,
                patch.object(
                    modelHelpers.actions.user, "model_response_canvas_refresh"
                ) as refresh,
            ):
                modelHelpers._refresh_response_canvas()

            open_canvas.assert_not_called()
            refresh.assert_not_called()

        def test_should_refresh_canvas_now_respects_manual_close(self):
            setattr(GPTState, "response_canvas_manual_close", True)
            self.assertFalse(modelHelpers._should_refresh_canvas_now())

        def test_should_refresh_canvas_now_follows_destination_kind(self):
            GPTState.current_destination_kind = "suggest"
            self.assertFalse(modelHelpers._should_refresh_canvas_now())
            GPTState.current_destination_kind = "window"
            self.assertTrue(modelHelpers._should_refresh_canvas_now())

        def test_append_history_entry_skips_when_flagged(self):
            session = SimpleNamespace(record_log_entry=MagicMock())
            GPTState.request = {}
            with patch("talon_user.lib.modelHelpers.append_entry_from_request") as append_entry:
                result = modelHelpers._append_history_entry(
                    session=session,
                    request_id="req-skip",
                    answer_text="done",
                    meta_text="",
                    last_recipe="",
                    started_at_ms=1,
                    duration_ms=2,
                    axes={},
                    provider=None,
                    skip_history=True,
                )
            append_entry.assert_not_called()
            self.assertEqual(result, "")

else:

    class ResponseCanvasRefreshTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
