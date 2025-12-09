import unittest
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
    from talon import actions

    class ResponseCanvasRefreshTests(unittest.TestCase):
        def setUp(self):
            actions.user.calls.clear()
            actions.app.calls.clear()
            GPTState.current_destination_kind = "window"
            GPTState.suppress_response_canvas = False  # type: ignore[attr-defined]

        def tearDown(self):
            GPTState.current_destination_kind = ""
            if hasattr(GPTState, "suppress_response_canvas"):
                delattr(GPTState, "suppress_response_canvas")

        def test_refresh_uses_ui_dispatch(self):
            run_calls = []

            def run_on_ui_thread(fn, delay_ms=0):
                run_calls.append(delay_ms)
                fn()

            with (
                patch.object(modelHelpers, "run_on_ui_thread", side_effect=run_on_ui_thread),
                patch.object(modelHelpers.actions.user, "model_response_canvas_refresh") as refresh,
                patch.object(modelHelpers.actions.user, "model_response_canvas_open") as open_canvas,
            ):
                modelHelpers._refresh_response_canvas()

            # Two scheduled refreshes plus final refresh; open called once.
            self.assertGreaterEqual(refresh.call_count, 3)
            open_canvas.assert_called_once()
            self.assertIn(0, run_calls)
            self.assertIn(50, run_calls)

        def test_refresh_swallow_exceptions(self):
            # Ensure no exception is raised if refresh/open throw.
            with (
                patch.object(modelHelpers, "run_on_ui_thread") as run_mock,
                patch.object(modelHelpers.actions.user, "model_response_canvas_refresh", side_effect=Exception("boom")),
                patch.object(modelHelpers.actions.user, "model_response_canvas_open", side_effect=Exception("boom")),
            ):
                run_mock.side_effect = lambda fn, delay_ms=0: fn()
                modelHelpers._refresh_response_canvas()
else:
    class ResponseCanvasRefreshTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass
