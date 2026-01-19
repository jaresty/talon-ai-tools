"""Canvas-based progress pill overlay.

Provides a small, draggable pill that reflects request lifecycle state and
offers a click-to-cancel affordance when cancellation is supported.
"""

from __future__ import annotations

from typing import Callable, Optional

from talon import Module, actions, app, canvas, ui, settings, cron

from .historyLifecycle import RequestPhase
from .uiDispatch import run_on_ui_thread
from .overlayHelpers import apply_canvas_blocking

mod = Module()


class PillState:
    showing: bool = False
    text: str = "Model"
    phase: RequestPhase = RequestPhase.IDLE
    hover: bool = False
    generation: int = 0  # increments each show/hide to ignore stale UI-thread work
    action_mode: str = "none"  # "dual" for cancel+show, "show" for show-only


_pill_canvas: Optional[canvas.Canvas] = None
_pill_button_bounds: list[tuple[str, ui.Rect]] = []
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
        enabled = settings.get("user.model_debug_pill", True)
    except Exception:
        enabled = False
    if not enabled:
        return
    try:
        print(f"[pill] {msg}")
    except Exception:
        pass


# Proactively create the canvas on Talon's ready event to ensure a main-thread
# resource context is available before worker threads attempt to show it.
_warmup_handle = None
_warmup_done = False


