"""Canvas-based request history drawer."""

from __future__ import annotations

from typing import List, Optional, Tuple

from talon import Module, actions, canvas, ui

from .requestLog import all_entries

mod = Module()


class HistoryDrawerState:
    showing: bool = False
    entries: List[Tuple[str, str]] = []  # (request_id, prompt_snippet)
    selected_index: int = 0


_history_canvas: Optional[canvas.Canvas] = None
_button_bounds: List[Tuple[int, int, int, int, int]] = []  # (idx, x1, y1, x2, y2)


def _ensure_canvas() -> canvas.Canvas:
    global _history_canvas
    if _history_canvas is not None:
        return _history_canvas

    rect = ui.Rect(40, 80, 520, 260)
    _history_canvas = canvas.Canvas.from_rect(rect)
    try:
        _history_canvas.blocks_mouse = True
        if hasattr(_history_canvas, "block_mouse"):
            _history_canvas.block_mouse = True  # type: ignore[attr-defined]
    except Exception:
        pass

    def _on_draw(c: canvas.Canvas):
        rect = getattr(c, "rect", None) or ui.Rect(40, 80, 520, 260)
        paint = getattr(c, "paint", None)
        draw_text = getattr(c, "draw_text", None)
        if draw_text is None:
            return
        _button_bounds.clear()
        try:
            if paint:
                old_color = paint.color
                paint.color = "F7F7F7"
                c.draw_rect(rect)
                paint.color = old_color
        except Exception:
            pass

        x = rect.x + 12
        y = rect.y + 24
        line_h = 18
        draw_text("Model request history", x, y)
        y += line_h
        if not HistoryDrawerState.entries:
            draw_text("No history yet.", x, y)
            return

        draw_text("Newest first (click to open):", x, y)
        y += line_h
        for idx, (req_id, snippet) in enumerate(HistoryDrawerState.entries):
            text = f"{idx}: {req_id} | {snippet}"
            # Highlight selected entry.
            if idx == HistoryDrawerState.selected_index and paint is not None:
                try:
                    old_color = paint.color
                    paint.color = "E6F7FF"
                    c.draw_rect(ui.Rect(x - 6, y - line_h + 4, rect.width - 24, line_h))
                    paint.color = old_color
                except Exception:
                    pass
            draw_text(text, x, y)
            _button_bounds.append((idx, x, y - line_h + 4, x + len(text) * 7, y + 2))
            y += line_h

    def _on_mouse(evt):
        event_type = getattr(evt, "event", "") or ""
        button = getattr(evt, "button", None)
        if event_type in ("mousedown", "mouse_down") and button in (0, 1):
            pos = getattr(evt, "pos", None)
            rect = getattr(_history_canvas, "rect", None)
            if pos is None or rect is None:
                return
            abs_x = rect.x + pos.x
            abs_y = rect.y + pos.y
            for idx, x1, y1, x2, y2 in list(_button_bounds):
                if x1 <= abs_x <= x2 and y1 <= abs_y <= y2:
                    HistoryDrawerState.selected_index = idx
                    _open_selected()
                    return

    def _on_key(evt):
        if not getattr(evt, "down", False):
            return
        key = (getattr(evt, "key", "") or "").lower()
        if key in ("up", "k"):
            actions.user.request_history_drawer_prev_entry()
        elif key in ("down", "j"):
            actions.user.request_history_drawer_next_entry()
        elif key in ("enter", "return"):
            _open_selected()

    def _open_selected():
        idx = HistoryDrawerState.selected_index
        try:
            actions.user.gpt_request_history_show_previous(idx)
        except Exception:
            pass
        try:
            actions.user.request_history_drawer_close()
        except Exception:
            pass
        return

    def _clamp_selection():
        if not HistoryDrawerState.entries:
            HistoryDrawerState.selected_index = 0
            return
        HistoryDrawerState.selected_index = max(
            0, min(HistoryDrawerState.selected_index, len(HistoryDrawerState.entries) - 1)
        )

    def _on_mouse(evt):
        event_type = getattr(evt, "event", "") or ""
        button = getattr(evt, "button", None)
        if event_type in ("mousedown", "mouse_down") and button in (0, 1):
            pos = getattr(evt, "pos", None)
            rect = getattr(_history_canvas, "rect", None)
            if pos is None or rect is None:
                return
            abs_x = rect.x + pos.x
            abs_y = rect.y + pos.y
            for idx, x1, y1, x2, y2 in list(_button_bounds):
                if x1 <= abs_x <= x2 and y1 <= abs_y <= y2:
                    HistoryDrawerState.selected_index = idx
                    _clamp_selection()
                    try:
                        actions.user.gpt_request_history_show_previous(idx)
                    except Exception:
                        pass
                    try:
                        actions.user.request_history_drawer_close()
                    except Exception:
                        pass
                    return

    try:
        _history_canvas.register("draw", _on_draw)
        _history_canvas.register("mouse", _on_mouse)
        _history_canvas.register("key", _on_key)
    except Exception:
        pass
    return _history_canvas


def _refresh_entries() -> None:
    entries = list(reversed(all_entries()))
    rendered: List[Tuple[str, str]] = []
    for entry in entries:
        prompt = (entry.prompt or "").strip().splitlines()[0] if entry.prompt else ""
        snippet = prompt[:80] + ("…" if len(prompt) > 80 else "")
        dur = f"{entry.duration_ms}ms" if entry.duration_ms is not None else ""
        label = f"{entry.request_id}"
        if dur:
            label = f"{label} ({dur})"
        rendered.append((label, snippet))
    HistoryDrawerState.entries = rendered
    HistoryDrawerState.selected_index = 0


@mod.action_class
class UserActions:
    def request_history_drawer_toggle():
        """Toggle the request history drawer"""
        if HistoryDrawerState.showing:
            actions.user.request_history_drawer_close()
            return
        actions.user.request_history_drawer_open()

    def request_history_drawer_open():
        """Open the request history drawer"""
        _refresh_entries()
        c = _ensure_canvas()
        HistoryDrawerState.showing = True
        try:
            c.show()
        except Exception:
            pass

    def request_history_drawer_close():
        """Close the request history drawer"""
        HistoryDrawerState.showing = False
        if _history_canvas is None:
            return
        try:
            _history_canvas.hide()
        except Exception:
            pass

    def request_history_drawer_prev_entry():
        """Move selection to previous entry in the history drawer"""
        if not HistoryDrawerState.entries:
            return
        HistoryDrawerState.selected_index = max(0, HistoryDrawerState.selected_index - 1)
        c = _ensure_canvas()
        try:
            c.show()
        except Exception:
            pass

    def request_history_drawer_next_entry():
        """Move selection to next entry in the history drawer"""
        if not HistoryDrawerState.entries:
            return
        HistoryDrawerState.selected_index = min(
            len(HistoryDrawerState.entries) - 1, HistoryDrawerState.selected_index + 1
        )
        c = _ensure_canvas()
        try:
            c.show()
        except Exception:
            pass

    def request_history_drawer_open_selected():
        """Open the currently selected entry in the history drawer"""
        if not HistoryDrawerState.entries:
            return
        idx = HistoryDrawerState.selected_index
        try:
            actions.user.gpt_request_history_show_previous(idx)
        except Exception:
            pass
        try:
            actions.user.request_history_drawer_close()
        except Exception:
            pass
