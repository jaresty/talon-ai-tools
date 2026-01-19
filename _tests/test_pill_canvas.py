import unittest
from unittest.mock import MagicMock, patch

from talon_user.lib import pillCanvas
from talon_user.lib.requestState import RequestPhase


class PillCanvasClickTests(unittest.TestCase):
    def setUp(self):
        pillCanvas.PillState.showing = False
        pillCanvas.PillState.text = "Model"
        pillCanvas.PillState.phase = RequestPhase.IDLE
        pillCanvas.PillState.generation = 0
        pillCanvas._pill_canvas = None

    def test_click_cancel_calls_cancel_request(self):
        with (
            patch.object(pillCanvas, "actions") as actions_mock,
            patch.object(pillCanvas, "hide_pill") as hide_pill,
        ):
            actions_mock.user.gpt_cancel_request = MagicMock()
            actions_mock.user.model_response_canvas_open = MagicMock()

            pillCanvas.handle_pill_click(RequestPhase.SENDING)
            pillCanvas.handle_pill_click(RequestPhase.SENDING, "cancel")

            self.assertEqual(actions_mock.user.gpt_cancel_request.call_count, 2)
            actions_mock.user.model_response_canvas_open.assert_not_called()
            self.assertEqual(hide_pill.call_count, 2)

    def test_click_terminal_opens_response_canvas(self):
        with (
            patch.object(pillCanvas, "actions") as actions_mock,
            patch.object(pillCanvas, "hide_pill") as hide_pill,
        ):
            actions_mock.user.gpt_cancel_request = MagicMock()
            actions_mock.user.model_response_canvas_open = MagicMock()

            pillCanvas.handle_pill_click(RequestPhase.DONE)
            pillCanvas.handle_pill_click(RequestPhase.DONE, "show")

            self.assertEqual(actions_mock.user.model_response_canvas_open.call_count, 2)
            actions_mock.user.gpt_cancel_request.assert_not_called()
            self.assertEqual(hide_pill.call_count, 2)

    def test_pill_positions_near_right(self):
        class Screen:
            width = 800
            height = 600
            x = 100
            y = -20

        with (
            patch.object(pillCanvas, "ui") as ui_mock,
            patch.object(pillCanvas, "_ensure_pill_canvas") as ensure_canvas,
            patch.object(pillCanvas, "actions") as actions_mock,
            patch.object(pillCanvas, "run_on_ui_thread") as run_mock,
        ):
            ui_mock.main_screen.return_value = Screen()
            ui_mock.Rect.side_effect = lambda x, y, w, h: type(
                "Rect", (), {"x": x, "y": y, "width": w, "height": h}
            )()
            dummy_canvas = MagicMock()
            ensure_canvas.return_value = dummy_canvas
            actions_mock.user.notify = MagicMock()
            run_mock.side_effect = lambda fn, delay_ms=0: fn()

            pillCanvas.show_pill("Sending", RequestPhase.SENDING)

            # Top-left placement: x = origin_x + margin, y = origin_y + margin
            self.assertEqual(pillCanvas._pill_rect.x, 120)
            self.assertEqual(pillCanvas._pill_rect.y, 0)
            dummy_canvas.rect = pillCanvas._pill_rect

    def test_show_pill_dispatches_on_ui_thread(self):
        class Rect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

        dispatched_delays = []

        def run_on_ui_thread(fn, delay_ms=0):
            dispatched_delays.append(delay_ms)
            fn()

        rect = Rect(10, 20, 30, 40)

        with (
            patch.object(
                pillCanvas, "run_on_ui_thread", side_effect=run_on_ui_thread
            ) as run_mock,
            patch.object(pillCanvas, "_default_rect", return_value=rect),
            patch.object(pillCanvas, "_show_canvas") as show_canvas,
            patch.object(pillCanvas, "actions") as actions_mock,
        ):
            actions_mock.user.notify = MagicMock()
            pillCanvas.show_pill("Sending", RequestPhase.SENDING)

            # Two scheduled attempts (immediate and retry).
            self.assertEqual(run_mock.call_count, 2)
            self.assertIn(0, dispatched_delays)
            self.assertIn(50, dispatched_delays)
            show_canvas.assert_called_with("Sending", RequestPhase.SENDING, rect)

    def test_hide_pill_dispatches_on_ui_thread(self):
        dispatched = []

        def run_on_ui_thread(fn, delay_ms=0):
            dispatched.append(delay_ms)
            fn()

        dummy_canvas = MagicMock()
        dummy_canvas.close = MagicMock()
        original_canvas = pillCanvas._pill_canvas
        pillCanvas._pill_canvas = dummy_canvas
        try:
            with patch.object(
                pillCanvas, "run_on_ui_thread", side_effect=run_on_ui_thread
            ):
                pillCanvas.hide_pill()

            self.assertEqual(dispatched, [0])
            dummy_canvas.hide.assert_called_once()
            dummy_canvas.close.assert_called_once()
            self.assertIsNone(pillCanvas._pill_canvas)
        finally:
            pillCanvas._pill_canvas = original_canvas

    def test_hide_prevents_late_show_from_background(self):
        # Simulate rapid hide after show scheduling; stale show should be skipped.
        class Rect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

        calls = {"show": 0}
        delayed_fns = []

        def run_on_ui_thread(fn, delay_ms=0):
            # Collect callbacks to run later to simulate async timing.
            delayed_fns.append(fn)

        rect = Rect(0, 0, 10, 10)

        with (
            patch.object(pillCanvas, "run_on_ui_thread", side_effect=run_on_ui_thread),
            patch.object(pillCanvas, "_default_rect", return_value=rect),
            patch.object(pillCanvas, "_show_canvas") as show_canvas,
            patch.object(pillCanvas, "actions") as actions_mock,
        ):
            actions_mock.user.notify = MagicMock()

            pillCanvas.show_pill("Sending", RequestPhase.SENDING)
            pillCanvas.hide_pill()

            # Execute delayed callbacks; stale shows should be skipped.
            for fn in delayed_fns:
                fn()

            show_canvas.assert_not_called()

    def test_show_pill_sets_action_modes(self):
        class Rect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

        rect = Rect(0, 0, 10, 10)

        with (
            patch.object(
                pillCanvas, "run_on_ui_thread", side_effect=lambda fn, delay_ms=0: fn()
            ),
            patch.object(pillCanvas, "_default_rect", return_value=rect),
            patch.object(pillCanvas, "_show_canvas"),
            patch.object(pillCanvas, "actions") as actions_mock,
        ):
            actions_mock.user.notify = MagicMock()

            pillCanvas.show_pill("Sending", RequestPhase.SENDING)
            self.assertEqual(pillCanvas.PillState.action_mode, "dual")

            pillCanvas.show_pill("Done", RequestPhase.DONE)
            self.assertEqual(pillCanvas.PillState.action_mode, "show")

            pillCanvas.show_pill("Idle", RequestPhase.IDLE)
            self.assertEqual(pillCanvas.PillState.action_mode, "none")

    def test_show_pill_skips_redundant_dispatch(self):
        class Rect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

        rect = Rect(0, 0, 10, 10)

        with (
            patch.object(pillCanvas, "run_on_ui_thread") as run_mock,
            patch.object(pillCanvas, "_default_rect", return_value=rect),
            patch.object(pillCanvas, "_show_canvas") as show_canvas,
            patch.object(pillCanvas, "actions") as actions_mock,
        ):
            run_mock.side_effect = lambda fn, delay_ms=0: fn()
            actions_mock.user.notify = MagicMock()

            pillCanvas.show_pill("Sending", RequestPhase.SENDING)
            # Second call with same text/phase should skip dispatch.
            pillCanvas.show_pill("Sending", RequestPhase.SENDING)

            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(show_canvas.call_count, 2)
