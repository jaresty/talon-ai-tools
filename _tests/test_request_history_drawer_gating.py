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

    class RequestHistoryDrawerGatingTests(unittest.TestCase):
        def test_request_is_in_flight_delegates_to_gating_helper(self) -> None:
            with patch.object(
                history_drawer, "request_is_in_flight", return_value=True
            ) as helper:
                self.assertTrue(history_drawer._request_is_in_flight())
            helper.assert_called_once_with()

            with patch.object(
                history_drawer, "request_is_in_flight", return_value=False
            ) as helper:
                self.assertFalse(history_drawer._request_is_in_flight())
            helper.assert_called_once_with()

            with patch.object(
                history_drawer,
                "request_is_in_flight",
                side_effect=RuntimeError("boom"),
            ) as helper:
                self.assertFalse(history_drawer._request_is_in_flight())
            helper.assert_called_once_with()

        def test_reject_if_request_in_flight_notifies_with_drop_message(
            self,
        ) -> None:
            with (
                patch.object(
                    history_drawer,
                    "try_begin_request",
                    return_value=(False, "in_flight"),
                ) as try_begin,
                patch.object(
                    history_drawer,
                    "render_drop_reason",
                    return_value="Request running",
                    create=True,
                ) as render_message,
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                self.assertTrue(history_drawer._reject_if_request_in_flight())
            try_begin.assert_called_once_with(source="requestHistoryDrawer")
            render_message.assert_called_once_with("in_flight")
            set_reason.assert_called_once_with("in_flight", "Request running")
            notify_mock.assert_called_once_with("Request running")

            with (
                patch.object(
                    history_drawer,
                    "try_begin_request",
                    return_value=(False, "unknown_reason"),
                ),
                patch(
                    "talon_user.lib.dropReasonUtils.drop_reason_message",
                    return_value="",
                ),
                patch.object(
                    history_drawer,
                    "render_drop_reason",
                    return_value="Rendered fallback",
                    create=True,
                ) as render_message,
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                self.assertTrue(history_drawer._reject_if_request_in_flight())
            render_message.assert_called_once_with("unknown_reason")
            set_reason.assert_called_once_with("unknown_reason", "Rendered fallback")
            notify_mock.assert_called_once_with("Rendered fallback")

            with (
                patch.object(
                    history_drawer, "try_begin_request", return_value=(True, "")
                ) as try_begin,
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                self.assertFalse(history_drawer._reject_if_request_in_flight())
            try_begin.assert_called_once_with(source="requestHistoryDrawer")
            set_reason.assert_called_once_with("")
            notify_mock.assert_not_called()

        def test_reject_if_request_in_flight_preserves_pending_reason(self) -> None:
            with (
                patch.object(
                    history_drawer, "try_begin_request", return_value=(True, "")
                ),
                patch.object(
                    history_drawer, "last_drop_reason", return_value="pending"
                ),
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
