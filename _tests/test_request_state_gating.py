import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestState import (
        RequestState,
        RequestPhase,
        lifecycle_status_for,
        is_in_flight,
        try_start_request,
    )
    from talon_user.lib.requestLifecycle import (
        RequestLifecycleState,
        reduce_request_state,
        is_terminal,
    )

    class RequestStateGatingTests(unittest.TestCase):
        def test_is_in_flight_true_for_active_phases(self) -> None:
            active_phases = (
                RequestPhase.LISTENING,
                RequestPhase.TRANSCRIBING,
                RequestPhase.CONFIRMING,
                RequestPhase.SENDING,
                RequestPhase.STREAMING,
            )
            for phase in active_phases:
                with self.subTest(phase=phase):
                    state = RequestState(phase=phase)
                    self.assertTrue(
                        is_in_flight(state),
                        f"{phase} should be considered in-flight",
                    )

        def test_is_in_flight_false_for_terminal_phases(self) -> None:
            terminal_phases = (
                RequestPhase.IDLE,
                RequestPhase.DONE,
                RequestPhase.ERROR,
                RequestPhase.CANCELLED,
            )
            for phase in terminal_phases:
                with self.subTest(phase=phase):
                    state = RequestState(phase=phase)
                    self.assertFalse(
                        is_in_flight(state),
                        f"{phase} should not be considered in-flight",
                    )

        def test_try_start_request_reports_drop_reason_for_inflight(self) -> None:
            active_phases = (
                RequestPhase.LISTENING,
                RequestPhase.TRANSCRIBING,
                RequestPhase.CONFIRMING,
                RequestPhase.SENDING,
                RequestPhase.STREAMING,
            )
            for phase in active_phases:
                with self.subTest(phase=phase):
                    allowed, reason = try_start_request(RequestState(phase=phase))
                    self.assertFalse(allowed)
                    self.assertEqual(reason, "in_flight")

        def test_try_start_request_allows_start_from_terminal_phases(self) -> None:
            terminal_phases = (
                RequestPhase.IDLE,
                RequestPhase.DONE,
                RequestPhase.ERROR,
                RequestPhase.CANCELLED,
            )
            for phase in terminal_phases:
                with self.subTest(phase=phase):
                    allowed, reason = try_start_request(RequestState(phase=phase))
                    self.assertTrue(allowed)
                    self.assertEqual(reason, "")

        def test_lifecycle_status_for_maps_phases(self) -> None:
            phase_to_status = {
                RequestPhase.IDLE: "pending",
                RequestPhase.LISTENING: "pending",
                RequestPhase.TRANSCRIBING: "pending",
                RequestPhase.CONFIRMING: "pending",
                RequestPhase.SENDING: "running",
                RequestPhase.STREAMING: "streaming",
                RequestPhase.DONE: "completed",
                RequestPhase.ERROR: "errored",
                RequestPhase.CANCELLED: "cancelled",
            }
            for phase, expected in phase_to_status.items():
                with self.subTest(phase=phase):
                    state = RequestState(phase=phase)
                    lifecycle = lifecycle_status_for(state)
                    self.assertIsInstance(lifecycle, RequestLifecycleState)
                    self.assertEqual(
                        lifecycle.status,
                        expected,
                        f"{phase} should map to {expected}",
                    )

        def test_reduce_request_state_respects_terminal_semantics(self) -> None:
            """Characterise retry vs terminal behaviour for RequestLifecycle reducer."""

            pending = RequestLifecycleState(status="pending")
            running = reduce_request_state(pending, "start")
            self.assertEqual(running.status, "running")

            streaming = reduce_request_state(running, "stream_start")
            self.assertEqual(streaming.status, "streaming")

            completed = reduce_request_state(streaming, "stream_end")
            self.assertEqual(completed.status, "completed")

            # Terminal errored/cancelled should not move back to non-terminal,
            # except via an explicit "retry".
            errored = reduce_request_state(running, "error")
            self.assertEqual(errored.status, "errored")
            self.assertTrue(is_terminal(errored))

            still_errored = reduce_request_state(errored, "start")
            self.assertIs(still_errored, errored)

            retried = reduce_request_state(errored, "retry")
            self.assertEqual(retried.status, "running")

            cancelled = reduce_request_state(running, "cancel")
            self.assertEqual(cancelled.status, "cancelled")
            self.assertTrue(is_terminal(cancelled))

            still_cancelled = reduce_request_state(cancelled, "start")
            self.assertIs(still_cancelled, cancelled)

else:
    if not TYPE_CHECKING:

        class RequestStateGatingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
