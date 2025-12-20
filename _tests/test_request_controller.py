import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from unittest.mock import patch

    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import (
        RequestEvent,
        RequestEventKind,
        RequestPhase,
        RequestState,
        Surface,
    )

    class RequestUIControllerTests(unittest.TestCase):
        def test_opens_and_closes_surfaces_on_phase_changes(self):
            calls = []

            def show_pill():
                calls.append("show_pill")

            def hide_pill():
                calls.append("hide_pill")

            def show_conf():
                calls.append("show_conf")

            def hide_conf():
                calls.append("hide_conf")

            def show_response():
                calls.append("show_response")

            def hide_response():
                calls.append("hide_response")

            def hide_hub():
                calls.append("hide_hub")

            controller = RequestUIController(
                show_pill=show_pill,
                hide_pill=hide_pill,
                show_confirmation=show_conf,
                hide_confirmation=hide_conf,
                show_response_canvas=show_response,
                hide_response_canvas=hide_response,
                hide_help_hub=hide_hub,
            )

            controller.handle(RequestEvent(RequestEventKind.GOT_TRANSCRIPT))
            self.assertEqual(controller.state.active_surface, Surface.CONFIRMATION_CHIP)
            self.assertIn("show_conf", calls)
            self.assertIn("hide_hub", calls)

            controller.handle(
                RequestEvent(RequestEventKind.CONFIRM_SEND, request_id="r1")
            )
            self.assertEqual(controller.state.active_surface, Surface.PILL)
            # Confirmation closed, pill opened.
            self.assertIn("hide_conf", calls)
            self.assertIn("show_pill", calls)

            controller.handle(RequestEvent(RequestEventKind.COMPLETE))
            self.assertEqual(controller.state.phase, RequestPhase.DONE)
            self.assertEqual(controller.state.active_surface, Surface.RESPONSE_CANVAS)
            # Pill closed, response opened.
            self.assertIn("hide_pill", calls)
            self.assertIn("show_response", calls)

        def test_terminal_states_close_transients(self):
            calls = []

            def hide_pill():
                calls.append("hide_pill")

            def hide_conf():
                calls.append("hide_conf")

            controller = RequestUIController(
                hide_pill=hide_pill,
                hide_confirmation=hide_conf,
            )
            controller.handle(RequestEvent(RequestEventKind.CONFIRM_SEND))
            controller.handle(RequestEvent(RequestEventKind.FAIL, error="timeout"))
            self.assertEqual(controller.state.phase, RequestPhase.ERROR)
            self.assertIn("hide_pill", calls)
            self.assertIn("hide_conf", calls)

        def test_history_saved_invokes_hook(self):
            calls = []

            def on_history_save(req_id, path):
                calls.append((req_id, path))

            controller = RequestUIController(on_history_save=on_history_save)
            controller.handle(
                RequestEvent(
                    RequestEventKind.HISTORY_SAVED,
                    request_id="rid-1",
                    payload="/tmp/file.md",
                )
            )
            self.assertEqual(calls, [("rid-1", "/tmp/file.md")])
            # State unchanged.
            self.assertEqual(controller.state.phase, RequestPhase.IDLE)

        def test_append_invokes_hook_without_state_change(self):
            calls = []

            def on_append(req_id, chunk):
                calls.append((req_id, chunk))

            controller = RequestUIController(on_append=on_append)
            controller.handle(
                RequestEvent(
                    RequestEventKind.APPEND,
                    request_id="rid-2",
                    payload="hello",
                )
            )
            self.assertEqual(calls, [("rid-2", "hello")])
            self.assertEqual(controller.state.phase, RequestPhase.IDLE)

        def test_reset_calls_state_change_even_when_idle(self):
            calls = []

            def on_state_change(state):
                calls.append(state.phase)

            controller = RequestUIController(on_state_change=on_state_change)
            # Reset from idle; should still emit state change to allow cleanup hooks.
            controller.handle(RequestEvent(RequestEventKind.RESET))
            self.assertEqual(calls, [RequestPhase.IDLE])

        def test_retry_invokes_hook_and_updates_state(self):
            calls = []

            def on_retry(req_id):
                calls.append(req_id)

            controller = RequestUIController(on_retry=on_retry)
            controller.handle(
                RequestEvent(RequestEventKind.RETRY, request_id="rid-retry")
            )

            self.assertEqual(calls, ["rid-retry"])
            self.assertEqual(controller.state.phase, RequestPhase.STREAMING)
            self.assertEqual(controller.state.request_id, "rid-retry")
            self.assertEqual(controller.state.active_surface, Surface.PILL)

        def test_retry_from_error_clears_error_and_moves_to_streaming(self):
            calls = []

            def on_retry(req_id):
                calls.append(req_id)

            controller = RequestUIController(on_retry=on_retry)
            controller._state = RequestState(
                phase=RequestPhase.ERROR,
                active_surface=Surface.RESPONSE_CANVAS,
                request_id="rid-error",
                last_error="boom",
            )
            controller.handle(
                RequestEvent(RequestEventKind.RETRY, request_id="rid-error")
            )

            self.assertEqual(calls, ["rid-error"])
            self.assertEqual(controller.state.phase, RequestPhase.STREAMING)
            self.assertEqual(controller.state.active_surface, Surface.PILL)
            self.assertEqual(controller.state.request_id, "rid-error")
            self.assertEqual(controller.state.last_error, "")

        def test_retry_from_cancel_clears_cancel_flag_and_moves_to_streaming(self):
            calls = []

            def on_retry(req_id):
                calls.append(req_id)

            controller = RequestUIController(on_retry=on_retry)
            controller._state = RequestState(
                phase=RequestPhase.CANCELLED,
                active_surface=Surface.NONE,
                request_id="rid-cancel",
                cancel_requested=True,
            )
            controller.handle(
                RequestEvent(RequestEventKind.RETRY, request_id="rid-cancel")
            )

            self.assertEqual(calls, ["rid-cancel"])
            self.assertEqual(controller.state.phase, RequestPhase.STREAMING)
            self.assertEqual(controller.state.active_surface, Surface.PILL)
            self.assertEqual(controller.state.request_id, "rid-cancel")
            self.assertFalse(controller.state.cancel_requested)
            self.assertEqual(controller.state.active_surface, Surface.PILL)

        def test_is_in_flight_delegates_to_request_state_helper(self) -> None:
            controller = RequestUIController()
            self.assertFalse(
                controller.is_in_flight(),
                "Idle controller state should not be considered in-flight",
            )

            controller.handle(
                RequestEvent(RequestEventKind.BEGIN_SEND, request_id="rid-inflight")
            )
            self.assertTrue(
                controller.is_in_flight(),
                "BEGIN_SEND should mark the controller as in-flight",
            )

            controller.handle(
                RequestEvent(RequestEventKind.COMPLETE, request_id="rid-inflight")
            )
            self.assertFalse(
                controller.is_in_flight(),
                "Terminal states should clear in-flight gating",
            )

        def test_try_start_request_returns_drop_reason(self) -> None:
            controller = RequestUIController()
            allowed, reason = controller.try_start_request()
            self.assertTrue(allowed)
            self.assertEqual(reason, "")

            controller.handle(
                RequestEvent(RequestEventKind.BEGIN_STREAM, request_id="rid-gating")
            )
            allowed, reason = controller.try_start_request()
            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")

        def test_is_in_flight_uses_request_lifecycle_facade(self) -> None:
            controller = RequestUIController()
            controller.handle(
                RequestEvent(RequestEventKind.BEGIN_SEND, request_id="rid-lifecycle")
            )

            with patch(
                "talon_user.lib.requestController.lifecycle_is_in_flight",
                return_value=True,
            ) as mock_is_in_flight:
                result = controller.is_in_flight()

            self.assertTrue(result)
            mock_is_in_flight.assert_called_once()
            lifecycle_state = mock_is_in_flight.call_args[0][0]
            self.assertEqual(lifecycle_state.status, "running")

        def test_try_start_request_uses_request_lifecycle_facade(self) -> None:
            controller = RequestUIController()
            controller.handle(
                RequestEvent(RequestEventKind.BEGIN_STREAM, request_id="rid-lifecycle")
            )

            with patch(
                "talon_user.lib.requestController.lifecycle_try_start_request",
                return_value=(False, "in_flight"),
            ) as mock_try_start:
                allowed, reason = controller.try_start_request()

            self.assertFalse(allowed)
            self.assertEqual(reason, "in_flight")
            mock_try_start.assert_called_once()
            lifecycle_state = mock_try_start.call_args[0][0]
            self.assertEqual(lifecycle_state.status, "streaming")
else:
    if not TYPE_CHECKING:

        class RequestUIControllerTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
