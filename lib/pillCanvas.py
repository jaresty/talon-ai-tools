"""Canvas-based progress pill overlay.

Provides a small, draggable pill that reflects request lifecycle state and
offers a click-to-cancel affordance when cancellation is supported.
"""

from __future__ import annotations

from typing import Optional

from talon import Module, actions, app, canvas, ui, settings, cron

from .requestState import RequestPhase

mod = Module()


class PillState:
    showing: bool = False
    text: str = "Model"
    phase: RequestPhase = RequestPhase.IDLE
    hover: bool = False


_pill_canvas: Optional[canvas.Canvas] = None
_pill_rect = ui.Rect(20, 20, 220, 40)
_DEFAULT_WIDTH = 220
_DEFAULT_HEIGHT = 40
_MARGIN = 20


def _default_rect() -> ui.Rect:
    """Place the pill near the top-right of the main screen."""
    try:
        screen = ui.main_screen()
        width = getattr(screen, "width", 0) or 0
        height = getattr(screen, "height", 0) or 0
        origin_x = getattr(screen, "x", 0) or 0
        origin_y = getattr(screen, "y", 0) or 0
        # Default to top-left to avoid off-screen placement on complex layouts.
        x = origin_x + _MARGIN
        y = origin_y + _MARGIN
        _debug(
            f"default rect screen=({origin_x},{origin_y},{width},{height}) "
            f"rect=({x},{y},{_DEFAULT_WIDTH},{_DEFAULT_HEIGHT})"
        )
        return ui.Rect(x, y, _DEFAULT_WIDTH, _DEFAULT_HEIGHT)
    except Exception:
        return ui.Rect(20, 20, _DEFAULT_WIDTH, _DEFAULT_HEIGHT)


def _pill_color_for_phase(phase: RequestPhase) -> str:
    if phase in (RequestPhase.SENDING, RequestPhase.STREAMING):
        return "4A90E2"  # blue
    if phase is RequestPhase.ERROR:
        return "D0021B"  # red
    if phase is RequestPhase.CANCELLED:
        return "9B9B9B"  # gray
    if phase is RequestPhase.DONE:
        return "7ED321"  # green
    return "9B9B9B"  # default gray


def _debug(msg: str) -> None:
    try:
        enabled = settings.get("user.model_debug_pill", False)
    except Exception:
        enabled = False
    if not enabled:
        return
    try:
        print(f"[pill] {msg}")
    except Exception:
        pass


def _ensure_pill_canvas() -> canvas.Canvas:
    global _pill_canvas
    if _pill_canvas is not None:
        _debug("reusing existing pill canvas")
        return _pill_canvas

    # Prefer a rect-based canvas; fall back to full screen if it fails.
    try:
        _pill_canvas = canvas.Canvas.from_rect(_pill_rect)
        _debug(
            f"pill canvas created from rect ({_pill_rect.x},{_pill_rect.y},{_pill_rect.width},{_pill_rect.height})"
        )
    except Exception as e:
        _debug(f"pill canvas from_rect failed: {e}")
        _pill_canvas = None
    if _pill_canvas is None:
        try:
            _pill_canvas = canvas.Canvas.from_screen(ui.main_screen())
            _debug("created pill canvas from screen fallback")
        except Exception as e:
            _debug(f"pill canvas from_screen failed: {e}")
            _pill_canvas = None
    if _pill_canvas is None:
        _debug("failed to create pill canvas")
        # Leave as None; notify fallback will still show text.
        return None  # type: ignore[return-value]

    try:
        _pill_canvas.blocks_mouse = True
    except Exception:
        pass

    def _on_draw(c: canvas.Canvas):
        rect = getattr(c, "rect", _pill_rect)
        paint = getattr(c, "paint", None)
        if rect is None or paint is None:
            _debug("pill draw skipped (rect or paint missing)")
            return
        # Background
        try:
            old_color = paint.color
            paint.color = _pill_color_for_phase(PillState.phase)
            c.draw_rect(rect)
            paint.color = "FFFFFF"
            text = PillState.text or "Model"
            # Center text vertically
            text_y = rect.y + rect.height // 2 + 5
            c.draw_text(text, rect.x + 12, text_y)
            paint.color = old_color
        except Exception:
            pass

    def _on_mouse(evt):
        event_type = getattr(evt, "event", "") or ""
        button = getattr(evt, "button", None)
        if event_type in ("mousedown", "mouse_down") and button in (0, 1):
            handle_pill_click(PillState.phase)

    try:
        _pill_canvas.register("draw", _on_draw)
        _pill_canvas.register("mouse", _on_mouse)
    except Exception:
        pass
    return _pill_canvas


