import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestState import (
        RequestEvent,
        RequestEventKind,
        RequestPhase,
        RequestState,
        Surface,
        transition,
    )

    class RequestStateTests(unittest.TestCase):
        def test_reset_restores_default(self):
            state = RequestState(
                phase=RequestPhase.DONE,
                active_surface=Surface.RESPONSE_CANVAS,
                request_id="abc",
                cancel_requested=True,
                last_error="boom",
            )

            next_state = transition(state, RequestEvent(RequestEventKind.RESET))

            self.assertEqual(next_state.phase, RequestPhase.IDLE)
            self.assertEqual(next_state.active_surface, Surface.NONE)
            self.assertIsNone(next_state.request_id)
            self.assertFalse(next_state.cancel_requested)
            self.assertEqual(next_state.last_error, "")

        def test_confirmation_flow_sets_surfaces(self):
            state = transition(RequestState(), RequestEvent(RequestEventKind.START_LISTEN))
            self.assertEqual(state.phase, RequestPhase.LISTENING)

            state = transition(state, RequestEvent(RequestEventKind.GOT_TRANSCRIPT))
            self.assertEqual(state.phase, RequestPhase.CONFIRMING)
            self.assertEqual(state.active_surface, Surface.CONFIRMATION_CHIP)

            state = transition(
                state, RequestEvent(RequestEventKind.CONFIRM_SEND, request_id="r1")
            )
            self.assertEqual(state.phase, RequestPhase.SENDING)
            self.assertEqual(state.active_surface, Surface.PILL)
            self.assertEqual(state.request_id, "r1")
            self.assertFalse(state.cancel_requested)

        def test_stream_and_cancel_preserve_request_id(self):
            state = transition(
                RequestState(), RequestEvent(RequestEventKind.BEGIN_SEND, request_id="rid")
            )
            state = transition(state, RequestEvent(RequestEventKind.BEGIN_STREAM))
            self.assertEqual(state.phase, RequestPhase.STREAMING)
            self.assertEqual(state.active_surface, Surface.PILL)
            self.assertEqual(state.request_id, "rid")

            cancelled = transition(state, RequestEvent(RequestEventKind.CANCEL))
            self.assertEqual(cancelled.phase, RequestPhase.CANCELLED)
            self.assertTrue(cancelled.cancel_requested)
            self.assertEqual(cancelled.request_id, "rid")
            self.assertEqual(cancelled.active_surface, Surface.NONE)

        def test_complete_and_fail_mark_response_canvas(self):
            state = transition(
                RequestState(), RequestEvent(RequestEventKind.BEGIN_SEND, request_id="rid")
            )
            done = transition(state, RequestEvent(RequestEventKind.COMPLETE))
            self.assertEqual(done.phase, RequestPhase.DONE)
            self.assertEqual(done.active_surface, Surface.RESPONSE_CANVAS)
            self.assertTrue(done.is_terminal)

            failed = transition(state, RequestEvent(RequestEventKind.FAIL, error="timeout"))
            self.assertEqual(failed.phase, RequestPhase.ERROR)
            self.assertEqual(failed.active_surface, Surface.RESPONSE_CANVAS)
            self.assertEqual(failed.last_error, "timeout")
            self.assertTrue(failed.is_terminal)
else:
    if not TYPE_CHECKING:
        class RequestStateTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
