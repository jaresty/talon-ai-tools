from typing import Callable, Optional

from talon import Context, Module, actions, canvas, clip, ui

from .modelState import GPTState
from .modelDestination import _parse_meta

mod = Module()
ctx = Context()


class ResponseCanvasState:
    """State specific to the canvas-based response viewer."""

    showing: bool = False
    scroll_y: float = 0.0


_response_canvas: Optional[canvas.Canvas] = None
_response_draw_handlers: list[Callable] = []
_response_button_bounds: dict[str, tuple[int, int, int, int]] = {}
_response_drag_offset: Optional[tuple[float, float]] = None
_response_hover_close: bool = False
_response_mouse_log_count: int = 0


def _debug(msg: str) -> None:
    try:
        print(f"GPT response canvas: {msg}")
    except Exception:
        pass


def _ensure_response_canvas() -> canvas.Canvas:
    """Create the response canvas if needed and register handlers."""
    global _response_canvas
    if _response_canvas is not None:
        _debug("reusing existing response canvas")
        return _response_canvas

    screen = ui.main_screen()
    try:
        screen_x = getattr(screen, "x", 0)
        screen_y = getattr(screen, "y", 0)
        screen_width = getattr(screen, "width", 1600)
        screen_height = getattr(screen, "height", 900)
        margin_x = 40
        margin_y = 40
        panel_width = min(900, max(screen_width - 2 * margin_x, 600))
        panel_height = min(700, max(screen_height - 2 * margin_y, 480))
        start_x = screen_x + max((screen_width - panel_width) // 2, margin_x)
        start_y = screen_y + max((screen_height - panel_height) // 2, margin_y)
        rect = ui.Rect(start_x, start_y, panel_width, panel_height)
        _response_canvas = canvas.Canvas.from_rect(rect)
        try:
            _response_canvas.blocks_mouse = True
        except Exception:
            pass
        _debug(
            f"response canvas rect=({start_x}, {start_y}, {panel_width}, {panel_height}) "
            f"screen=({screen_x}, {screen_y}, {screen_width}, {screen_height})"
        )
    except Exception:
        _response_canvas = canvas.Canvas.from_screen(screen)
        _debug("created response canvas from main_screen fallback")

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        for handler in list(_response_draw_handlers):
            try:
                handler(c)
            except Exception:
                continue

    _response_canvas.register("draw", _on_draw)
    _debug("registered response draw handler")

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        try:
            global _response_drag_offset, _response_hover_close, _response_mouse_log_count
            rect = getattr(_response_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type = getattr(evt, "event", "") or ""
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos

            # Lightweight generic mouse logging (first few events only) to
            # understand the event shapes Talon delivers in this runtime.
            if _response_mouse_log_count < 20:
                try:
                    attrs = sorted(a for a in dir(evt) if not a.startswith("_"))
                    dy_val = getattr(evt, "dy", None)
                    wy_val = getattr(evt, "wheel_y", None)
                    _debug(
                        f"response canvas mouse raw event_type={event_type} button={button} "
                        f"attrs={attrs} dy={dy_val} wheel_y={wy_val}"
                    )
                except Exception:
                    pass
                _response_mouse_log_count += 1

            local_x = pos.x
            local_y = pos.y
            if local_x < 0 or local_y < 0:
                return
            abs_x = rect.x + local_x
            abs_y = rect.y + local_y

            header_height = 32
            hotspot_width = 80

            if event_type in ("mousemove", "mouse_move"):
                _response_hover_close = (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                )

            # Handle close click and drag start.
            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Close hotspot in top-right header.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("response close click detected")
                    ResponseCanvasState.showing = False
                    ResponseCanvasState.scroll_y = 0.0
                    try:
                        _response_canvas.hide()
                    except Exception:
                        pass
                    _response_drag_offset = None
                    return

                # Button hits in footer.
                for key, (bx1, by1, bx2, by2) in list(_response_button_bounds.items()):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    _debug(f"response button clicked: {key}")
                    answer = getattr(GPTState, "last_response", "") or ""
                    try:
                        if key == "paste":
                            actions.user.confirmation_gui_paste()
                            actions.user.model_response_canvas_close()
                        elif key == "copy":
                            actions.user.confirmation_gui_copy()
                            actions.user.model_response_canvas_close()
                        elif key == "discard":
                            actions.user.confirmation_gui_close()
                            actions.user.model_response_canvas_close()
                        elif key == "context":
                            actions.user.confirmation_gui_pass_context()
                            actions.user.model_response_canvas_close()
                        elif key == "query":
                            actions.user.confirmation_gui_pass_query()
                            actions.user.model_response_canvas_close()
                        elif key == "thread":
                            actions.user.confirmation_gui_pass_thread()
                            actions.user.model_response_canvas_close()
                        elif key == "browser":
                            if answer:
                                actions.user.gpt_open_browser(answer)
                            else:
                                actions.user.confirmation_gui_open_browser()
                            actions.user.model_response_canvas_close()
                        elif key == "analyze":
                            actions.user.confirmation_gui_analyze_prompt()
                            actions.user.model_response_canvas_close()
                        elif key == "patterns":
                            actions.user.confirmation_gui_open_pattern_menu_for_prompt()
                            actions.user.model_response_canvas_close()
                        elif key == "quick_help":
                            actions.user.model_help_canvas_open_for_last_recipe()
                    except Exception:
                        pass
                    return

                # Start drag anywhere else.
                _response_drag_offset = (gpos.x - rect.x, gpos.y - rect.y)
                _debug(f"response drag start at offset {_response_drag_offset}")
                return

            if event_type in ("mouseup", "mouse_up"):
                _response_drag_offset = None
                return

            # Scroll with mouse wheel when available.
            if event_type in ("mouse_scroll", "wheel", "scroll"):
                dy = getattr(evt, "dy", 0) or getattr(evt, "wheel_y", 0)
                try:
                    dy = float(dy)
                except Exception:
                    dy = 0.0
                if dy:
                    # Talon's scroll delta sign can vary by platform; treat
                    # positive deltas as scrolling down (content up).
                    ResponseCanvasState.scroll_y = max(
                        ResponseCanvasState.scroll_y - dy * 40.0, 0.0
                    )
                    _debug(
                        f"response canvas mouse scroll dy={dy}, scroll_y={ResponseCanvasState.scroll_y}"
                    )  # pragma: no cover - debug aid
                return

            # Drag while moving.
            if (
                event_type in ("mousemove", "mouse_move")
                and _response_drag_offset is not None
            ):
                dx, dy = _response_drag_offset
                new_x = gpos.x - dx
                new_y = gpos.y - dy
                try:
                    _response_canvas.move(new_x, new_y)
                except Exception:
                    _response_drag_offset = None
        except Exception:
            return

    try:
        _response_canvas.register("mouse", _on_mouse)
        _debug("registered response mouse handler")
    except Exception:
        _debug("response mouse handler registration failed")

    def _on_scroll(evt) -> None:  # pragma: no cover - visual only
        """Handle high-level scroll events when the runtime exposes them."""
        try:
            rect = getattr(_response_canvas, "rect", None)
            if rect is None:
                return
            event_type = getattr(evt, "event", "") or ""
            attrs = sorted(a for a in dir(evt) if not a.startswith("_"))
            dy = getattr(evt, "dy", None)
            delta_y = getattr(evt, "delta_y", None)
            pixels = getattr(evt, "pixels", None)
            degrees = getattr(evt, "degrees", None)
            _debug(
                f"response canvas scroll event_type={event_type} attrs={attrs} "
                f"dy={dy} delta_y={delta_y} pixels={pixels} degrees={degrees}"
            )

            # Prefer pixel deltas when available, then degrees, then dy/delta_y.
            raw = None
            if pixels is not None and hasattr(pixels, "y"):
                raw = getattr(pixels, "y", None)
            elif degrees is not None and hasattr(degrees, "y"):
                raw = getattr(degrees, "y", None)
            elif dy is not None:
                raw = dy
            elif delta_y is not None:
                raw = delta_y
            if raw is None:
                return
            try:
                raw = float(raw)
            except Exception:
                return
            if raw:
                # Treat negative pixel.y (scroll down) as increasing scroll_y.
                ResponseCanvasState.scroll_y = max(
                    ResponseCanvasState.scroll_y - raw, 0.0
                )
                _debug(
                    f"response canvas scroll applied raw={raw}, scroll_y={ResponseCanvasState.scroll_y}"
                )
        except Exception:
            return

    for evt_name in ("scroll", "wheel", "mouse_scroll"):
        try:
            _response_canvas.register(evt_name, _on_scroll)
            _debug(f"registered response scroll handler for '{evt_name}'")
        except Exception:
            _debug(f"response scroll handler registration failed for '{evt_name}'")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = (getattr(evt, "key", "") or "").lower()
            if key in ("escape", "esc"):
                _debug("escape key pressed; closing response canvas")
                ResponseCanvasState.showing = False
                try:
                    _response_canvas.hide()
                except Exception:
                    pass
            elif key in ("pagedown", "page_down"):
                ResponseCanvasState.scroll_y += 200
            elif key in ("pageup", "page_up"):
                ResponseCanvasState.scroll_y = max(ResponseCanvasState.scroll_y - 200, 0)
            elif key in ("down", "j"):
                ResponseCanvasState.scroll_y += 40
            elif key in ("up", "k"):
                ResponseCanvasState.scroll_y = max(ResponseCanvasState.scroll_y - 40, 0)
        except Exception:
            return

    try:
        _response_canvas.register("key", _on_key)
        _debug("registered response key handler")
    except Exception:
        _debug("response key handler registration failed")

    return _response_canvas


def register_response_draw_handler(handler: Callable) -> None:
    _response_draw_handlers.append(handler)


def unregister_response_draw_handler(handler: Callable) -> None:
    try:
        _response_draw_handlers.remove(handler)
    except ValueError:
        pass


def _format_answer_lines(answer: str, max_chars: int) -> list[str]:
    """Normalise answer text into display lines.

    - Collapses multiple blank lines.
    - Applies a simple bullet style for lines starting with '-' or '*'.
    """
    raw_lines = answer.splitlines() or [answer]
    lines: list[str] = []
    last_blank = False
    for raw in raw_lines:
        line = raw.rstrip()
        stripped = line.lstrip()
        if not stripped:
            if not last_blank and lines:
                lines.append("")
            last_blank = True
            continue
        last_blank = False
        # Bullet detection: optional indent + '- ' or '* '.
        if stripped.startswith("- ") or stripped.startswith("* "):
            content = stripped[2:].lstrip()
            bullet_prefix = "  • "
            content = content or ""
            # Wrap bullet content with indentation.
            while content:
                available = max_chars - len(bullet_prefix)
                if available <= 8:
                    # Fallback: avoid infinite loops on tiny widths.
                    lines.append(bullet_prefix + content)
                    content = ""
                    break
                piece = content[:available]
                # Try to break at the last space inside the window.
                break_at = piece.rfind(" ")
                if break_at <= 0:
                    chunk = content[:available]
                    content = content[available:].lstrip()
                else:
                    chunk = content[:break_at]
                    content = content[break_at + 1 :].lstrip()
                lines.append(bullet_prefix + chunk)
                bullet_prefix = "    "  # Subsequent lines align under text.
            continue

        # Non-bullet line wrapping.
        text = line
        while text:
            if len(text) <= max_chars:
                lines.append(text)
                break
            piece = text[:max_chars]
            break_at = piece.rfind(" ")
            if break_at <= 0:
                lines.append(text[:max_chars])
                text = text[max_chars:].lstrip()
            else:
                lines.append(text[:break_at])
                text = text[break_at + 1 :].lstrip()

    return lines or [answer]


def _default_draw_response(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        _debug("response canvas draw skipped (no draw_text)")
        return

    # Fill background.
    paint = getattr(c, "paint", None)
    if rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            paint.color = "FFFFFF"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(rect)
            if old_style is not None:
                paint.style = old_style
            paint.color = old_color or "000000"
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    # Allow users to choose a canvas font (for example, one with good emoji
    # coverage) via a Talon setting rather than hard-coding a platform-
    # specific family here. This is best-effort and ignored when unsupported.
    paint = getattr(c, "paint", None)
    # Prefer a configurable typeface when the runtime exposes one. This uses
    # the same pattern as talon_hud's rich text handling, but allows an
    # optional user override for the font family.
    # Note: we intentionally do not override the canvas font family here.
    # Experiments with skia.Typeface and FontMgr showed that the necessary
    # constructors are not exposed on all Talon runtimes, so per-canvas font
    # changes are not reliable. See ADR 023 work-log for details.

    if rect is not None and hasattr(rect, "x") and hasattr(rect, "y"):
        x = rect.x + 40
        y = rect.y + 60
        body_top = rect.y + 80
        body_bottom = rect.y + rect.height - 60
    else:
        x = 40
        y = 60
        body_top = 80
        body_bottom = 520
    line_h = 18

    # Header with close affordance.
    draw_text("Model response viewer", x, y)
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * 8) - 16
        draw_text(close_label, close_x, close_y)
    y += line_h * 2

    # Optional compact meta interpretation summary above the answer body.
    meta = getattr(GPTState, "last_meta", "").strip()
    if meta:
        try:
            parsed = _parse_meta(meta)
            interpretation = (parsed.get("interpretation") or "").strip()
            if interpretation:
                draw_text("Interpretation:", x, y)
                y += line_h
                for part in interpretation.splitlines()[:2]:
                    draw_text(f"  {part}", x, y)
                    y += line_h
                y += line_h // 2
        except Exception:
            # Meta parsing is best-effort; ignore failures.
            pass

    # Body: scrollable answer text.
    answer = getattr(GPTState, "last_response", "") or ""
    if not answer:
        draw_text("No last response available.", x, y)
        return

    visible_height = body_bottom - body_top
    # Simple line-based scrolling: normalise answer into display lines,
    # including basic bullet formatting, wrapping, and blank-line compression.
    approx_char_width = 8
    max_chars = max(int((rect.width - 80) // approx_char_width), 40) if rect else 80
    lines = _format_answer_lines(answer, max_chars)

    # Compute content height and clamp scroll offset so we cannot scroll past
    # the end of the content.
    content_height = len(lines) * line_h
    max_scroll = max(content_height - visible_height, 0)
    scroll_y = max(min(ResponseCanvasState.scroll_y, max_scroll), 0)
    ResponseCanvasState.scroll_y = scroll_y
    start_index = int(scroll_y // line_h)
    offset_y = body_top - (scroll_y % line_h)

    for idx in range(start_index, len(lines)):
        ly = offset_y + (idx - start_index) * line_h
        if ly > body_bottom:
            break
        draw_text(lines[idx] or " ", x, ly)

    # Draw a simple scrollbar when content exceeds the visible height.
    if content_height > visible_height and rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            # Track along the right edge of the body.
            track_x = rect.x + rect.width - 12
            track_y = body_top
            track_height = visible_height
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.STROKE
            paint.color = "DDDDDD"
            c.draw_rect(ui.Rect(track_x, track_y, 6, track_height))
            # Thumb sized proportionally to visible/content heights.
            thumb_height = max(int(visible_height * visible_height / content_height), 20)
            if max_scroll > 0:
                thumb_offset = int((scroll_y / max_scroll) * (visible_height - thumb_height))
            else:
                thumb_offset = 0
            paint.color = "888888"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(
                ui.Rect(track_x + 1, track_y + thumb_offset + 1, 4, thumb_height - 2)
            )
            # Restore paint state.
            if old_style is not None and hasattr(paint, "Style"):
                paint.style = old_style
            if old_color is not None:
                paint.color = old_color
        except Exception:
            pass

    # Footer buttons.
    _response_button_bounds.clear()
    footer_y = body_bottom + line_h // 2
    btn_labels = [
        ("paste", "[Paste]"),
        ("copy", "[Copy]"),
        ("discard", "[Discard]"),
        ("context", "[Context]"),
        ("query", "[Query]"),
        ("thread", "[Thread]"),
        ("browser", "[Browser]"),
        ("analyze", "[Analyze]"),
        ("patterns", "[Patterns]"),
        ("quick_help", "[Quick help]"),
    ]
    btn_x = x
    approx_char = 8
    for key, label in btn_labels:
        draw_text(label, btn_x, footer_y)
        width = len(label) * approx_char
        _response_button_bounds[key] = (
            btn_x,
            footer_y - line_h,
            btn_x + width,
            footer_y,
        )
        btn_x += width + approx_char * 2


register_response_draw_handler(_default_draw_response)


@mod.action_class
class UserActions:
    def model_response_canvas_open():
        """Toggle the canvas-based response viewer for the last model answer"""
        canvas_obj = _ensure_response_canvas()
        if ResponseCanvasState.showing:
            ResponseCanvasState.showing = False
            ResponseCanvasState.scroll_y = 0.0
            try:
                canvas_obj.hide()
            except Exception:
                pass
            return

        ResponseCanvasState.showing = True
        ResponseCanvasState.scroll_y = 0.0
        _debug("opening response canvas")
        canvas_obj.show()

    def model_response_canvas_close():
        """Explicitly close the response viewer"""
        if _response_canvas is None:
            ResponseCanvasState.showing = False
            return
        ResponseCanvasState.showing = False
        ResponseCanvasState.scroll_y = 0.0
        try:
            _response_canvas.hide()
        except Exception:
            pass