def _release_pill_canvas() -> None:
    global _pill_canvas
    canvas_obj = _pill_canvas
    if canvas_obj is None:
        return
    _pill_canvas = None
    try:
        canvas_obj.hide()
    except Exception:
        pass
    close = getattr(canvas_obj, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass


def _stop_pill_warmup(interval: object | None = None) -> None:
    global _warmup_handle
    if interval is not None and interval is not _warmup_handle:
        return
    if _warmup_handle is None:
        return
    try:
        cron.cancel(_warmup_handle)
    except Exception:
        pass
    _warmup_handle = None


def _pill_warmup_tick() -> None:
    global _warmup_done
    if _warmup_done:
        _stop_pill_warmup()
        return
    try:
        if _ensure_pill_canvas() is not None:
            _debug("app ready: pill canvas warmup succeeded; stopping interval")
            _warmup_done = True
            _stop_pill_warmup()
    except Exception as exc:
        _debug(f"app ready warmup failed: {exc}")


def _on_app_ready():
    """Warm up a canvas on the main thread; retry a few times via cron."""
    global _warmup_handle
    if _warmup_done or _warmup_handle is not None:
        return
    try:
        _debug("app ready: scheduling pill canvas warmup")
        _warmup_handle = cron.interval("50ms", _pill_warmup_tick)
    except Exception as exc:
        _debug(f"app ready warmup scheduling failed: {exc}")


try:
    app.register("ready", _on_app_ready)
except Exception:
    pass


def _ensure_pill_canvas() -> canvas.Canvas:
    global _pill_canvas
    created = False
    if _pill_canvas is not None:
        _debug("reusing existing pill canvas")
        return _pill_canvas

    # Prefer a rect-based canvas; fall back to full screen if it fails.
    try:
        _pill_canvas = canvas.Canvas.from_rect(_pill_rect)
        created = True
        _debug(
            f"pill canvas created from rect ({_pill_rect.x},{_pill_rect.y},{_pill_rect.width},{_pill_rect.height})"
        )
    except Exception as e:
        _debug(f"pill canvas from_rect failed: {e}")
        _pill_canvas = None
    if _pill_canvas is None:
        try:
            _pill_canvas = canvas.Canvas.from_screen(ui.main_screen())
            created = True
            _debug("created pill canvas from screen fallback")
        except Exception as e:
            _debug(f"pill canvas from_screen failed: {e}")
            _pill_canvas = None
    if _pill_canvas is None:
        _debug("failed to create pill canvas")
        # Leave as None; notify fallback will still show text.
        return None  # type: ignore[return-value]

    apply_canvas_blocking(_pill_canvas)

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
            label = PillState.text or "Model"
            label_y = rect.y + 16
            c.draw_text(label, rect.x + 12, label_y)
            _pill_button_bounds.clear()
            action_baseline = rect.y + rect.height - 10
            if PillState.action_mode == "dual":
                cancel_text = "Cancel"
                show_text = "Show response"
                c.draw_text(cancel_text, rect.x + 12, action_baseline)
                show_x = rect.x + rect.width // 2 + 12
                c.draw_text(show_text, show_x, action_baseline)
                _pill_button_bounds.append(
                    (
                        "cancel",
                        ui.Rect(
                            rect.x,
                            rect.y + rect.height // 2,
                            rect.width // 2,
                            rect.height // 2,
                        ),
                    )
                )
                _pill_button_bounds.append(
                    (
                        "show",
                        ui.Rect(
                            rect.x + rect.width // 2,
                            rect.y + rect.height // 2,
                            rect.width // 2,
                            rect.height // 2,
                        ),
                    )
                )
            elif PillState.action_mode == "show":
                show_text = "Show response"
                c.draw_text(show_text, rect.x + 12, action_baseline)
                _pill_button_bounds.append(
                    (
                        "show",
                        ui.Rect(rect.x, rect.y, rect.width, rect.height),
                    )
                )
            else:
                _pill_button_bounds.clear()
            paint.color = old_color
        except Exception:
            pass

    def _on_mouse(evt):
        event_type = getattr(evt, "event", "") or ""
        button = getattr(evt, "button", None)
        if event_type not in ("mousedown", "mouse_down") or button not in (0, 1):
            return
        pos = getattr(evt, "pos", None)
        rect = getattr(_pill_canvas, "rect", None)
        if pos is None or rect is None:
            handle_pill_click(PillState.phase)
            return
        abs_x = rect.x + getattr(pos, "x", 0)
        abs_y = rect.y + getattr(pos, "y", 0)
        for action, bounds in list(_pill_button_bounds):
            if (
                bounds.x <= abs_x <= bounds.x + bounds.width
                and bounds.y <= abs_y <= bounds.y + bounds.height
            ):
                handle_pill_click(PillState.phase, action)
                return
        handle_pill_click(PillState.phase)

    try:
        _pill_canvas.register("draw", _on_draw)
        _pill_canvas.register("mouse", _on_mouse)
    except Exception:
        pass
    # Ensure newly created canvases stay hidden until explicitly shown.
    if created:
        try:
            _pill_canvas.hide()
        except Exception:
            pass
    return _pill_canvas


def _show_canvas(
    display_text: str, phase: RequestPhase, rect: Optional[ui.Rect]
) -> None:
    """Create/show the canvas; must be called on the main thread."""
    target_rect = rect or _pill_rect
    c = _ensure_pill_canvas()
    # Ensure the canvas reflects the latest rect when reused.
    _apply_rect(target_rect)
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
        if _pill_canvas is not None:
            apply_canvas_blocking(_pill_canvas)


def show_pill(text: str, phase: RequestPhase) -> None:
    # Surface a simple affordance hint depending on phase.
    if phase in (RequestPhase.SENDING, RequestPhase.STREAMING):
        display_text = text
        PillState.action_mode = "dual"
    elif phase in (RequestPhase.DONE, RequestPhase.ERROR, RequestPhase.CANCELLED):
        display_text = text
        PillState.action_mode = "show"
    else:
        display_text = text
        PillState.action_mode = "none"
    # Avoid redundant UI-thread dispatch if nothing changed.
    if (
        PillState.showing
        and PillState.phase == phase
        and PillState.text == display_text
    ):
        _debug("skip redundant pill show (same phase/text)")
        return
    PillState.text = display_text
    PillState.phase = phase
    PillState.showing = True
    PillState.generation += 1
    current_gen = PillState.generation
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
            # Ignore stale show requests if hide was called meanwhile.
            if PillState.generation != current_gen or not PillState.showing:
                _debug("skipping stale pill show attempt")
                return
            rect = _default_rect()
            _debug(
                f"Show pill: '{display_text}' phase={phase.name} rect=({rect.x}, {rect.y}, {rect.width}, {rect.height})"
            )
            _show_canvas(display_text, phase, rect)
        except Exception as e:
            _debug(f"pill canvas show failed: {e}")

    run_on_ui_thread(_try_show, delay_ms=0)
    run_on_ui_thread(_try_show, delay_ms=50)


def hide_pill() -> None:
    PillState.showing = False
    PillState.generation += 1
    _debug("Hide pill")

    def _hide():
        _release_pill_canvas()

    run_on_ui_thread(_hide)


def handle_pill_click(phase: RequestPhase, action: Optional[str] = None) -> None:
    """Handle a pill click based on the current request phase."""
    try:
        if action == "show" or (
            action is None
            and phase in (RequestPhase.DONE, RequestPhase.ERROR, RequestPhase.CANCELLED)
        ):
            actions.user.model_response_canvas_open()
            _debug(f"Pill click: open response (phase={phase.name})")
        elif action == "cancel" or (
            action is None and phase in (RequestPhase.SENDING, RequestPhase.STREAMING)
        ):
            actions.user.gpt_cancel_request()
            _debug(f"Pill click: cancel (phase={phase.name})")
    except Exception:
        # Swallow to avoid breaking the pill overlay on click.
        pass
    hide_pill()


__all__ = ["show_pill", "hide_pill", "handle_pill_click"]
