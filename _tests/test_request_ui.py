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
    from talon_user.lib.requestBus import (
        current_state,
        emit_begin_send,
        emit_history_saved,
        emit_append,
        emit_retry,
        emit_reset,
        emit_fail,
        emit_cancel,
        emit_begin_stream,
        emit_complete,
    )
    from talon_user.lib.requestState import RequestState, RequestPhase, Surface
    from talon_user.lib.modelState import GPTState
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

        def test_cancel_clears_fallbacks_and_closes_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_close",
                create=True,
            ) as close_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.GPTState.suppress_response_canvas = False
                requestUI.register_default_request_ui()
                requestUI._on_append("rid-cancel", "chunk")
                self.assertEqual(fallback_for("rid-cancel"), "chunk")
                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.CANCELLED, request_id="rid-cancel")
                )
                self.assertEqual(fallback_for("rid-cancel"), "")
                close_mock.assert_called()

        def test_error_clears_fallbacks_and_closes_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_close",
                create=True,
            ) as close_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.GPTState.suppress_response_canvas = False
                requestUI.register_default_request_ui()
                requestUI._on_append("rid-error", "chunk")
                self.assertEqual(fallback_for("rid-error"), "chunk")
                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.ERROR, request_id="rid-error")
                )
                self.assertEqual(fallback_for("rid-error"), "")
                close_mock.assert_called()

        def test_retry_notifies_and_opens_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ) as run_mock, patch.object(
                requestUI, "_notify"
            ) as notify_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-retry-ui")
                emit_retry("rid-retry-ui")
            notify_mock.assert_called()
            self.assertTrue(any("retry" in str(args[0]).lower() for args, _ in notify_mock.call_args_list))
            self.assertTrue(run_mock.called)
            open_mock.assert_called()

        def test_retry_respects_canvas_gate_when_suppressed(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI, "_notify"
            ) as notify_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock:
                requestUI.GPTState.current_destination_kind = "clipboard"
                requestUI.GPTState.suppress_response_canvas = True
                requestUI.register_default_request_ui()
                emit_begin_send("rid-retry-suppressed")
                emit_retry("rid-retry-suppressed")
            notify_mock.assert_called()
            open_mock.assert_not_called()

        def test_retry_clears_fallback_and_resets_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI, "_notify"
            ) as notify_mock, patch.object(
                requestUI, "_hide_pill"
            ) as hide_pill_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.GPTState.suppress_response_canvas = False
                requestUI.register_default_request_ui()
                # Seed fallback/throttle to ensure retry clears them.
                requestUI._LAST_APPEND_REFRESH_MS = 999.0
                requestUI._on_append("rid-retry-clear", "old chunk")
                self.assertTrue(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertEqual(fallback_for("rid-retry-clear"), "old chunk")

                emit_retry("rid-retry-clear")

                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertEqual(fallback_for("rid-retry-clear"), "")
            notify_mock.assert_called()
            hide_pill_mock.assert_called()

        def test_retry_flow_resets_state_and_refreshes_next_append(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.GPTState.suppress_response_canvas = False
                requestUI.register_default_request_ui()
                # Seed throttle and fallback, then simulate an error.
                requestUI._LAST_APPEND_REFRESH_MS = 111.0
                requestUI._on_append("rid-retry-flow", "stale")
                requestUI._on_state_change(
                    RequestState(
                        phase=RequestPhase.ERROR,
                        request_id="rid-retry-flow",
                        last_error="boom",
                    )
                )
                self.assertEqual(fallback_for("rid-retry-flow"), "")
                # Retry should clear throttle/fallback and open canvas.
                emit_retry("rid-retry-flow")
                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertEqual(fallback_for("rid-retry-flow"), "")
                open_mock.assert_called()
                # Next append should refresh canvas (no throttle).
                emit_append("fresh chunk")
            refresh_mock.assert_called()

        def test_new_request_id_resets_throttle_even_with_close_timestamps(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.time, "time", side_effect=[0.0, 0.05]
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-one")
                emit_append("first chunk")  # seeds throttle for rid-one at t=0
                emit_begin_send("rid-two")
                emit_append("second chunk")  # at t=50ms; new rid should bypass throttle
            self.assertEqual(refresh_mock.call_count, 2)

        def test_terminal_states_clear_response_canvas_suppression(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()

            requestUI._on_state_change(
                RequestState(phase=RequestPhase.ERROR, request_id="rid-suppression")
            )

            self.assertFalse(getattr(requestUI.GPTState, "suppress_response_canvas"))

        def test_cancel_clears_response_canvas_suppression(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()

            requestUI._on_state_change(
                RequestState(phase=RequestPhase.CANCELLED, request_id="rid-cancelled")
            )

            self.assertFalse(getattr(requestUI.GPTState, "suppress_response_canvas"))

        def test_cancel_via_bus_clears_suppression_and_allows_next_append(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_begin_send("rid-bus-cancel")
                emit_cancel("rid-bus-cancel")

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-bus-next")
                emit_append("chunk-after-cancel", request_id="rid-bus-next")
            refresh_mock.assert_called()

        def test_error_then_retry_keeps_response_canvas_visible(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_begin_send("rid-error")
                emit_fail("boom", request_id="rid-error")

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_retry("rid-error")
                emit_append("chunk-after-error", request_id="rid-error")
            open_mock.assert_called()
            refresh_mock.assert_called()

        def test_error_then_new_request_clears_suppression_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_begin_send("rid-error-new")
                emit_fail("boom", request_id="rid-error-new")

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-fresh")
                emit_append("chunk-fresh", request_id="rid-fresh")
            refresh_mock.assert_called()

        def test_begin_stream_clears_suppression_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_begin_stream("rid-stream")

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_append("chunk-stream", request_id="rid-stream")
            refresh_mock.assert_called()

        def test_listening_state_clears_suppression(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()

            requestUI._on_state_change(
                RequestState(phase=RequestPhase.LISTENING, request_id="rid-listen")
            )

            self.assertFalse(
                getattr(requestUI.GPTState, "suppress_response_canvas")
            )

        def test_confirming_state_clears_suppression(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()

            requestUI._on_state_change(
                RequestState(phase=RequestPhase.CONFIRMING, request_id="rid-confirm")
            )

            self.assertFalse(
                getattr(requestUI.GPTState, "suppress_response_canvas")
            )

        def test_transcribing_state_clears_suppression(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()

            requestUI._on_state_change(
                RequestState(phase=RequestPhase.TRANSCRIBING, request_id="rid-transcribe")
            )

            self.assertFalse(
                getattr(requestUI.GPTState, "suppress_response_canvas")
            )

        def test_listen_to_send_flow_clears_suppression_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                # Walk through listen -> confirm -> send.
                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.LISTENING, request_id="rid-flow")
                )
                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.CONFIRMING, request_id="rid-flow")
                )
                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.SENDING, request_id="rid-flow")
                )

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                requestUI._on_append("rid-flow", "streaming chunk")
            refresh_mock.assert_called()

        def test_bus_begin_send_clears_suppression_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_begin_send("rid-bus-send")

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_append("chunk-after-send", request_id="rid-bus-send")
            refresh_mock.assert_called()

        def test_bus_reset_clears_suppression_and_next_append_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                emit_reset()

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-after-reset")
                emit_append("chunk-after-reset", request_id="rid-after-reset")
            refresh_mock.assert_called()

        def test_done_state_clears_suppression_and_allows_refresh(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                requestUI._on_state_change(
                    RequestState(phase=RequestPhase.DONE, request_id="rid-done")
                )

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-after-done")
                emit_append("chunk-after-done", request_id="rid-after-done")
            refresh_mock.assert_called()

        def test_bus_complete_clears_suppression_and_allows_refresh(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                rid = emit_begin_send("rid-bus-complete")
                emit_complete(request_id=rid)

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-after-complete")
                emit_append("chunk-after-complete", request_id="rid-after-complete")
            refresh_mock.assert_called()

        def test_idle_state_clears_suppression_and_allows_refresh(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI.GPTState.suppress_response_canvas = True

                requestUI._on_state_change(RequestState(phase=RequestPhase.IDLE))

                self.assertFalse(
                    getattr(requestUI.GPTState, "suppress_response_canvas")
                )

                emit_begin_send("rid-after-idle")
                emit_append("chunk-after-idle", request_id="rid-after-idle")
            refresh_mock.assert_called()

        def test_register_default_clears_suppression_flag(self):
            requestUI.GPTState.suppress_response_canvas = True
            requestUI.register_default_request_ui()
            self.assertFalse(
                getattr(requestUI.GPTState, "suppress_response_canvas")
            )

        def test_register_default_resets_append_tracking(self):
            # Seed globals to ensure registration clears them.
            requestUI._LAST_APPEND_REFRESH_MS = 999.0
            requestUI._LAST_APPEND_REQUEST_ID = "stale-rid"
            requestUI.register_default_request_ui()
            self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
            self.assertIsNone(requestUI._LAST_APPEND_REQUEST_ID)

        def test_retry_without_prior_request_generates_id_and_opens_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ) as run_mock, patch.object(
                requestUI, "_notify"
            ) as notify_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                # No prior begin_send; retry should generate an id and open canvas.
                requestUI._LAST_APPEND_REFRESH_MS = 123.0
                emit_retry()
                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                notify_mock.assert_called()
                run_mock.assert_called()
                open_mock.assert_called()
                # Next append should refresh (not throttled, has an id).
                emit_append("first chunk")
            refresh_mock.assert_called()

        def test_bus_retry_without_prior_request_opens_canvas_and_clears_cache(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ) as run_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 555.0
                requestUI._LAST_APPEND_REQUEST_ID = "stale-id"
                emit_reset()
                emit_retry()
                state = current_state()
                self.assertEqual(state.phase, RequestPhase.STREAMING)
                self.assertEqual(state.active_surface, Surface.PILL)
                self.assertTrue(state.request_id)
                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertIsNone(requestUI._LAST_APPEND_REQUEST_ID)
                run_mock.assert_called()
                open_mock.assert_called()
                # Next append should refresh (not throttled).
                emit_append("first chunk after retry")
            refresh_mock.assert_called()

        def test_error_then_retry_resets_throttle_and_refreshes_append(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-error-retry")
                emit_append("chunk-before-error")  # seeds throttle
                emit_retry("rid-error-retry")
                emit_append("chunk-after-retry")
            # After retry, append should refresh (throttle reset).
            refresh_mock.assert_called()

        def test_error_then_retry_flow_refreshes_after_reset_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-error-retry-flow")
                emit_append("first chunk")  # seeds throttle
                emit_fail("boom")
                emit_retry()  # no id passed; should generate/pick current and reset throttle
                emit_append("second chunk")  # should refresh (not throttled) after retry
            # Expect two refreshes: initial append and post-retry append.
            self.assertGreaterEqual(refresh_mock.call_count, 2)

        def test_reset_closes_response_canvas(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_close",
                create=True,
            ) as close_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ):
                requestUI._on_state_change(RequestState(phase=RequestPhase.IDLE))
            close_mock.assert_called()

        def test_terminal_states_hide_pill(self):
            with patch.object(
                requestUI, "_hide_pill"
            ) as hide_mock, patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_close",
                create=True,
            ):
                requestUI._on_state_change(RequestState(phase=RequestPhase.DONE))
                requestUI._on_state_change(RequestState(phase=RequestPhase.CANCELLED))
            self.assertGreaterEqual(hide_mock.call_count, 2)

        def test_sending_resets_append_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.time, "time", return_value=0.0
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 123.0  # simulate prior throttle state
                requestUI.register_default_request_ui()
                requestUI._on_state_change(RequestState(phase=RequestPhase.SENDING, request_id="rid-throttle"))
                emit_append("chunk-after-reset")
            refresh_mock.assert_called_once()

        def test_idle_resets_append_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock, patch.object(
                requestUI.time, "time", return_value=0.0
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 456.0  # simulate prior throttle state
                requestUI.register_default_request_ui()
                requestUI._on_state_change(RequestState(phase=RequestPhase.IDLE, request_id="rid-idle-throttle"))
                emit_append("chunk-after-idle")
            refresh_mock.assert_called_once()

        def test_terminal_resets_append_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 789.0
                requestUI.register_default_request_ui()
                requestUI._on_state_change(RequestState(phase=RequestPhase.ERROR, request_id="rid-error-throttle"))
                emit_append("chunk-after-error")
            refresh_mock.assert_called_once()

        def test_cancel_resets_append_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 321.0
                requestUI.register_default_request_ui()
                requestUI._on_state_change(RequestState(phase=RequestPhase.CANCELLED, request_id="rid-cancel-throttle"))
                emit_append("chunk-after-cancel")
            refresh_mock.assert_called_once()

        def test_reset_resets_append_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI._LAST_APPEND_REFRESH_MS = 222.0
                requestUI.register_default_request_ui()
                requestUI._on_state_change(RequestState(phase=RequestPhase.IDLE, request_id="rid-reset-throttle"))
                emit_append("chunk-after-reset")
            refresh_mock.assert_called_once()

        def test_retry_without_request_id_clears_all_fallbacks(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                requestUI._on_append("rid-old", "old chunk")
                self.assertEqual(fallback_for("rid-old"), "old chunk")
                requestUI._LAST_APPEND_REFRESH_MS = 100.0
                requestUI._LAST_APPEND_REQUEST_ID = "rid-old"
                emit_retry()
                self.assertEqual(fallback_for("rid-old"), "")
                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertIsNone(requestUI._LAST_APPEND_REQUEST_ID)

        def test_cancel_then_retry_resets_throttle_and_refreshes_append(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-cancel-retry")
                emit_append("first chunk")  # seeds throttle
                requestUI._on_state_change(RequestState(phase=RequestPhase.CANCELLED, request_id="rid-cancel-retry"))
                emit_retry("rid-cancel-retry")
                emit_append("second chunk")
            # Expect two refreshes: before cancel and after retry.
            self.assertGreaterEqual(refresh_mock.call_count, 2)

        def test_bus_cancel_then_retry_clears_fallback_and_throttle(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-cancel-bus")
                emit_append("first chunk")
                self.assertEqual(fallback_for("rid-cancel-bus"), "first chunk")
                emit_cancel()
                # Seed throttle/cache to ensure retry clears them.
                requestUI._LAST_APPEND_REFRESH_MS = 100.0
                requestUI._LAST_APPEND_REQUEST_ID = "rid-cancel-bus"
                emit_retry()
                self.assertEqual(fallback_for("rid-cancel-bus"), "")
                self.assertIsNone(requestUI._LAST_APPEND_REFRESH_MS)
                self.assertIsNone(requestUI._LAST_APPEND_REQUEST_ID)
                emit_append("second chunk after retry")
            self.assertGreaterEqual(refresh_mock.call_count, 2)

        def test_error_then_retry_clears_fallback_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-error-flow")
                emit_append("before error")  # seeds fallback/throttle
                requestUI._on_state_change(
                    RequestState(
                        phase=RequestPhase.ERROR,
                        request_id="rid-error-flow",
                        last_error="boom",
                    )
                )
                self.assertEqual(fallback_for("rid-error-flow"), "")
                emit_retry("rid-error-flow")
                emit_append("after retry")
            self.assertGreaterEqual(refresh_mock.call_count, 2)

        def test_cancel_then_retry_sets_request_id_and_last_request_id(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ), patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ):
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send()
                emit_cancel()
                emit_retry()
                state = current_state()
                self.assertTrue(state.request_id)
                self.assertEqual(getattr(GPTState, "last_request_id", ""), state.request_id)

        def test_error_retry_integration_resets_cache_and_refreshes(self):
            with patch.object(
                requestUI, "run_on_ui_thread", side_effect=lambda fn: fn()
            ) as run_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_open",
                create=True,
            ) as open_mock, patch.object(
                requestUI.actions.user,
                "model_response_canvas_refresh",
                create=True,
            ) as refresh_mock:
                requestUI.GPTState.current_destination_kind = "window"
                requestUI.register_default_request_ui()
                emit_begin_send("rid-int")
                emit_append("before error")  # seeds fallback/throttle
                emit_fail("boom")
                self.assertEqual(fallback_for("rid-int"), "")
                emit_retry("rid-int")
                emit_append("after retry")
            # Expect refreshes for the initial append and post-retry append.
            self.assertGreaterEqual(refresh_mock.call_count, 2)
            self.assertTrue(run_mock.called)
            open_mock.assert_called()

        def test_response_canvas_hint_references_show_response_command(self) -> None:
            """Specifying validation: _show_response_canvas_hint must reference
            'model show response', not 'model last response' (ADR-0057 D4,
            ADR-0080 Workstream 1 Loop 2)."""
            notified: list[str] = []
            with patch.object(requestUI, "_notify", side_effect=notified.append):
                requestUI._show_response_canvas_hint()
            self.assertEqual(len(notified), 1, "expected exactly one notification")
            self.assertIn(
                "model show response",
                notified[0],
                "hint should reference the dedicated open command, not the toggle",
            )
            self.assertNotIn(
                "model last response",
                notified[0],
                "hint must not reference the toggle command",
            )

else:
    if not TYPE_CHECKING:

        class RequestUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
