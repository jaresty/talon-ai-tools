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
    from talon_user.lib import requestUI
    from talon_user.lib.requestBus import emit_begin_send, emit_history_saved, emit_append
    from talon_user.lib.requestState import RequestState, RequestPhase
    from talon_user.lib.responseCanvasFallback import fallback_for

    class RequestUITests(unittest.TestCase):
        def test_history_save_event_refreshes_history_drawer(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "request_history_drawer_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.register_default_request_ui()
                emit_history_saved("/tmp/file.md", request_id="rid-1")
            refresh_mock.assert_called()

        def test_history_save_event_provides_current_request_id(self):
            calls = []

            def record_req_id(req_id, path):
                calls.append((req_id, path))

            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "request_history_drawer_refresh",
                create=True,
            ):
                controller = requestUI.register_default_request_ui()
                controller._callbacks["on_history_save"] = record_req_id  # type: ignore[index]
                emit_begin_send("rid-current")
                emit_history_saved("/tmp/file.md")
            self.assertEqual(calls, [("rid-current", "/tmp/file.md")])

        def test_append_event_refreshes_response_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-append")
                emit_append("chunk")
            refresh_mock.assert_called()

        def test_append_refresh_is_throttled_and_ignores_empty(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.time, "time", side_effect=[0.0, 0.05, 0.21]
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-append-throttle")
                emit_append("")  # ignored
                emit_append("c1")  # at t=0
                emit_append("c2")  # at t=50ms, throttled
                emit_append("c3")  # at t=210ms, allowed
            self.assertEqual(refresh_mock.call_count, 2)

        def test_append_refresh_skips_when_canvas_suppressed(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "clipboard"
                requestUI.GPTState.suppress_response_canvas = True
                requestUI.register_default_request_ui()
                emit_begin_send("rid-append-suppressed")
                emit_append("chunk")
            refresh_mock.assert_not_called()
            self.assertEqual(fallback_for("rid-append-suppressed"), "")

        def test_append_caches_fallback_and_clears_on_terminal(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ), patch.object(
                requestUI.time, "time", side_effect=[0.0, 0.21, 0.42]
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-fallback")
                emit_append("hi ")
                emit_append("there")
            self.assertEqual(fallback_for("rid-fallback"), "hi there")
            # Clear on terminal transition.
            requestUI._on_state_change(
                RequestState(phase=RequestPhase.DONE, request_id="rid-fallback")
            )
            self.assertEqual(fallback_for("rid-fallback"), "")

        def test_reset_clears_all_fallbacks(self):
            # Seed a fallback value.
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ), patch.object(
                requestUI.time, "time", side_effect=[0.0, 0.21]
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.GPTState.suppress_response_canvas = False
                requestUI.register_default_request_ui()
                requestUI._on_append("rid-reset", "hi")
                requestUI._on_append("rid-reset", " there")
            self.assertEqual(fallback_for("rid-reset"), "hi there")
            # Reset/idle state clears all cached fallbacks.
            requestUI._on_state_change(RequestState(phase=RequestPhase.IDLE))
            self.assertEqual(fallback_for("rid-reset"), "")

        def test_sending_clears_all_fallbacks(self):
            # Seed two fallbacks, ensure send clears both.
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ), patch.object(
                requestUI.time, "time", side_effect=[0.0, 0.21, 0.42]
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI._on_append("rid-one", "hello")
                requestUI._on_append("rid-two", "world")
            self.assertEqual(fallback_for("rid-one"), "hello")
            self.assertEqual(fallback_for("rid-two"), "world")
            # Entering SENDING clears all fallbacks.
            requestUI._on_state_change(RequestState(phase=RequestPhase.SENDING))
            self.assertEqual(fallback_for("rid-one"), "")
            self.assertEqual(fallback_for("rid-two"), "")
else:
    if not TYPE_CHECKING:

        class RequestUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
