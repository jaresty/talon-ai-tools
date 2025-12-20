import unittest
from typing import TYPE_CHECKING
from unittest import mock

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestBus import (
        current_state,
        current_lifecycle_state,
        emit_begin_send,
        emit_begin_stream,
        emit_retry,
        emit_append,
        emit_complete,
        emit_fail,
        emit_reset,
        emit_cancel,
        emit_history_saved,
        next_request_id,
        set_controller,
        is_in_flight as bus_is_in_flight,
        try_start_request as bus_try_start_request,
    )
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import RequestPhase, Surface
    from talon_user.lib.modelState import GPTState

    class RequestBusTests(unittest.TestCase):
        def setUp(self):
            # Fresh controller per test.
            set_controller(RequestUIController())
            emit_reset()

        def test_begin_complete_drives_state(self):
            rid = emit_begin_send()
            self.assertTrue(rid.startswith("req-"))
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.SENDING)
            self.assertEqual(state.active_surface, Surface.PILL)

            emit_complete(request_id=rid)
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.DONE)
            self.assertEqual(state.active_surface, Surface.RESPONSE_CANVAS)

        def test_fail_sets_error(self):
            rid = emit_begin_send("custom-id")
            emit_fail("boom", request_id=rid)
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.ERROR)
            self.assertEqual(state.active_surface, Surface.RESPONSE_CANVAS)

        def test_next_request_id_monotonic(self):
            first = next_request_id()
            second = next_request_id()
            self.assertNotEqual(first, second)

        def test_current_lifecycle_state_tracks_bus_phase(self):
            # Initial state: idle/pending.
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "pending")

            # BEGIN_SEND moves to running.
            rid = emit_begin_send()
            self.assertTrue(rid.startswith("req-"))
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "running")

            # BEGIN_STREAM maps to streaming.
            emit_begin_stream(request_id=rid)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "streaming")

            # COMPLETE maps to completed.
            emit_complete(request_id=rid)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "completed")

            # FAIL from a fresh send maps to errored.
            emit_reset()
            rid2 = emit_begin_send()
            emit_fail("boom", request_id=rid2)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "errored")

            # CANCEL maps to cancelled.
            emit_reset()
            rid3 = emit_begin_send()
            emit_cancel(request_id=rid3)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "cancelled")

        def test_emit_history_saved_calls_controller_hook(self):
            calls = []

            def on_history_save(req_id, path):
                calls.append((req_id, path))

            set_controller(RequestUIController(on_history_save=on_history_save))
            emit_reset()
            rid = emit_begin_send()
            emit_history_saved("/tmp/file.md", request_id=rid)
            self.assertEqual(calls, [(rid, "/tmp/file.md")])
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_append_calls_controller_hook(self):
            calls = []

            def on_append(req_id, chunk):
                calls.append((req_id, chunk))

            set_controller(RequestUIController(on_append=on_append))
            emit_reset()
            rid = emit_begin_send()
            emit_append("chunk-1", request_id=rid)
            self.assertEqual(calls, [(rid, "chunk-1")])

        def test_emit_history_saved_defaults_request_id(self):
            calls = []

            def on_history_save(req_id, path):
                calls.append((req_id, path))

            set_controller(RequestUIController(on_history_save=on_history_save))
            emit_reset()
            rid = emit_begin_send()
            emit_history_saved("/tmp/file.md")
            self.assertEqual(calls, [(rid, "/tmp/file.md")])
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_history_saved_generates_request_id_when_missing(self):
            calls = []

            def on_history_save(req_id, path):
                calls.append((req_id, path))

            set_controller(RequestUIController(on_history_save=on_history_save))
            emit_reset()
            emit_history_saved("/tmp/file.md")
            # A generated req id should be set and returned to the hook/last_request_id.
            self.assertEqual(len(calls), 1)
            generated_rid, path = calls[0]
            self.assertTrue(generated_rid.startswith("req-"))
            self.assertEqual(path, "/tmp/file.md")
            self.assertEqual(getattr(GPTState, "last_request_id", None), generated_rid)

        def test_emit_append_defaults_request_id(self):
            calls = []

            def on_append(req_id, chunk):
                calls.append((req_id, chunk))

            set_controller(RequestUIController(on_append=on_append))
            emit_reset()
            rid = emit_begin_send()
            emit_append("chunk-2")
            self.assertEqual(calls, [(rid, "chunk-2")])
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_append_without_id_generates_request_id_and_updates_last_request_id(
            self,
        ):
            calls = []

            def on_append(req_id, chunk):
                calls.append((req_id, chunk))

            set_controller(RequestUIController(on_append=on_append))
            emit_reset()
            emit_append("chunk-missing-id")
            self.assertEqual(len(calls), 1)
            req_id, chunk = calls[0]
            self.assertTrue(req_id.startswith("req-"))
            self.assertEqual(chunk, "chunk-missing-id")
            self.assertEqual(getattr(GPTState, "last_request_id", None), req_id)

        def test_emit_append_with_explicit_id_sets_last_request_id(self):
            calls = []

            def on_append(req_id, chunk):
                calls.append((req_id, chunk))

            set_controller(RequestUIController(on_append=on_append))
            emit_reset()
            emit_append("chunk-explicit", request_id="rid-explicit-append")
            self.assertEqual(calls, [("rid-explicit-append", "chunk-explicit")])
            self.assertEqual(
                getattr(GPTState, "last_request_id", None), "rid-explicit-append"
            )

        def test_emit_begin_stream_sets_last_request_id(self):
            emit_reset()
            rid = emit_begin_stream()
            self.assertTrue(rid.startswith("req-"))
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_begin_stream_with_explicit_id_sets_last_request_id(self):
            emit_reset()
            rid = "explicit-stream-id"
            emit_begin_stream(request_id=rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_begin_stream_without_controller_sets_last_request_id(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_stream()
            self.assertTrue(rid.startswith("req-"))
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            set_controller(RequestUIController())

        def test_emit_reset_clears_last_request_id(self):
            emit_reset()
            rid = emit_begin_send()
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

            emit_reset()

            self.assertEqual(getattr(GPTState, "last_request_id", None), "")

        def test_emit_complete_sets_last_request_id_with_explicit_id(self):
            emit_reset()
            rid = "rid-complete"
            emit_complete(request_id=rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            self.assertEqual(current_state().phase, RequestPhase.DONE)

        def test_emit_retry_sets_last_request_id_and_calls_hook(self):
            calls = []

            def on_retry(req_id):
                calls.append(req_id)

            set_controller(RequestUIController(on_retry=on_retry))
            emit_reset()
            rid = emit_begin_send()
            emit_retry()
            self.assertEqual(calls, [rid])
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.STREAMING)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_retry_without_request_id_generates_one(self):
            calls = []

            def on_retry(req_id):
                calls.append(req_id)

            set_controller(RequestUIController(on_retry=on_retry))
            emit_reset()
            state = emit_retry()
            self.assertTrue(state.request_id)
            self.assertEqual(calls, [state.request_id])
            self.assertEqual(state.phase, RequestPhase.STREAMING)
            self.assertEqual(
                getattr(GPTState, "last_request_id", None), state.request_id
            )

        def test_emit_retry_from_error_clears_error_and_moves_to_streaming(self):
            emit_reset()
            rid = emit_begin_send("rid-bus-retry")
            emit_fail("boom")
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.ERROR)
            self.assertEqual(state.last_error, "boom")

            emit_retry()

            state = current_state()
            self.assertEqual(state.phase, RequestPhase.STREAMING)
            self.assertEqual(state.active_surface, Surface.PILL)
            self.assertEqual(state.request_id, rid)
            self.assertEqual(state.last_error, "")

        def test_emit_begin_send_with_explicit_id_sets_last_request_id(self):
            emit_reset()
            rid = "explicit-id"
            emit_begin_send(rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_cancel_preserves_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-cancel")
            emit_cancel(request_id=rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_fail_sets_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-fail")
            emit_fail("boom", request_id=rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            self.assertEqual(current_state().phase, RequestPhase.ERROR)

        def test_emit_fail_without_id_preserves_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-fail-none")
            emit_fail("boom")
            # Should keep the last request id instead of clearing it.
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_cancel_without_id_preserves_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-cancel-none")
            emit_cancel()
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_complete_without_id_preserves_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-complete-none")
            emit_complete()
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_emit_history_saved_without_controller_generates_request_id(self):
            # Drop the controller to simulate history_saved without active request context.
            set_controller(None)
            emit_reset()
            emit_history_saved("/tmp/file.md")
            # A generated request id should still be recorded.
            self.assertTrue(
                getattr(GPTState, "last_request_id", None).startswith("req-")
            )
            # Restore a controller for cleanliness.
            set_controller(RequestUIController())

        def test_emit_history_saved_with_explicit_id_without_controller_sets_last_request_id(
            self,
        ):
            set_controller(None)
            emit_reset()
            emit_history_saved("/tmp/explicit.md", request_id="rid-explicit-history")
            self.assertEqual(
                getattr(GPTState, "last_request_id", None), "rid-explicit-history"
            )
            set_controller(RequestUIController())

        def test_emit_reset_clears_last_request_id_without_controller(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_send("rid-no-controller")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

            emit_reset()

            self.assertEqual(getattr(GPTState, "last_request_id", None), "")
            set_controller(RequestUIController())

        def test_emit_begin_send_without_controller_sets_last_request_id(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_send()
            self.assertTrue(rid.startswith("req-"))
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            set_controller(RequestUIController())

        def test_emit_complete_without_id_generates_request_id_without_controller(self):
            set_controller(None)
            emit_reset()
            emit_complete()
            self.assertTrue(
                getattr(GPTState, "last_request_id", None).startswith("req-")
            )
            set_controller(RequestUIController())

        def test_emit_fail_without_id_generates_request_id_without_controller(self):
            set_controller(None)
            emit_reset()
            emit_fail("boom")
            self.assertTrue(
                getattr(GPTState, "last_request_id", None).startswith("req-")
            )
            set_controller(RequestUIController())

        def test_emit_cancel_without_id_generates_request_id_without_controller(self):
            set_controller(None)
            emit_reset()
            emit_cancel()
            self.assertTrue(
                getattr(GPTState, "last_request_id", None).startswith("req-")
            )
            set_controller(RequestUIController())

        def test_handle_without_controller_returns_state_with_request_id(self):
            set_controller(None)
            emit_reset()
            rid = emit_history_saved("/tmp/no-controller-state")
            self.assertTrue(rid.request_id.startswith("req-"))
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid.request_id)
            self.assertEqual(current_state().request_id, rid.request_id)
            self.assertEqual(current_state().phase, RequestPhase.IDLE)
            set_controller(RequestUIController())

        def test_emit_append_without_controller_generates_request_id_and_returns_state(
            self,
        ):
            set_controller(None)
            emit_reset()
            state = emit_append("chunk-no-controller")
            self.assertTrue(state.request_id.startswith("req-"))
            self.assertEqual(
                getattr(GPTState, "last_request_id", None), state.request_id
            )
            self.assertEqual(current_state().request_id, state.request_id)
            self.assertEqual(current_state().phase, RequestPhase.IDLE)
            set_controller(RequestUIController())

        def test_begin_send_advances_state_without_controller(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_send("rid-no-controller")
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.SENDING)
            self.assertEqual(state.request_id, rid)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            set_controller(RequestUIController())

        def test_set_controller_none_resets_retained_state(self):
            emit_reset()
            rid = emit_begin_send("rid-with-controller")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            # Drop the controller; retained state should reset to idle/empty.
            set_controller(None)
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.IDLE)
            self.assertIsNone(state.request_id)
            # Reattach a controller for subsequent tests.
            set_controller(RequestUIController())

        def test_complete_fail_cancel_transition_without_controller(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_send("rid-controllerless")

            state = emit_complete().phase
            self.assertEqual(state, RequestPhase.DONE)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

            emit_reset()
            rid = emit_begin_send("rid-controllerless-fail")
            fail_state = emit_fail("boom").phase
            self.assertEqual(fail_state, RequestPhase.ERROR)
            self.assertEqual(current_state().last_error, "boom")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

            emit_reset()
            rid = emit_begin_send("rid-controllerless-cancel")
            cancel_state = emit_cancel().phase
            self.assertEqual(cancel_state, RequestPhase.CANCELLED)
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            set_controller(RequestUIController())

        def test_lifecycle_state_advances_without_controller(self):
            set_controller(None)
            emit_reset()
            rid = emit_begin_send("rid-lifecycle")
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "running")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

            emit_begin_stream(request_id=rid)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "streaming")

            emit_complete(request_id=rid)
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "completed")

            emit_reset()
            emit_begin_send("rid-lifecycle-fail")
            emit_fail("boom")
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "errored")

            emit_reset()
            emit_begin_send("rid-lifecycle-cancel")
            emit_cancel()
            lifecycle = current_lifecycle_state()
            self.assertEqual(lifecycle.status, "cancelled")
            set_controller(RequestUIController())

        def test_emit_retry_after_cancel_clears_cancel_flag_and_resets_surface(self):
            emit_reset()
            rid = emit_begin_send("rid-cancel-retry")
            emit_cancel()
            state = current_state()
            self.assertEqual(state.phase, RequestPhase.CANCELLED)
            self.assertTrue(state.cancel_requested)

            emit_retry()

            state = current_state()
            self.assertEqual(state.phase, RequestPhase.STREAMING)
            self.assertEqual(state.active_surface, Surface.PILL)
            self.assertEqual(state.request_id, rid)
            self.assertFalse(state.cancel_requested)

        def test_begin_send_sets_last_request_id(self):
            emit_reset()
            rid = emit_begin_send("rid-bus")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_begin_stream_sets_last_request_id(self):
            emit_reset()
            rid = emit_begin_stream("rid-stream")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_reset_clears_last_request_id(self):
            emit_reset()
            emit_begin_send("rid-reset")
            self.assertEqual(getattr(GPTState, "last_request_id", None), "rid-reset")
            emit_reset()
            self.assertEqual(getattr(GPTState, "last_request_id", None), "")

        def test_complete_fail_cancel_default_request_id_and_track_last(self):
            emit_reset()
            rid = emit_begin_send("rid-full")
            # Complete without passing id defaults to current state and updates last_request_id.
            emit_complete()
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            # Fail defaults to current state and updates last_request_id.
            emit_fail("boom")
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)
            # Cancel defaults similarly.
            emit_cancel()
            self.assertEqual(getattr(GPTState, "last_request_id", None), rid)

        def test_try_start_request_delegates_to_controller(self):
            controller = RequestUIController()
            set_controller(controller)
            emit_reset()
            with mock.patch.object(
                controller, "try_start_request", return_value=(False, "in_flight")
            ) as patched:
                allowed, reason = bus_try_start_request()
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")
            patched.assert_called_once_with()

        def test_try_start_request_without_controller_defaults_to_state(self):
            set_controller(None)
            emit_reset()
            allowed, reason = bus_try_start_request()
            self.assertTrue(allowed)
            self.assertEqual(reason, "")
            set_controller(RequestUIController())

        def test_is_in_flight_delegates_to_controller(self):
            controller = RequestUIController()
            set_controller(controller)
            emit_reset()
            with mock.patch.object(
                controller, "is_in_flight", return_value=True
            ) as patched:
                result = bus_is_in_flight()
            self.assertTrue(result)
            patched.assert_called_once_with()

        def test_is_in_flight_without_controller_defaults_to_state(self):
            set_controller(None)
            emit_reset()
            result = bus_is_in_flight()
            self.assertFalse(result)
            set_controller(RequestUIController())

else:
    if not TYPE_CHECKING:

        class RequestBusTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
