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
    from talon_user.lib.requestHistoryDrawer import HistoryDrawerState

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
            HistoryDrawerState.last_message = ""

            def _block_guard(**kwargs):
                on_block = kwargs.get("on_block")
                if on_block is not None:
                    on_block("in_flight", "Request running")
                return True

            with patch.object(
                history_drawer,
                "guard_surface_request",
                side_effect=_block_guard,
            ) as guard:
                self.assertTrue(history_drawer._reject_if_request_in_flight())
            guard.assert_called_once()
            kwargs = guard.call_args.kwargs
            self.assertEqual(kwargs.get("surface"), "history_drawer")
            self.assertEqual(kwargs.get("source"), "requestHistoryDrawer")
            self.assertEqual(HistoryDrawerState.last_message, "Request running")

            HistoryDrawerState.last_message = ""

            def _fallback_guard(**kwargs):
                on_block = kwargs.get("on_block")
                if on_block is not None:
                    on_block("unknown_reason", "Rendered fallback")
                return True

            with patch.object(
                history_drawer,
                "guard_surface_request",
                side_effect=_fallback_guard,
            ) as guard:
                self.assertTrue(history_drawer._reject_if_request_in_flight())
            kwargs = guard.call_args.kwargs
            self.assertEqual(kwargs.get("surface"), "history_drawer")
            self.assertEqual(kwargs.get("source"), "requestHistoryDrawer")
            self.assertEqual(HistoryDrawerState.last_message, "Rendered fallback")

            HistoryDrawerState.last_message = "pending"
            with (
                patch.object(
                    history_drawer, "guard_surface_request", return_value=False
                ) as guard,
                patch.object(history_drawer, "last_drop_reason", return_value=""),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
            ):
                self.assertFalse(history_drawer._reject_if_request_in_flight())
            guard.assert_called_once()
            set_reason.assert_called_once_with("")
            self.assertEqual(HistoryDrawerState.last_message, "")

        def test_reject_if_request_in_flight_preserves_pending_reason(self) -> None:
            HistoryDrawerState.last_message = "pending"
            with (
                patch.object(
                    history_drawer, "guard_surface_request", return_value=False
                ),
                patch.object(
                    history_drawer, "last_drop_reason", return_value="pending"
                ),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
            ):
                self.assertFalse(history_drawer._reject_if_request_in_flight())
            set_reason.assert_not_called()
            self.assertEqual(HistoryDrawerState.last_message, "")

        def test_history_drawer_uses_lifecycle_drop_helpers(self) -> None:
            import talon_user.lib.historyLifecycle as history_lifecycle

            self.assertIs(
                history_drawer.set_drop_reason, history_lifecycle.set_drop_reason
            )
            self.assertIs(
                history_drawer.last_drop_reason, history_lifecycle.last_drop_reason
            )
            self.assertIs(
                history_drawer.consume_last_drop_reason_record,
                history_lifecycle.consume_last_drop_reason_record,
            )

else:
    if not TYPE_CHECKING:

        class RequestHistoryDrawerGatingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
