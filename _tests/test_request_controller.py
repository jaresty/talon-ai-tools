import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestController import RequestUIController
    from talon_user.lib.requestState import (
        RequestEvent,
        RequestEventKind,
        RequestPhase,
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
else:
    if not TYPE_CHECKING:
        class RequestUIControllerTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
