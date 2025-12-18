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
    import talon_user.lib.requestHistoryDrawer as history_drawer  # type: ignore
    from talon_user.lib.requestState import RequestPhase

    class RequestHistoryDrawerGatingTests(unittest.TestCase):
        def test_request_is_in_flight_delegates_to_request_state_helper(self) -> None:
            class State:
                def __init__(self, phase):
                    self.phase = phase

            with (
                patch.object(
                    history_drawer,
                    "current_state",
                    return_value=State(RequestPhase.STREAMING),
                ),
                patch.object(
                    history_drawer, "is_in_flight", return_value=True
                ) as inflight,
            ):
                self.assertTrue(history_drawer._request_is_in_flight())
                inflight.assert_called_once()

            with (
                patch.object(
                    history_drawer,
                    "current_state",
                    return_value=State(RequestPhase.DONE),
                ),
                patch.object(
                    history_drawer, "is_in_flight", return_value=False
                ) as inflight,
            ):
                self.assertFalse(history_drawer._request_is_in_flight())
                inflight.assert_called_once()

        def test_reject_if_request_in_flight_uses_try_start_request_drop_reason(
            self,
        ) -> None:
            with (
                patch.object(
                    history_drawer,
                    "try_start_request",
                    return_value=(False, "in_flight"),
                ),
                patch.object(history_drawer, "current_state"),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                self.assertTrue(history_drawer._reject_if_request_in_flight())
            set_reason.assert_called_once_with("in_flight")
            notify_mock.assert_called_once()

            with (
                patch.object(
                    history_drawer, "try_start_request", return_value=(True, "")
                ),
                patch.object(history_drawer, "current_state"),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                self.assertFalse(history_drawer._reject_if_request_in_flight())
            set_reason.assert_not_called()
            notify_mock.assert_not_called()

else:
    if not TYPE_CHECKING:

        class RequestHistoryDrawerGatingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
