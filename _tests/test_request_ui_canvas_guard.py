import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import talon_user.lib.requestUI as requestUI  # type: ignore
    from talon_user.lib.historyLifecycle import RequestPhase, RequestState  # type: ignore

    class RequestUICanvasGuardTests(unittest.TestCase):
        def test_state_change_skips_canvas_close_when_suppressed(self) -> None:
            with (
                patch.object(
                    requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
                ),
                patch.object(
                    requestUI.actions.user,
                    "model_response_canvas_close",
                    create=True,
                ) as close_mock,
            ):
                requestUI.GPTState.suppress_response_canvas_close = True
                requestUI.register_default_request_ui()
                requestUI._on_state_change(
                    RequestState(
                        phase=RequestPhase.CANCELLED,
                        request_id="rid-suppressed-close",
                    )
                )
            close_mock.assert_not_called()
            requestUI.GPTState.suppress_response_canvas_close = False

else:

    class RequestUICanvasGuardTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            pass
