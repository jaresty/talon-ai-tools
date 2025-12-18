"""Canvas-based request history drawer."""

from __future__ import annotations

from typing import List, Optional, Tuple
from collections.abc import Sequence

from talon import Module, actions, canvas, ui

from .requestLog import (
    all_entries,
    consume_last_drop_reason_record,
    drop_reason_message,
    set_drop_reason,
)
from .historyQuery import history_drawer_entries_from
from .requestBus import current_state
from .requestState import is_in_flight, try_start_request
from .modelHelpers import notify
from .overlayHelpers import apply_canvas_blocking
from .overlayLifecycle import close_overlays, close_common_overlays

mod = Module()


class HistoryDrawerState:
    showing: bool = False
    entries: List[
        Tuple[str, str]
    ] = []  # (request_id, prompt_snippet + recipe + provider)
    selected_index: int = 0
    last_message: str = ""


_history_canvas: Optional[canvas.Canvas] = None
_button_bounds: List[Tuple[int, int, int, int, int]] = []  # (idx, x1, y1, x2, y2)
_last_key_handler = None


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running.

    This delegates to the central ``is_in_flight`` helper so history drawer
    gating stays aligned with the RequestState/RequestLifecycle contract.
    """
    try:
        state = current_state()
    except Exception:
        return False
    try:
        return is_in_flight(state)  # type: ignore[arg-type]
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""
    try:
        state = current_state()
    except Exception:
        return False
    try:
        allowed, reason = try_start_request(state)  # type: ignore[arg-type]
    except Exception:
        return False
    if not allowed and reason == "in_flight":
        message = drop_reason_message("in_flight")
        try:
            set_drop_reason("in_flight")
        except Exception:
            pass
        notify(message)
        return True
    return False


def _ensure_canvas() -> canvas.Canvas:
    global _history_canvas
    if _history_canvas is not None:
        return _history_canvas

    rect = ui.Rect(40, 80, 520, 260)
    _history_canvas = canvas.Canvas.from_rect(rect)
    apply_canvas_blocking(_history_canvas)

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
            message = HistoryDrawerState.last_message or "No history yet."
            for line in message.splitlines() or [message]:
                if not line:
                    y += line_h
                    continue
                draw_text(line, x, y)
                y += line_h
            draw_text("Press s to save latest source.", x, y)
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
        elif key == "s":
            try:
                actions.user.request_history_drawer_save_latest_source()
            except Exception:
                pass
        elif key in ("escape", "esc"):
            try:
                actions.user.request_history_drawer_close()
            except Exception:
                try:
                    UserActions.request_history_drawer_close()  # type: ignore[attr-defined]
                except Exception:
                    pass
            # Ensure state reflects closure even if actions stubs do nothing.
            HistoryDrawerState.showing = False

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
            0,
            min(HistoryDrawerState.selected_index, len(HistoryDrawerState.entries) - 1),
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
        global _last_key_handler
        _last_key_handler = _on_key
    except Exception:
        pass
    return _history_canvas


def _refresh_entries() -> None:
    try:
        entries = list(reversed(all_entries()))
    except Exception as e:
        try:
            print(f"[requestHistoryDrawer] failed to load entries: {e}")
        except Exception:
            pass
        HistoryDrawerState.entries = []
        HistoryDrawerState.selected_index = 0
        HistoryDrawerState.last_message = ""
        return
    try:
        print(f"[requestHistoryDrawer] refresh entries={len(entries)}")
    except Exception:
        pass
    try:
        HistoryDrawerState.entries = history_drawer_entries_from(entries)
    except ValueError as exc:
        HistoryDrawerState.entries = []
        HistoryDrawerState.selected_index = 0
        details = str(exc).strip()
        problem_line = (
            f"Details: {details}"
            if details
            else "Unsupported axis keys detected in stored entries."
        )
        HistoryDrawerState.last_message = (
            "History validation failed: stored entries include unsupported axis keys.\n"
            f"{problem_line}\n"
            "Run `python3 scripts/tools/history-axis-validate.py` to inspect and clean legacy entries."
        )
        return
    HistoryDrawerState.selected_index = 0
    HistoryDrawerState.last_message = ""
    if not HistoryDrawerState.entries:
        try:
            record = consume_last_drop_reason_record()
            HistoryDrawerState.last_message = record.message
        except Exception:
            HistoryDrawerState.last_message = ""
        if not HistoryDrawerState.last_message:
            HistoryDrawerState.last_message = "GPT: No history entries include a directional lens; replay requires fog/fig/dig/ong/rog/bog/jog."


@mod.action_class
class UserActions:
    def request_history_drawer_toggle():
        """Toggle the request history drawer"""
        if _reject_if_request_in_flight():
            return
        if HistoryDrawerState.showing:
            actions.user.request_history_drawer_close()
            return
        actions.user.request_history_drawer_open()

    def request_history_drawer_open():
        """Open the request history drawer"""
        if _reject_if_request_in_flight():
            return
        close_common_overlays(actions.user)
        _refresh_entries()
        c = _ensure_canvas()
        HistoryDrawerState.showing = True
        try:
            c.show()
        except Exception:
            pass

    def request_history_drawer_close():
        """Close the request history drawer"""
        if _reject_if_request_in_flight():
            return
        HistoryDrawerState.showing = False
        if _history_canvas is None:
            return
        try:
            _history_canvas.hide()
        except Exception:
            pass

    def request_history_drawer_prev_entry():
        """Move selection to previous entry in the history drawer"""
        if _reject_if_request_in_flight():
            return
        if not HistoryDrawerState.entries:
            return
        HistoryDrawerState.selected_index = max(
            0, HistoryDrawerState.selected_index - 1
        )
        c = _ensure_canvas()
        try:
            c.show()
        except Exception:
            pass

    def request_history_drawer_next_entry():
        """Move selection to next entry in the history drawer"""
        if _reject_if_request_in_flight():
            return
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
        if _reject_if_request_in_flight():
            return
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

    def request_history_drawer_save_latest_source():
        """Save latest source, refresh the drawer, and surface new entry if available."""
        if _reject_if_request_in_flight():
            return None
        close_common_overlays(actions.user)
        result = None
        try:
            result = actions.user.gpt_request_history_save_latest_source()  # type: ignore[attr-defined]
        except Exception:
            result = None
        _refresh_entries()
        c = _ensure_canvas()
        HistoryDrawerState.showing = True
        try:
            c.show()
        except Exception:
            pass
        return result

    def request_history_drawer_refresh():
        """Refresh entries when the drawer is showing (e.g., after a history save)."""
        if not HistoryDrawerState.showing:
            return
        if _reject_if_request_in_flight():
            return
        _refresh_entries()
        c = _ensure_canvas()
        try:
            c.show()
        except Exception:
            pass
