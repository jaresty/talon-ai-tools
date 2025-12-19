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

        def test_try_begin_request_handles_current_state_failure(self) -> None:
            with patch.object(requestGating, "current_state", side_effect=RuntimeError):
                allowed, reason = requestGating.try_begin_request()
            self.assertTrue(allowed)
            self.assertEqual(reason, "")

        def test_history_validation_stats_include_gating_counts(self) -> None:
            requestLog.clear_history()
            requestLog.consume_gating_drop_stats()

            streaming_state = RequestState(phase=RequestPhase.SENDING)
            requestGating.try_begin_request(streaming_state)

            stats = requestLog.history_validation_stats()
            self.assertEqual(stats.get("gating_drop_total"), 1)
            self.assertEqual(stats.get("gating_drop_counts", {}).get("in_flight"), 1)

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
