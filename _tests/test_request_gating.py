import runpy
import runpy
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import requestGating
    from talon_user.lib import requestLog
    from talon_user.lib.requestState import RequestPhase, RequestState
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.streamingCoordinator import new_streaming_session

    _HISTORY_VALIDATE_PATH = (
        Path(__file__).resolve().parents[1]
        / "scripts"
        / "tools"
        / "history-axis-validate.py"
    )
    _history_axis_validate_globals = runpy.run_path(
        str(_HISTORY_VALIDATE_PATH), run_name="history_axis_validate_test"
    )
    history_axis_validate_main = _history_axis_validate_globals["main"]

    class RequestGatingTests(unittest.TestCase):
        def test_request_is_in_flight_with_explicit_state(self) -> None:
            streaming_state = RequestState(phase=RequestPhase.STREAMING)
            self.assertTrue(requestGating.request_is_in_flight(streaming_state))

            done_state = RequestState(phase=RequestPhase.DONE)
            self.assertFalse(requestGating.request_is_in_flight(done_state))

        def test_request_is_in_flight_handles_current_state_errors(self) -> None:
            with patch.object(requestGating, "current_state", side_effect=RuntimeError):
                self.assertFalse(requestGating.request_is_in_flight())

        def test_try_begin_request_with_state(self) -> None:
            streaming_state = RequestState(phase=RequestPhase.SENDING)
            allowed, reason = requestGating.try_begin_request(streaming_state)
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")

            idle_state = RequestState(phase=RequestPhase.IDLE)
            allowed, reason = requestGating.try_begin_request(idle_state)
            self.assertTrue(allowed)
            self.assertEqual(reason, "")

        def test_try_begin_request_records_gating_drop_stats(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()
            streaming_state = RequestState(phase=RequestPhase.SENDING)
            allowed, reason = requestGating.try_begin_request(streaming_state)
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")

            stats = requestLog.consume_gating_drop_stats()
            self.assertEqual(stats.get("in_flight"), 1)

            idle_state = RequestState(phase=RequestPhase.IDLE)
            requestGating.try_begin_request(idle_state)
            self.assertEqual(requestLog.gating_drop_stats().get("in_flight", 0), 0)

        def test_try_begin_request_records_streaming_event(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            session = new_streaming_session("rid-stream")
            GPTState.last_streaming_events = []
            streaming_state = RequestState(
                phase=RequestPhase.SENDING,
                request_id="rid-stream",
            )

            allowed, reason = requestGating.try_begin_request(
                streaming_state, source="test_case"
            )
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertTrue(events)
            first = events[-1]
            self.assertEqual(first.get("kind"), "gating_drop")
            self.assertEqual(first.get("reason"), "in_flight")
            self.assertEqual(first.get("phase"), RequestPhase.SENDING.value)
            self.assertEqual(first.get("source"), "test_case")
            self.assertEqual(first.get("reason_count"), 1)
            self.assertEqual(first.get("total_count"), 1)
            self.assertEqual(first.get("counts", {}).get("in_flight"), 1)
            self.assertEqual(first.get("sources", {}).get("test_case"), 1)
            self.assertEqual(first.get("source_count"), 1)
            self.assertEqual(session.events[-1], first)

            snapshot = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(snapshot.get("gating_drop_total"), 1)
            self.assertEqual(snapshot.get("gating_drop_counts", {}).get("in_flight"), 1)
            self.assertEqual(
                snapshot.get("gating_drop_sources", {}).get("test_case"), 1
            )
            self.assertEqual(
                snapshot.get("gating_drop_last"),
                {"reason": "in_flight", "reason_count": 1},
            )
            self.assertEqual(
                snapshot.get("gating_drop_last_source"),
                {"source": "test_case", "count": 1},
            )

            allowed_again, reason_again = requestGating.try_begin_request(
                streaming_state, source="test_case"
            )
            self.assertFalse(allowed_again)
            self.assertEqual(reason_again, "in_flight")

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertGreaterEqual(len(events), 2)
            final = events[-1]
            self.assertEqual(final.get("kind"), "gating_drop")
            self.assertEqual(final.get("reason"), "in_flight")
            self.assertEqual(final.get("phase"), RequestPhase.SENDING.value)
            self.assertEqual(final.get("source"), "test_case")
            self.assertEqual(final.get("reason_count"), 2)
            self.assertEqual(final.get("total_count"), 2)
            self.assertEqual(final.get("counts", {}).get("in_flight"), 2)
            self.assertEqual(final.get("sources", {}).get("test_case"), 2)
            self.assertEqual(final.get("source_count"), 2)
            self.assertEqual(session.events[-1], final)

            snapshot = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(snapshot.get("gating_drop_total"), 2)
            self.assertEqual(snapshot.get("gating_drop_counts", {}).get("in_flight"), 2)
            self.assertEqual(
                snapshot.get("gating_drop_last"),
                {"reason": "in_flight", "reason_count": 2},
            )

        def test_try_begin_request_handles_current_state_failure(self) -> None:
            with patch.object(requestGating, "current_state", side_effect=RuntimeError):
                allowed, reason = requestGating.try_begin_request()
            self.assertTrue(allowed)
            self.assertEqual(reason, "")

        def test_gating_snapshot_persists_across_session_updates(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            session = new_streaming_session("rid-session")
            GPTState.last_streaming_events = []
            streaming_state = RequestState(
                phase=RequestPhase.SENDING,
                request_id="rid-session",
            )

            allowed, reason = requestGating.try_begin_request(streaming_state)
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")

            snapshot = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(snapshot.get("gating_drop_total"), 1)

            # Simulate streaming progress; gating summary should remain intact.
            from talon_user.lib.streamingCoordinator import (
                record_streaming_chunk,
                record_streaming_snapshot,
            )

            record_streaming_chunk(session.run, "partial chunk")
            persisted = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(persisted.get("gating_drop_total"), 1)
            self.assertEqual(
                persisted.get("gating_drop_counts", {}).get("in_flight"),
                1,
            )

            # Introduce a second gating drop reason via snapshot metadata.
            record_streaming_snapshot(
                session.run,
                extra={
                    "request_id": "rid-session",
                    "gating_drop_counts": {"history_save_failed": 1},
                    "gating_drop_last": {
                        "reason": "history_save_failed",
                        "reason_count": 1,
                    },
                },
            )

            summary = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(summary.get("gating_drop_total"), 2)
            counts = summary.get("gating_drop_counts", {})
            self.assertEqual(counts.get("in_flight"), 1)
            self.assertEqual(counts.get("history_save_failed"), 1)
            self.assertEqual(
                summary.get("gating_drop_counts_sorted"),
                [
                    {"reason": "history_save_failed", "count": 1},
                    {"reason": "in_flight", "count": 1},
                ],
            )
            self.assertEqual(
                summary.get("gating_drop_last"),
                {"reason": "history_save_failed", "reason_count": 1},
            )

        def test_history_validation_stats_include_gating_counts(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            session = new_streaming_session("rid-stats")
            GPTState.last_streaming_events = []
            streaming_state = RequestState(
                phase=RequestPhase.SENDING,
                request_id="rid-stats",
            )
            requestGating.try_begin_request(streaming_state, source="test_case")

            stats = requestLog.history_validation_stats()
            self.assertEqual(stats.get("gating_drop_total"), 1)
            self.assertEqual(stats.get("gating_drop_counts", {}).get("in_flight"), 1)
            self.assertEqual(stats.get("gating_drop_sources", {}).get("test_case"), 1)
            summary = stats.get("streaming_gating_summary", {})
            self.assertIsInstance(summary, dict)
            self.assertEqual(summary.get("total"), 1)
            self.assertEqual(summary.get("counts", {}).get("in_flight"), 1)
            self.assertEqual(summary.get("sources", {}).get("test_case"), 1)
            self.assertEqual(
                summary.get("counts_sorted"),
                [{"reason": "in_flight", "count": 1}],
            )
            self.assertEqual(
                summary.get("sources_sorted"),
                [{"source": "test_case", "count": 1}],
            )
            self.assertEqual(
                summary.get("last"),
                {"reason": "in_flight", "reason_count": 1},
            )
            self.assertEqual(
                summary.get("last_source"),
                {"source": "test_case", "count": 1},
            )
            self.assertEqual(
                summary.get("last_message"),
                requestLog.drop_reason_message("in_flight"),  # type: ignore[arg-type]
            )
            self.assertEqual(summary.get("last_code"), "in_flight")

        def test_history_validation_stats_reports_last_drop_message(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()
            requestLog.set_drop_reason("")

            streaming_state = RequestState(phase=RequestPhase.SENDING)
            allowed, reason = requestGating.try_begin_request(
                streaming_state, source="message_case"
            )
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")
            expected_message = requestLog.drop_reason_message(reason)

            requestLog.set_drop_reason(reason, expected_message)

            stats = requestLog.history_validation_stats()
            self.assertEqual(
                stats.get("gating_drop_last_message"),
                expected_message,
            )

            requestLog.set_drop_reason("")
            stats_after_clear = requestLog.history_validation_stats()
            self.assertEqual(stats_after_clear.get("gating_drop_last_message"), "")

        def test_history_axis_validate_reset_gating_flag(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            streaming_state = RequestState(phase=RequestPhase.SENDING)
            requestGating.try_begin_request(streaming_state)

            with patch.object(
                sys,
                "argv",
                ["history-axis-validate", "--reset-gating", "--summary"],
            ):
                exit_code = history_axis_validate_main()
            self.assertEqual(exit_code, 0)
            self.assertEqual(requestLog.gating_drop_stats(), {})

        def test_history_axis_validate_requires_summary_for_reset(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            streaming_state = RequestState(phase=RequestPhase.SENDING)
            requestGating.try_begin_request(streaming_state)

            with patch.object(sys, "argv", ["history-axis-validate", "--reset-gating"]):
                exit_code = history_axis_validate_main()
            self.assertEqual(exit_code, 1)
            self.assertEqual(requestLog.gating_drop_stats().get("in_flight"), 1)

else:
    if not TYPE_CHECKING:

        class RequestGatingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

    else:
        unittest.main()
