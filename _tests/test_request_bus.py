import unittest
from typing import TYPE_CHECKING

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
        emit_complete,
        emit_fail,
        emit_reset,
        emit_cancel,
        next_request_id,
        set_controller,
    )
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import RequestPhase, Surface

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
else:
    if not TYPE_CHECKING:

        class RequestBusTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
