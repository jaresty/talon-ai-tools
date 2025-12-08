import unittest
from unittest.mock import MagicMock, patch

from talon_user.lib import pillCanvas
from talon_user.lib.requestState import RequestPhase


class PillCanvasClickTests(unittest.TestCase):
    def test_click_cancel_calls_cancel_request(self):
        with patch.object(pillCanvas, "actions") as actions_mock, patch.object(
            pillCanvas, "hide_pill"
        ) as hide_pill:
            actions_mock.user.gpt_cancel_request = MagicMock()
            actions_mock.user.model_response_canvas_open = MagicMock()

            pillCanvas.handle_pill_click(RequestPhase.SENDING)

            actions_mock.user.gpt_cancel_request.assert_called_once()
            actions_mock.user.model_response_canvas_open.assert_not_called()
            hide_pill.assert_called_once()

    def test_click_terminal_opens_response_canvas(self):
        with patch.object(pillCanvas, "actions") as actions_mock, patch.object(
            pillCanvas, "hide_pill"
        ) as hide_pill:
            actions_mock.user.gpt_cancel_request = MagicMock()
            actions_mock.user.model_response_canvas_open = MagicMock()

            pillCanvas.handle_pill_click(RequestPhase.DONE)

            actions_mock.user.model_response_canvas_open.assert_called_once()
            actions_mock.user.gpt_cancel_request.assert_not_called()
            hide_pill.assert_called_once()

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
            patch.object(pillCanvas, "cron") as cron_mock,
        ):
            ui_mock.main_screen.return_value = Screen()
            ui_mock.Rect.side_effect = (
                lambda x, y, w, h: type("Rect", (), {"x": x, "y": y, "width": w, "height": h})()
            )
            dummy_canvas = MagicMock()
            ensure_canvas.return_value = dummy_canvas
            actions_mock.user.notify = MagicMock()
            cron_mock.after.side_effect = lambda _, fn: fn()

            pillCanvas.show_pill("Sending", RequestPhase.SENDING)

            # Top-left placement: x = origin_x + margin, y = origin_y + margin
            self.assertEqual(pillCanvas._pill_rect.x, 120)
            self.assertEqual(pillCanvas._pill_rect.y, 0)
            dummy_canvas.rect = pillCanvas._pill_rect
