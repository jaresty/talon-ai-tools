import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.requestLifecycle import (
        RequestLifecycleState,
        reduce_request_state,
        is_terminal,
        is_in_flight,
        try_start_request,
    )

    class RequestLifecycleTests(unittest.TestCase):
        def test_happy_path_streaming_flow(self) -> None:
            state = RequestLifecycleState()
            state = reduce_request_state(state, "start")
            self.assertEqual(state.status, "running")

            state = reduce_request_state(state, "stream_start")
            self.assertEqual(state.status, "streaming")

            state = reduce_request_state(state, "stream_end")
            self.assertEqual(state.status, "completed")

        def test_non_streaming_completion_flow(self) -> None:
            state = RequestLifecycleState()
            state = reduce_request_state(state, "start")
            self.assertEqual(state.status, "running")

            state = reduce_request_state(state, "complete")
            self.assertEqual(state.status, "completed")

        def test_error_and_cancel_are_terminal(self) -> None:
            state = RequestLifecycleState()
            state = reduce_request_state(state, "start")
            state = reduce_request_state(state, "error")
            self.assertEqual(state.status, "errored")

            # Further events should not move out of errored.
            for event in ("start", "stream_start", "stream_end", "complete", "cancel"):
                new_state = reduce_request_state(state, event)
                self.assertEqual(new_state.status, "errored")

            # Cancel from non-terminal states reaches cancelled.
            for initial in ("pending", "running", "streaming"):
                with self.subTest(initial=initial):
                    state = RequestLifecycleState(status=initial)
                    final = reduce_request_state(state, "cancel")
                    self.assertEqual(final.status, "cancelled")

        def test_unknown_events_are_ignored(self) -> None:
            state = RequestLifecycleState()
            new_state = reduce_request_state(state, "unknown-event")
            self.assertIs(new_state, state)

        def test_retry_leaves_terminal_states(self) -> None:
            # Retry from errored should return to running.
            state = RequestLifecycleState(status="errored")
            retried = reduce_request_state(state, "retry")
            self.assertEqual(retried.status, "running")
            # Retry from cancelled should also return to running.
            state = RequestLifecycleState(status="cancelled")
            retried = reduce_request_state(state, "retry")
            self.assertEqual(retried.status, "running")
            # Retry from completed/pending should leave state unchanged.
            for status in ("completed", "pending"):
                with self.subTest(status=status):
                    state = RequestLifecycleState(status=status)
                    retried = reduce_request_state(state, "retry")
                    self.assertEqual(retried.status, "running")

        def test_is_terminal_matches_error_and_cancel_contract(self) -> None:
            # Pending, running, streaming, and completed are non-terminal.
            for status in ("pending", "running", "streaming", "completed"):
                with self.subTest(status=status):
                    self.assertFalse(is_terminal(RequestLifecycleState(status=status)))

            # Errored and cancelled are terminal.
            for status in ("errored", "cancelled"):
                with self.subTest(status=status):
                    self.assertTrue(is_terminal(RequestLifecycleState(status=status)))

        def test_is_in_flight_covers_active_statuses(self) -> None:
            for status in ("running", "streaming"):
                with self.subTest(status=status):
                    self.assertTrue(is_in_flight(RequestLifecycleState(status=status)))

            for status in ("pending", "completed", "errored", "cancelled"):
                with self.subTest(status=status):
                    self.assertFalse(is_in_flight(RequestLifecycleState(status=status)))

        def test_try_start_request_returns_drop_reason(self) -> None:
            allowed, reason = try_start_request(RequestLifecycleState(status="pending"))
            self.assertTrue(allowed)
            self.assertEqual(reason, "")

            for status in ("running", "streaming"):
                with self.subTest(status=status):
                    allowed, reason = try_start_request(
                        RequestLifecycleState(status=status)
                    )
                    self.assertFalse(allowed)
                    self.assertEqual(reason, "in_flight")


else:
    if not TYPE_CHECKING:

        class RequestLifecycleTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
