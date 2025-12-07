from typing import Callable, Optional

from talon import Context, Module, actions, canvas, clip, ui

from .canvasFont import apply_canvas_typeface

from .modelState import GPTState
from .modelDestination import _parse_meta

mod = Module()
ctx = Context()


class ResponseCanvasState:
    """State specific to the canvas-based response viewer."""

    showing: bool = False
    scroll_y: float = 0.0
    meta_expanded: bool = False


_response_canvas: Optional[canvas.Canvas] = None
_response_draw_handlers: list[Callable] = []
_response_button_bounds: dict[str, tuple[int, int, int, int]] = {}
_response_drag_offset: Optional[tuple[float, float]] = None
_response_hover_close: bool = False
_response_hover_button: Optional[str] = None
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
            global _response_drag_offset, _response_hover_close, _response_hover_button, _response_mouse_log_count
            rect = getattr(_response_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type = getattr(evt, "event", "") or ""
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos

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
                hover_key: Optional[str] = None
                for key, (bx1, by1, bx2, by2) in list(_response_button_bounds.items()):
                    if bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2:
                        hover_key = key
                        break
                _response_hover_button = hover_key

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

                # Button hits in header/footer.
                for key, (bx1, by1, bx2, by2) in list(_response_button_bounds.items()):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    _debug(f"response button clicked: {key}")
                    # Use the same selection as the body: prefer the current
                    # confirmation text, then fall back to the last response.
                    answer = (
                        getattr(GPTState, "text_to_confirm", "")
                        or getattr(GPTState, "last_response", "")
                        or ""
                    )
                    try:
                        if key in ("meta_toggle", "meta_toggle_region"):
                            ResponseCanvasState.meta_expanded = (
                                not ResponseCanvasState.meta_expanded
                            )
                            _response_canvas.show()
                        elif key == "paste":
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
            dy = getattr(evt, "dy", None)
            delta_y = getattr(evt, "delta_y", None)
            pixels = getattr(evt, "pixels", None)
            degrees = getattr(evt, "degrees", None)

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
                # If the remaining content fits on this line, keep it intact
                # instead of forcing a wrap that leaves a short trailing
                # fragment (for example, moving a single word like "truth)"
                # onto its own line).
                if len(content) <= available:
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
    # Reset button bounds on each draw so header/footer hit targets stay fresh.
    _response_button_bounds.clear()

    # Fill background and draw a subtle outline so the canvas reads as a
    # coherent panel against the editor/background.
    paint = getattr(c, "paint", None)
    if rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            paint.color = "FFFFFF"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(rect)
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.STROKE
            paint.color = "C0C0C0"
            c.draw_rect(
                ui.Rect(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1)
            )
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
    if paint is not None:
        # Share a common canvas typeface selection helper so all GPT canvases
        # (response viewer, quick help, patterns, suggestions) prefer the same
        # monospaced font chain, while still allowing a Talon setting override.
        apply_canvas_typeface(
            paint,
            settings_key="user.model_response_canvas_typeface",
            debug=_debug,
            cache_key="response",
        )

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

    # Track the default text color so we can temporarily lighten diagnostic
    # sections (like meta) without permanently changing the canvas text color.
    default_text_color = None
    if paint is not None:
        try:
            default_text_color = getattr(paint, "color", None) or "000000"
        except Exception:
            default_text_color = "000000"

    # Header with close affordance.
    draw_text("Model response viewer", x, y)
    close_x = None
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * 8) - 16
        draw_text(close_label, close_x, close_y)
        if paint is not None and _response_hover_close:
            try:
                underline_rect = ui.Rect(
                    close_x, close_y + 4, len(close_label) * 8, 1
                )
                c.draw_rect(underline_rect)
            except Exception:
                pass
    y += line_h

    # Compact prompt recap under the title so users can see which recipe and
    # spoken form produced the current response. Prefer the structured
    # axis fields when available so we keep this recap concise and
    # token-based even if older code paths stored a verbose last_recipe.
    recipe = getattr(GPTState, "last_recipe", "") or ""
    static_prompt = getattr(GPTState, "last_static_prompt", "") or ""
    axis_parts: list[str] = []
    if static_prompt:
        axis_parts.append(static_prompt)
    for attr in ("last_completeness", "last_scope", "last_method", "last_style"):
        value = getattr(GPTState, attr, "") or ""
        if value:
            axis_parts.append(value)
    if axis_parts:
        recipe = " · ".join(axis_parts)
    if recipe:
        draw_text("Talon GPT Result", x, y)
        y += line_h
        draw_text("Prompt recap", x, y)
        y += line_h
        directional = getattr(GPTState, "last_directional", "") or ""
        if directional:
            recipe_text = f"{recipe} · {directional}"
            grammar_phrase = (
                f"model {recipe.replace(' · ', ' ')} {directional}"
            )
        else:
            recipe_text = recipe
            grammar_phrase = f"model {recipe.replace(' · ', ' ')}"
        draw_text(f"Recipe: {recipe_text}", x, y)
        y += line_h
        draw_text(f"Say: {grammar_phrase}", x, y)
        y += line_h

    # Optional diagnostic meta section and toggle under the recap.
    meta = getattr(GPTState, "last_meta", "").strip()
    parsed_meta: Optional[dict] = None
    meta_summary: str = ""
    if meta:
        try:
            parsed_meta = _parse_meta(meta)
        except Exception:
            parsed_meta = None
    if parsed_meta:
        interpretation = (parsed_meta.get("interpretation") or "").strip()
        if interpretation:
            meta_summary = interpretation.splitlines()[0]
    # Fallback: if parsing did not yield an interpretation summary, use the
    # first non-empty raw meta line (after stripping markdown-style headings)
    # so the band always has a short preview.
    if not meta_summary and meta:
        for raw_line in meta.splitlines():
            stripped = raw_line.strip()
            if not stripped:
                continue
            # Strip markdown-style headings.
            if stripped.startswith("#"):
                stripped = stripped.lstrip("#").strip()
            if not stripped:
                continue
            lower = stripped.lower()
            # Skip generic section headers; we want a content-bearing line.
            if lower == "model interpretation" or lower.startswith(
                "model interpretation "
            ):
                continue
            # If we see an Interpretation:/Reading: line, treat the tail as the
            # summary, and strip any leading bullet marker.
            if lower.startswith("interpretation:") or lower.startswith("reading:"):
                tail = stripped.split(":", 1)[1].strip()
                # Drop leading "- " or "* " if present.
                if tail.startswith("- ") or tail.startswith("* "):
                    tail = tail[2:].strip()
                meta_summary = tail or stripped
            # Strip a leading bullet when using a generic content line.
            elif stripped.startswith("- ") or stripped.startswith("* "):
                meta_summary = stripped[2:].strip()
            else:
                meta_summary = stripped
            break

    meta_region_top: Optional[int] = None
    meta_region_bottom: Optional[int] = None

    if meta and rect is not None:
        approx_char_width = 8
        # Compute the toggle first so we know exactly how much horizontal
        # space is available for the meta band text.
        toggle_label = (
            "[Hide meta]"
            if parsed_meta and ResponseCanvasState.meta_expanded
            else "[Show meta]"
        )
        toggle_x = rect.x + rect.width - (len(toggle_label) * approx_char_width) - 24
        toggle_y = y

        # Meta label band, visually distinct from the answer and recap. We draw
        # a subtle background strip and lighten the text color so it reads as
        # secondary to the main response.
        base_label = "Meta (diagnostic)"
        if meta_summary:
            # Available width for the band is everything from x to slightly
            # before the toggle. Use that to truncate the summary so the band
            # never overlaps the toggle or the window edge.
            max_band_pixels = max(
                toggle_x - x - 16, len(base_label) * approx_char_width
            )
            max_band_chars = max(
                int(max_band_pixels // approx_char_width), len(base_label)
            )
            summary_text = meta_summary
            if len(f"{base_label} – {summary_text}") > max_band_chars:
                # Reserve space for an ellipsis when truncating.
                avail = max_band_chars - len(base_label) - 3
                if avail > 0:
                    summary_text = summary_text[:avail].rstrip()
                    if len(meta_summary) > len(summary_text):
                        summary_text += "…"
                else:
                    summary_text = ""
            if summary_text:
                band_text = f"{base_label} – {summary_text}"
            else:
                band_text = base_label
        else:
            band_text = base_label

        # Draw a light background band behind the meta label.
        if paint is not None:
            try:
                old_color = getattr(paint, "color", None)
                old_style = getattr(paint, "style", None)
                if hasattr(paint, "Style") and hasattr(paint, "style"):
                    paint.style = paint.Style.FILL
                paint.color = "F5F5F5"
                band_width = toggle_x - x if toggle_x > x else rect.width - 80
                c.draw_rect(ui.Rect(x - 8, y - line_h + 4, band_width + 16, line_h + 4))
                # Slightly lighter text for meta.
                paint.color = "666666"
            except Exception:
                pass

        draw_text(band_text, x, y)
        draw_text(toggle_label, toggle_x, toggle_y)
        _response_button_bounds["meta_toggle"] = (
            toggle_x,
            toggle_y - line_h,
            toggle_x + len(toggle_label) * approx_char_width,
            toggle_y + line_h,
        )
        if _response_hover_button in ("meta_toggle", "meta_toggle_region"):
            try:
                underline_rect = ui.Rect(
                    toggle_x,
                    toggle_y + 4,
                    len(toggle_label) * approx_char_width,
                    1,
                )
                c.draw_rect(underline_rect)
            except Exception:
                pass

        # Restore default text color after drawing the band/toggle.
        if paint is not None and default_text_color is not None:
            try:
                paint.color = default_text_color
            except Exception:
                pass

        # Record the top of the clickable meta region slightly above the band.
        meta_region_top = y - line_h // 2
        y += line_h

    # Optional expanded meta panel above the answer body when requested. This
    # is explicitly diagnostic and visually treated as an annotation block,
    # not part of the pasteable response.
    if parsed_meta and ResponseCanvasState.meta_expanded:
        # Lighten diagnostic meta text to further separate it from the primary
        # response body.
        if paint is not None:
            try:
                paint.color = "666666"
            except Exception:
                pass
        y += line_h
        detail_x = x + 16
        # Use the same approximate character width as the body, but keep meta
        # text within the visible canvas width so it does not run off-screen.
        meta_max_chars = max(
            int((rect.width - (detail_x - (rect.x if rect else 0)) - 40) // approx_char_width),
            20,
        )

        def _wrap_meta(text: str) -> list[str]:
            lines: list[str] = []
            remaining = text.strip()
            while remaining:
                if len(remaining) <= meta_max_chars:
                    lines.append(remaining)
                    break
                piece = remaining[:meta_max_chars]
                split_at = piece.rfind(" ")
                if split_at <= 0:
                    lines.append(remaining[:meta_max_chars])
                    remaining = remaining[meta_max_chars:].lstrip()
                else:
                    lines.append(remaining[:split_at])
                    remaining = remaining[split_at + 1 :].lstrip()
            return lines or [text]

        interpretation = (parsed_meta.get("interpretation") or "").strip()
        if interpretation:
            for part in interpretation.splitlines():
                for wrapped in _wrap_meta(f"  {part}"):
                    draw_text(wrapped, detail_x, y)
                    y += line_h
            y += line_h // 2
        assumptions = parsed_meta.get("assumptions") or []
        if assumptions:
            for wrapped in _wrap_meta("  Assumptions/constraints:"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            for item in assumptions:
                for wrapped in _wrap_meta(f"    - {item}"):
                    draw_text(wrapped, detail_x, y)
                    y += line_h
            y += line_h // 2
        gaps = parsed_meta.get("gaps") or []
        if gaps:
            for wrapped in _wrap_meta("  Gaps/checks:"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            for item in gaps:
                for wrapped in _wrap_meta(f"    - {item}"):
                    draw_text(wrapped, detail_x, y)
                    y += line_h
            y += line_h // 2
        better = (parsed_meta.get("better_prompt") or "").strip()
        if better:
            for wrapped in _wrap_meta("  Better prompt:"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            for part in better.splitlines():
                for wrapped in _wrap_meta(f"    {part}"):
                    draw_text(wrapped, detail_x, y)
                    y += line_h
            y += line_h // 2
        suggestion = (parsed_meta.get("suggestion") or "").strip()
        if suggestion:
            for wrapped in _wrap_meta("  Axis tweak suggestion:"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            for wrapped in _wrap_meta(f"    {suggestion}"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            y += line_h // 2
        extra = parsed_meta.get("extra") or []
        for item in extra:
            for wrapped in _wrap_meta(f"  {item}"):
                draw_text(wrapped, detail_x, y)
                y += line_h
        # Closing reminder that this section is diagnostic context about how
        # the model read the request, not part of the main answer body.
        for wrapped in _wrap_meta("  Note: meta is diagnostic context only."):
            draw_text(wrapped, detail_x, y)
            y += line_h
        # Restore default text color for the main response body.
        if paint is not None and default_text_color is not None:
            try:
                paint.color = default_text_color
            except Exception:
                pass

        # Extend the clickable meta region to the bottom of the expanded block.
        meta_region_bottom = y

    # If we have any meta at all, allow clicking anywhere in the meta band /
    # block region to toggle expansion, not just on the text toggle control.
    if (
        meta
        and rect is not None
        and meta_region_top is not None
        and meta_region_bottom is None
    ):
        # Meta was present but not expanded; treat just the band as clickable.
        meta_region_bottom = y
    if (
        meta
        and rect is not None
        and meta_region_top is not None
        and meta_region_bottom is not None
    ):
        _response_button_bounds["meta_toggle_region"] = (
            rect.x,
            int(meta_region_top),
            rect.x + rect.width,
            int(meta_region_bottom),
        )

    # Transition into the main, pasteable response body with an explicit
    # heading and additional spacing so it is visually separated from recap
    # and diagnostic meta.
    y += line_h
    draw_text("Response:", x, y)
    y += line_h
    y += line_h // 2
    body_top = max(body_top, y)

    # Body: scrollable answer text. Prefer the current confirmation text when
    # present, falling back to the last model response.
    answer = (
        getattr(GPTState, "text_to_confirm", "") or getattr(GPTState, "last_response", "")
    )
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

    # Footer buttons. We intentionally do not clear _response_button_bounds
    # here so that the header meta toggle bounds remain registered; the
    # bounds map was cleared at the start of this draw.
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
    max_footer_x = (rect.x + rect.width - 40) if rect is not None else 10000
    for key, label in btn_labels:
        width = len(label) * approx_char
        # Wrap to a new footer line if the next button would exceed the
        # visible canvas width.
        if btn_x + width > max_footer_x:
            footer_y += line_h * 2
            btn_x = x
        label_x = btn_x
        draw_text(label, label_x, footer_y)
        _response_button_bounds[key] = (
            label_x,
            footer_y - line_h,
            label_x + width,
            footer_y,
        )
        if (
            _response_hover_button == key
            and rect is not None
            and paint is not None
        ):
            try:
                underline_rect = ui.Rect(label_x, footer_y + 4, width, 1)
                c.draw_rect(underline_rect)
            except Exception:
                pass
        btn_x += width + approx_char * 2
        # Add extra spacing between logical button groups to improve visual
        # scanability (output actions | context/thread | analysis/browser).
        if key in ("discard", "thread"):
            btn_x += approx_char * 4


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
        # Always start with meta collapsed; the band still shows a short
        # summary so the initial view is response-first.
        ResponseCanvasState.meta_expanded = False
        _debug("opening response canvas")
        canvas_obj.show()

    def model_response_canvas_close():
        """Explicitly close the response viewer"""
        if _response_canvas is None:
            ResponseCanvasState.showing = False
            return
        ResponseCanvasState.showing = False
        ResponseCanvasState.scroll_y = 0.0
        ResponseCanvasState.meta_expanded = False
        try:
            _response_canvas.hide()
        except Exception:
            pass