def _show_canvas(display_text: str, phase: RequestPhase) -> None:
    """Create/show the canvas on the main thread (cron) to avoid threading issues."""
    c = _ensure_pill_canvas()
    # Ensure the canvas reflects the latest rect when reused.
    _apply_rect(_pill_rect)
    try:
        if c is not None:
            c.show()
        else:
            _debug("pill canvas unavailable")
    except Exception as e:
        _debug(f"pill canvas show failed: {e}")


def _apply_rect(rect: ui.Rect) -> None:
    """Update the pill rect and apply to the canvas, recreating if needed."""
    global _pill_canvas, _pill_rect
    _pill_rect = rect
    if _pill_canvas is None:
        return
    try:
        _pill_canvas.rect = rect
    except Exception:
        _debug("Recreating pill canvas due to rect apply failure")
        # If direct assignment fails, recreate the canvas at the new location.
        try:
            _pill_canvas.close()
        except Exception:
            pass
        _pill_canvas = None
        try:
            _pill_canvas = canvas.Canvas.from_rect(_pill_rect)
        except Exception:
            _pill_canvas = None


def show_pill(text: str, phase: RequestPhase) -> None:
    # Place the pill near the right-hand side on every show.
    _apply_rect(_default_rect())
    PillState.phase = phase
    # Surface a simple affordance hint depending on phase.
    if phase in (RequestPhase.SENDING, RequestPhase.STREAMING):
        display_text = f"{text} (click to cancel)"
    elif phase in (RequestPhase.DONE, RequestPhase.ERROR, RequestPhase.CANCELLED):
        display_text = f"{text} (open response)"
    else:
        display_text = text
    PillState.text = display_text
    PillState.phase = phase
    PillState.showing = True
    _debug(
        f"Show pill: '{display_text}' phase={phase.name} rect=({_pill_rect.x}, {_pill_rect.y}, {_pill_rect.width}, {_pill_rect.height})"
    )
    # Best-effort toast in case canvas is not visible or available.
    try:
        actions.user.notify(display_text)
    except Exception:
        try:
            app.notify(display_text)
        except Exception:
            pass
    # Schedule on the main thread to ensure an active resource context; also
    # retry shortly after in case the resource context is briefly unavailable.
    def _try_show():
        try:
            _show_canvas(display_text, phase)
        except Exception as e:
            _debug(f"pill canvas show failed: {e}")
    try:
        cron.after("0ms", _try_show)
        cron.after("50ms", _try_show)
    except Exception as e:
        _debug(f"cron dispatch failed, showing directly: {e}")
        _try_show()


def hide_pill() -> None:
    PillState.showing = False
    _debug("Hide pill")
    if _pill_canvas is not None:
        try:
            _pill_canvas.hide()
        except Exception:
            pass


def handle_pill_click(phase: RequestPhase) -> None:
    """Handle a pill click based on the current request phase."""
    try:
        if phase in (RequestPhase.SENDING, RequestPhase.STREAMING):
            # Best-effort cancel while in-flight.
            actions.user.gpt_cancel_request()
            _debug(f"Pill click: cancel (phase={phase.name})")
        elif phase in (RequestPhase.DONE, RequestPhase.ERROR, RequestPhase.CANCELLED):
            # After completion/error, let users reopen the last response canvas.
            actions.user.model_response_canvas_open()
            _debug(f"Pill click: open response (phase={phase.name})")
    except Exception:
        # Swallow to avoid breaking the pill overlay on click.
        pass
    hide_pill()


__all__ = ["show_pill", "hide_pill", "handle_pill_click"]
