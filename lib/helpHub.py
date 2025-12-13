from dataclasses import dataclass
import os
import time
from typing import Callable, Dict, List, Optional
from collections.abc import Sequence

from talon import Context, Module, actions, app, canvas, clip, ui, tap
from talon import skia

from .axisCatalog import axis_catalog

from .canvasFont import apply_canvas_typeface
from .helpUI import apply_scroll_delta, clamp_scroll, scroll_fraction
from .modelState import GPTState
from .suggestionCoordinator import last_recipe_snapshot, suggestion_grammar_phrase
from .helpDomain import (
    help_index,
    help_search,
    help_focusable_items,
    help_next_focus_label,
    help_activation_target,
    help_edit_filter_text,
    HelpIndexEntry,
)
from .requestBus import current_state
from .requestState import RequestPhase
from .modelHelpers import notify


try:
    from .modelPatternGUI import PATTERNS
    from .modelPromptPatternGUI import PROMPT_PRESETS
except ImportError:  # During bootstrap/test fallback to empty lists
    PATTERNS = []
    PROMPT_PRESETS = []


mod = Module()
ctx = Context()


@dataclass
class HubButton:
    label: str
    description: str
    handler: Callable[[], None]
    voice_hint: str = ""


class HelpHubState:
    showing: bool = False
    filter_text: str = ""
    show_onboarding: bool = False
    drag_offset: Optional[tuple[float, float]] = None
    scroll_y: float = 0.0
    hover_label: str = ""
    max_scroll: float = 0.0


_hub_canvas: Optional[canvas.Canvas] = None
_button_bounds: Dict[str, skia.Rect] = {}
_search_bounds: Dict[str, skia.Rect] = {}
_scroll_bounds: Dict[str, skia.Rect] = {}
_buttons: List[HubButton] = []
_search_index: List[HubButton] = []
_search_results: List[HubButton] = []
_last_layout_signature: Optional[tuple[float, float, float]] = None
_layout_log_count = 0
_scroll_log_count = 0
_modifier_state = {"alt": False, "cmd": False}
_last_alt_down = 0.0
_last_cmd_down = 0.0
_last_alt_nav_down = 0.0
_global_key_handler_registered = False
_tap_key_handler_registered = False
_hub_key_handler = None  # set after canvas creation
_handlers_registered = False


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""
    try:
        phase = getattr(current_state(), "phase", RequestPhase.IDLE)
        return phase not in (
            RequestPhase.IDLE,
            RequestPhase.DONE,
            RequestPhase.ERROR,
            RequestPhase.CANCELLED,
        )
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""
    if _request_is_in_flight():
        notify(
            "GPT: A request is already running; wait for it to finish or cancel it first."
        )
        return True
    return False

# Basic layout constants for a compact panel.
_PANEL_WIDTH = 520
_PANEL_HEIGHT = 560
_PADDING_X = 18
_PADDING_Y = 18
_BUTTON_HEIGHT = 64
_BUTTON_SPACING = 10
_SEARCH_ITEM_HEIGHT = 32
_SCROLL_GUTTER = 20
_panel_height_px = _PANEL_HEIGHT


def _rgba(r: int, g: int, b: int, a: int = 255) -> int:
    return (r << 24) | (g << 16) | (b << 8) | a


_BACKGROUND_COLOR = _rgba(30, 30, 30, 255)
_BORDER_COLOR = _rgba(74, 74, 74, 255)
_BUTTON_COLOR = _rgba(46, 46, 46, 255)
_BUTTON_HOVER_COLOR = _rgba(58, 58, 58, 255)
_RESULT_COLOR = _rgba(37, 37, 37, 255)
_RESULT_HOVER_COLOR = _rgba(70, 70, 70, 255)


def _rect_contains(rect: skia.Rect, x: float, y: float) -> bool:
    """Manual containment check to avoid backend differences."""
    try:
        rx, ry, rw, rh = rect.x, rect.y, rect.width, rect.height
    except Exception:
        return False
    return rx <= x <= rx + rw and ry <= y <= ry + rh


def _log(msg: str) -> None:
    try:
        print(f"HelpHub: {msg}")
    except Exception:
        pass


def _block_key_event(evt) -> None:
    """Best-effort key blocking to stop fallthrough into other apps."""

    for name in ("block", "stop", "consume"):
        fn = getattr(evt, name, None)
        if callable(fn):
            try:
                fn()
            except Exception:
                continue
            else:
                return
    # As a last resort, set a handled flag if present.
    try:
        if hasattr(evt, "handled"):
            evt.handled = True  # type: ignore[attr-defined]
    except Exception:
        pass


def _close_overlapping_surfaces() -> None:
    """Close other overlays to avoid stacking UIs."""
    for closer in (
        getattr(actions.user, "model_help_canvas_close", None),
        getattr(actions.user, "model_pattern_gui_close", None),
        getattr(actions.user, "prompt_pattern_gui_close", None),
        getattr(actions.user, "model_prompt_recipe_suggestions_gui_close", None),
    ):
        try:
            if closer:
                closer()
        except Exception:
            continue


def _ensure_canvas() -> None:
    global _hub_canvas, _panel_height_px
    if _hub_canvas is not None:
        return
    target_rect = None
    try:
        screen = ui.main_screen()
        rect = getattr(ui, "Rect", None)
        if rect is not None and screen is not None:
            cx = getattr(screen, "width", 1200) or 1200
            cy = getattr(screen, "height", 800) or 800
            # Prefer a taller panel to reduce scrolling; clamp to screen.
            _panel_height_px = max(700, min(cy - 80, cy - 40))
            x = max((cx - _PANEL_WIDTH) / 2, 20)
            y = max((cy - _panel_height_px) / 3, 20)
            target_rect = rect(x, y, _PANEL_WIDTH, _panel_height_px)
            # Use block_mouse to ensure the canvas can capture keyboard focus and clicks.
            _hub_canvas = canvas.Canvas.from_rect(target_rect, block_mouse=True)
        else:
            _panel_height_px = _PANEL_HEIGHT
            target_rect = ui.Rect(100, 100, _PANEL_WIDTH, _panel_height_px)
            _hub_canvas = canvas.Canvas.from_rect(target_rect)
    except Exception as e:
        _hub_canvas = None
        _log(f"_ensure_canvas failed: {e}")
        return

    if _hub_canvas is None:
        return
    try:
        _hub_canvas.blocks_mouse = True  # type: ignore[attr-defined]
    except Exception as e:
        _log(f"failed to set blocks_mouse: {e}")
    # Try to block keyboard input from reaching the foreground app while the hub is open.
    for attr in ("blocks_keyboard", "block_keyboard"):
        try:
            setattr(_hub_canvas, attr, True)  # type: ignore[attr-defined]
        except Exception as e:
            _log(f"failed to set {attr}: {e}")
    try:
        _hub_canvas.block_mouse = True  # type: ignore[attr-defined]
    except Exception as e:
        _log(f"failed to set block_mouse: {e}")
    _log(
        "canvas created; size="
        f"{_PANEL_WIDTH}x{_panel_height_px}; rect={getattr(_hub_canvas, 'rect', None)}"
    )
    try:
        if target_rect is not None:
            _hub_canvas.rect = target_rect  # type: ignore[attr-defined]
    except Exception:
        pass

    def _draw(c: canvas.Canvas):  # pragma: no cover - visual
        if not hasattr(c, "draw_rect") or not hasattr(c, "draw_text"):
            return
        try:
            # Clear background to opaque dark gray with a simple border.
            paint = skia.Paint()
            paint.color = _BACKGROUND_COLOR
            c.draw_rect(
                skia.Rect(c.rect.x, c.rect.y, _PANEL_WIDTH, _panel_height_px),
                paint,
            )
            border = skia.Paint()
            border.color = _BORDER_COLOR
            c.draw_rect(
                skia.Rect(
                    c.rect.x + 1, c.rect.y + 1, _PANEL_WIDTH - 2, _panel_height_px - 2
                ),
                border,
            )

            text_paint = skia.Paint()
            text_paint.color = _rgba(255, 255, 255, 255)
            apply_canvas_typeface(text_paint)

            content_top = c.rect.y + _PADDING_Y
            y = content_top - HelpHubState.scroll_y  # draw position
            x = c.rect.x + _PADDING_X
            title = "Model Help Hub"
            c.draw_text(title, x, y + 18, text_paint)
            # Reset bounds each draw.
            _button_bounds.clear()
            _search_bounds.clear()
            _scroll_bounds.clear()
            # Close affordance (clickable "×" in the top-right).
            close_rect = skia.Rect(
                c.rect.x + _PANEL_WIDTH - _PADDING_X - 24,
                y + 2,
                22,
                22,
            )
            _button_bounds["__close__"] = close_rect
            close_bg = skia.Paint()
            is_close_hover = HelpHubState.hover_label == "__close__"
            close_bg.color = (
                _rgba(200, 64, 64, 255) if is_close_hover else _BUTTON_COLOR
            )
            c.draw_rect(close_rect, close_bg)
            # Draw glyph with slight brightness bump on hover.
            glyph_paint = skia.Paint()
            glyph_paint.color = (
                _rgba(255, 255, 255, 255)
                if is_close_hover
                else _rgba(220, 220, 220, 255)
            )
            apply_canvas_typeface(glyph_paint)
            c.draw_text("×", close_rect.x + 7, close_rect.y + 16, glyph_paint)

            filter_query = HelpHubState.filter_text.strip()

            content_width = _PANEL_WIDTH - 2 * _PADDING_X - _SCROLL_GUTTER

            def _draw_result_row(
                res: HubButton, start_x: float, start_y: float
            ) -> float:
                """Draw a filtered result row; return the total height consumed."""
                label = res.label if len(res.label) <= 70 else res.label[:70] + "..."
                rect_height = _SEARCH_ITEM_HEIGHT
                hint = res.voice_hint.strip()
                desc = res.description.strip()
                has_hint = bool(hint)
                has_desc = bool(desc)
                if has_hint or has_desc:
                    rect_height += 16
                rect = skia.Rect(start_x, start_y, content_width, rect_height)
                _search_bounds[res.label] = rect
                is_hover = HelpHubState.hover_label == f"res:{res.label}"
                res_bg = skia.Paint()
                res_bg.color = _RESULT_HOVER_COLOR if is_hover else _RESULT_COLOR
                c.draw_rect(rect, res_bg)
                label_paint = skia.Paint()
                label_paint.color = text_paint.color
                apply_canvas_typeface(label_paint)
                if is_hover:
                    label_paint.color = _rgba(255, 255, 255, 255)
                c.draw_text(label, rect.x + 10, rect.y + 18, label_paint)
                detail_y = rect.y + 34
                detail_line = ""
                if has_hint:
                    detail_line = hint
                elif has_desc:
                    detail_line = desc
                if detail_line:
                    # Avoid copying a Paint via constructor (can raise in some runtimes).
                    detail_paint = skia.Paint()
                    detail_paint.color = label_paint.color
                    apply_canvas_typeface(detail_paint)
                    for wrapped in _wrap_text(
                        detail_line, content_width - 20, approx_char_px=7
                    ):
                        c.draw_text(wrapped, rect.x + 10, detail_y, detail_paint)
                        detail_y += 16
                return rect.height + 6

            if filter_query:
                # Filtered mode: focus on search results only.
                c.draw_text(f"Filter: {filter_query}", x, y + 40, text_paint)
                list_y = y + 60
                for res in _search_results:
                    list_y += _draw_result_row(res, x, list_y)
                if filter_query and not _search_results:
                    c.draw_text("No results", x, list_y + 16, text_paint)
                content_bottom = list_y + 10
            else:
                btn_y = y + 36
                # Render grouped buttons (main nav first, then util).
                groups = [
                    ("Navigation", _buttons[:5]),
                    ("Docs & Copy", _buttons[5:]),
                ]
                for group_name, group_items in groups:
                    c.draw_text(group_name, x, btn_y + 14, text_paint)
                    btn_y += 22
                    for btn in group_items:
                        rect = skia.Rect(
                            x,
                            btn_y,
                            content_width,
                            _BUTTON_HEIGHT,
                        )
                        _button_bounds[btn.label] = rect

                        # Button background
                        bg = skia.Paint()
                        bg.color = _BUTTON_COLOR
                        if HelpHubState.hover_label == f"btn:{btn.label}":
                            bg.color = _BUTTON_HOVER_COLOR
                        c.draw_rect(rect, bg)

                        # Label + wrapped description.
                        label_paint = skia.Paint()
                        label_paint.color = text_paint.color
                        apply_canvas_typeface(label_paint)
                        if HelpHubState.hover_label == f"btn:{btn.label}":
                            label_paint.color = _rgba(255, 255, 255, 255)
                        c.draw_text(btn.label, rect.x + 10, rect.y + 20, label_paint)
                        desc_lines: List[str] = []
                        desc = (btn.description or "").strip()
                        hint = (btn.voice_hint or "").strip()
                        max_desc_width = content_width - 20
                        if desc:
                            desc_lines.extend(
                                _wrap_text(desc, max_desc_width, approx_char_px=7)[:2]
                            )
                        if hint:
                            desc_lines.extend(
                                _wrap_text(hint, max_desc_width, approx_char_px=7)[:2]
                            )
                        for idx, line in enumerate(desc_lines[:3]):
                            c.draw_text(
                                line, rect.x + 10, rect.y + 38 + idx * 16, label_paint
                            )

                        btn_y += _BUTTON_HEIGHT + _BUTTON_SPACING
                btn_y += 6

                # Last recipe recap.
                snapshot = last_recipe_snapshot()
                recipe_text = snapshot.get("recipe", "") or ""
                directional = snapshot.get("directional", "") or ""
                if recipe_text:
                    if directional:
                        recipe_line = f"Last recipe: {recipe_text} · {directional}"
                    else:
                        recipe_line = f"Last recipe: {recipe_text}"
                    c.draw_text(recipe_line, x, btn_y + 16, text_paint)
                    btn_y += 34

                # Render search/filter input and results.
                filter_label = f"Filter: {HelpHubState.filter_text or '(empty)'}"
                caret = " ▍" if HelpHubState.showing else ""
                c.draw_text(filter_label + caret, x, btn_y + 4, text_paint)
                result_y = btn_y + 24
                for res in _search_results[:8]:
                    result_y += _draw_result_row(res, x, result_y)
                if HelpHubState.filter_text and not _search_results:
                    c.draw_text("No results", x, result_y + 16, text_paint)

                # Normalisation and voice hints.
                info_y = result_y + 10
                info_lines = [
                    "Caps: scope≤2, method≤3, form=1, channel=1; include a directional lens.",
                    "Voice hints: model patterns · model quick help · model run suggest · history drawer.",
                    "Hub: wheel/PgUp/PgDn/arrow keys or scrollbar to scroll; say 'model help filter <phrase>'.",
                ]
                for line in info_lines:
                    for wrapped in _wrap_text(line, content_width, approx_char_px=7):
                        c.draw_text(wrapped, x, info_y, text_paint)
                        info_y += 18

                if HelpHubState.show_onboarding:
                    onboarding_lines = [
                        "Onboarding:",
                        "1) Open Patterns and run one recipe.",
                        "2) Open Quick help and say model show grammar.",
                        "3) Try 'model run again gist fog' after a run.",
                    ]
                    info_y += 8
                    for line in onboarding_lines:
                        for wrapped in _wrap_text(
                            line, content_width, approx_char_px=7
                        ):
                            c.draw_text(wrapped, x, info_y, text_paint)
                            info_y += 18

                content_bottom = info_y + 10

            # Adjust content_bottom back to unscrolled coordinates for height math.
            content_bottom += HelpHubState.scroll_y
            # Update max scroll based on content height, then clamp scroll.
            visible_height = _panel_height_px - 2 * _PADDING_Y
            content_height = content_bottom - content_top
            HelpHubState.max_scroll = max(0.0, content_height - visible_height)
            _clamp_scroll()
            # Draw a simple scrollbar track/thumb in a reserved gutter, plus
            # explicit step buttons for setups where wheel events do not fire.
            if HelpHubState.max_scroll > 0:
                track_x = c.rect.x + _PANEL_WIDTH - _PADDING_X - (_SCROLL_GUTTER // 2)
                track_y = content_top + 64  # leave space for title/close affordance
                track_width = 6
                track_height = max(visible_height - 120, 60)
                track = skia.Paint()
                track.color = _BORDER_COLOR
                track_rect = skia.Rect(track_x, track_y, track_width, track_height)
                _scroll_bounds["track"] = track_rect
                c.draw_rect(track_rect, track)
                thumb_height = max(
                    int(
                        track_height
                        * visible_height
                        / (content_bottom - (c.rect.y + _PADDING_Y))
                    ),
                    18,
                )
                thumb_offset = 0
                if HelpHubState.max_scroll > 0:
                    thumb_offset = int(
                        scroll_fraction(HelpHubState.scroll_y, HelpHubState.max_scroll)
                        * max(track_height - thumb_height, 0)
                    )
                thumb_rect = skia.Rect(
                    track_x, track_y + thumb_offset, track_width, thumb_height
                )
                _scroll_bounds["thumb"] = thumb_rect
                thumb = skia.Paint()
                thumb.color = _BUTTON_HOVER_COLOR
                c.draw_rect(thumb_rect, thumb)
                # Step buttons
                up_rect = skia.Rect(track_x - 8, track_y - 18, track_width + 16, 14)
                dn_rect = skia.Rect(
                    track_x - 8, track_y + track_height + 4, track_width + 16, 14
                )
                _scroll_bounds["step_up"] = up_rect
                _scroll_bounds["step_down"] = dn_rect
                c.draw_text("▲", up_rect.x + 4, up_rect.y + 12, text_paint)
                c.draw_text("▼", dn_rect.x + 4, dn_rect.y + 12, text_paint)
            # Cut down logging noise: only emit when layout changes or early draws.
            global _last_layout_signature, _layout_log_count
            sig = (
                round(float(content_bottom), 1),
                round(float(visible_height), 1),
                round(float(HelpHubState.max_scroll), 1),
            )
            if sig != _last_layout_signature or _layout_log_count < 5:
                _log(
                    f"layout done: content_bottom={content_bottom}, "
                    f"visible_height={visible_height}, max_scroll={HelpHubState.max_scroll}"
                )
                _last_layout_signature = sig
                _layout_log_count += 1
        except Exception:
            # Fallback draw if anything above fails.
            import traceback

            try:
                _log(f"render exception: {traceback.format_exc()}")
            except Exception:
                pass
            err_paint = skia.Paint()
            err_paint.color = 0xFF000000
            c.draw_rect(
                skia.Rect(c.rect.x, c.rect.y, _PANEL_WIDTH, _panel_height_px),
                err_paint,
            )
            txt = skia.Paint()
            txt.color = 0xFFFFFFFF
            c.draw_text("Help Hub render error", c.rect.x + 10, c.rect.y + 24, txt)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual
        try:
            event_type = getattr(evt, "event", "") or ""
            # Keep early logging limited.
            if event_type and _scroll_log_count < 4:
                _log(f"mouse event type={event_type}")
                globals()["_scroll_log_count"] = _scroll_log_count + 1
            pos = getattr(evt, "gpos", None) or getattr(evt, "pos", None)
            if pos is None:
                return
            gx = getattr(pos, "x", None)
            gy = getattr(pos, "y", None)
            if gx is None or gy is None:
                return
            # Hover state (always set on move/down).
            HelpHubState.hover_label = ""
            close_rect = _button_bounds.get("__close__")
            if close_rect and _rect_contains(close_rect, gx, gy):
                HelpHubState.hover_label = "__close__"
            else:
                for btn in _buttons:
                    rect = _button_bounds.get(btn.label)
                    if rect and _rect_contains(rect, gx, gy):
                        HelpHubState.hover_label = f"btn:{btn.label}"
                        break
                if not HelpHubState.hover_label:
                    for res in _search_results:
                        rect = _search_bounds.get(res.label)
                        if rect and _rect_contains(rect, gx, gy):
                            HelpHubState.hover_label = f"res:{res.label}"
                            break
            if event_type not in ("mousedown", "mouse_down"):
                # Drag / move support.
                if (
                    event_type in ("mousemove", "mouse_move")
                    and HelpHubState.drag_offset
                ):
                    try:
                        _hub_canvas.move(
                            gx - HelpHubState.drag_offset[0],
                            gy - HelpHubState.drag_offset[1],
                        )
                    except Exception:
                        HelpHubState.drag_offset = None
                if event_type in ("mouseup", "mouse_up"):
                    HelpHubState.drag_offset = None
                if event_type in ("mouse_scroll", "wheel", "scroll"):
                    _handle_scroll_delta(evt)
                return
            if getattr(evt, "button", 0) not in (0, 1):
                return
            _log(
                f"mousedown type={event_type} at ({gx},{gy}); bounds keys={list(_button_bounds.keys())}"
            )
            # Scrollbar clicks: clicking track jumps proportionally; thumb behaves the same.
            for zone_name, rect in _scroll_bounds.items():
                if (
                    rect
                    and rect.x <= gx <= rect.x + rect.width
                    and rect.y <= gy <= rect.y + rect.height
                ):
                    if zone_name in ("track", "thumb") and HelpHubState.max_scroll > 0:
                        frac = max(
                            0.0,
                            min((gy - rect.y) / max(rect.height - 1, 1), 1.0),
                        )
                        HelpHubState.scroll_y = clamp_scroll(
                            frac * HelpHubState.max_scroll, HelpHubState.max_scroll
                        )
                    elif zone_name == "step_up":
                        HelpHubState.scroll_y = apply_scroll_delta(
                            HelpHubState.scroll_y, -120.0, HelpHubState.max_scroll
                        )
                    elif zone_name == "step_down":
                        HelpHubState.scroll_y = apply_scroll_delta(
                            HelpHubState.scroll_y, 120.0, HelpHubState.max_scroll
                        )
                    _clamp_scroll()
                    try:
                        _hub_canvas.show()
                    except Exception:
                        pass
                    return
            # Close hit target.
            if _handle_click(gx, gy):
                return

            # Start drag anywhere in panel.
            try:
                if _hub_canvas is not None:
                    rect = _hub_canvas.rect
                    if (
                        rect.x <= gx <= rect.x + rect.width
                        and rect.y <= gy <= rect.y + rect.height
                    ):
                        HelpHubState.drag_offset = (gx - rect.x, gy - rect.y)
            except Exception:
                pass
            for btn in _buttons:
                rect = _button_bounds.get(btn.label)
                if rect and _rect_contains(rect, gx, gy):
                    HelpHubState.hover_label = f"btn:{btn.label}"
                    target = help_activation_target(
                        HelpHubState.hover_label, _buttons, _search_results
                    )
                    if target is None:
                        return
                    try:
                        handler = getattr(target, "handler", None)
                        if callable(handler):
                            handler()
                    except Exception:
                        pass
                    return
            for res in _search_results:
                rect = _search_bounds.get(res.label)
                if rect and _rect_contains(rect, gx, gy):
                    HelpHubState.hover_label = f"res:{res.label}"
                    target = help_activation_target(
                        HelpHubState.hover_label, _buttons, _search_results
                    )
                    if target is None:
                        return
                    try:
                        handler = getattr(target, "handler", None)
                        if callable(handler):
                            handler()
                    except Exception:
                        pass
                    return
        except Exception:
            return

    # Register handlers once per canvas lifetime.
    if not globals().get("_handlers_registered", False):
        try:
            _hub_canvas.register("draw", _draw)
            _log("hub draw handler registered")
        except Exception as e:
            _log(f"hub draw register failed: {e}")
        for evt_name in ("mouse", "mouse_move", "mouse_drag"):
            try:
                _hub_canvas.register(evt_name, _on_mouse)
                _log(f"hub mouse handler registered for {evt_name}")
            except Exception as e:
                _log(f"hub mouse register failed for {evt_name}: {e}")
        for evt_name in ("scroll", "wheel", "mouse_scroll"):
            try:
                _hub_canvas.register(evt_name, _on_scroll)
                _log(f"hub scroll handler registered for {evt_name}")
            except Exception as e:
                _log(f"hub scroll register failed for {evt_name}: {e}")
        globals()["_handlers_registered"] = True


def _on_scroll(evt) -> None:  # pragma: no cover - visual
    _handle_scroll_delta(evt)


def _on_key(evt) -> None:  # pragma: no cover - visual
    """Global key handler for Help Hub."""
    try:
        if not getattr(HelpHubState, "showing", False):
            return None
        raw_key = getattr(evt, "key", "") or ""
        key = raw_key.lower()
        # Normalise common aliases from tap/ui events.
        if key in ("bksp", "backspace"):
            key = "backspace"
        # Some runtimes send delete as "del" or the raw delete char ("\x7f").
        if key in ("del", "\x7f"):
            key = "delete"
        if not getattr(evt, "down", False):
            if key in ("alt", "lalt", "ralt"):
                _modifier_state["alt"] = False
            if key in ("cmd", "lcmd", "rcmd", "meta", "super"):
                _modifier_state["cmd"] = False
            _block_key_event(evt)
            return True
        # Track modifiers explicitly; Talon may send them as separate keys.
        if key in ("alt", "lalt", "ralt"):
            _modifier_state["alt"] = True
            globals()["_last_alt_down"] = time.time()
            _block_key_event(evt)
            return True
        if key in ("cmd", "lcmd", "rcmd", "meta", "super"):
            _modifier_state["cmd"] = True
            globals()["_last_cmd_down"] = time.time()
            _block_key_event(evt)
            return True
        mods = []
        raw_mods = getattr(evt, "mods", None) or []
        _log(
            f"hub key: raw_key={raw_key!r} key={key!r} down={getattr(evt, 'down', False)} mods={raw_mods}"
        )
        # Track an Alt+Left/Right navigation pattern so we can treat a
        # subsequent bare delete as an Alt+Delete semantic (word delete).
        if key in ("left", "right", "arrowleft", "arrowright") and any(
            str(m).lower() in ("alt", "option", "opt") for m in raw_mods
        ):
            globals()["_last_alt_nav_down"] = time.time()
        for mod_name in (
            "alt",
            "cmd",
            "ctrl",
            "shift",
            "meta",
            "super",
            "option",
            "opt",
            "command",
        ):
            if getattr(evt, mod_name, False):
                mods.append(mod_name)
        for side_mod in ("lalt", "ralt", "lcmd", "rcmd", "lctrl", "rctrl"):
            if getattr(evt, side_mod, False) and side_mod not in mods:
                mods.append(side_mod)
        for m in raw_mods:
            lm = str(m).lower()
            if lm not in mods:
                mods.append(lm)
        alt_down = (
            _modifier_state.get("alt", False)
            or getattr(evt, "alt", False)
            or getattr(evt, "lalt", False)
            or getattr(evt, "ralt", False)
            or any(m in ("alt", "option", "opt") for m in mods)
        )
        cmd_down = (
            _modifier_state.get("cmd", False)
            or getattr(evt, "cmd", False)
            or getattr(evt, "lcmd", False)
            or getattr(evt, "rcmd", False)
            or getattr(evt, "meta", False)
            or getattr(evt, "super", False)
            or any(m in ("cmd", "command", "meta", "super") for m in mods)
        )
        now = time.time()
        shift_down = (
            "shift" in mods
            or getattr(evt, "shift", False)
            or getattr(evt, "lshift", False)
        )
        if key in ("escape", "esc"):
            help_hub_close()
            _block_key_event(evt)
            return True
        if key in ("tab",) or key in ("down", "arrowdown"):
            _focus_step(-1 if shift_down and key == "tab" else 1)
            _block_key_event(evt)
            return True
        if key in ("up", "arrowup"):
            _focus_step(-1)
            _block_key_event(evt)
            return True
        if key in ("enter", "return"):
            if _activate_focus():
                _block_key_event(evt)
                return True
        if key in ("backspace", "back") and not alt_down and not cmd_down:
            HelpHubState.filter_text = help_edit_filter_text(
                HelpHubState.filter_text, key, alt=False, cmd=False
            )
            _recompute_search_results()
            _block_key_event(evt)
            return True
        # Treat recent alt/cmd down as active even if the modifier isn't reported on the delete key.
        alt_active = (
            alt_down
            or (now - globals().get("_last_alt_down", 0.0) < 0.4)
            or (now - globals().get("_last_alt_nav_down", 0.0) < 0.4)
        )
        cmd_active = cmd_down or (now - globals().get("_last_cmd_down", 0.0) < 0.4)
        if key in ("delete", "backspace") and alt_active:
            HelpHubState.filter_text = help_edit_filter_text(
                HelpHubState.filter_text, key, alt=True, cmd=False
            )
            _recompute_search_results()
            _block_key_event(evt)
            return True
        if key in ("delete", "backspace") and cmd_active:
            HelpHubState.filter_text = help_edit_filter_text(
                HelpHubState.filter_text, key, alt=False, cmd=True
            )
            _recompute_search_results()
            _block_key_event(evt)
            return True
        if key in ("pagedown", "page_down"):
            HelpHubState.scroll_y = apply_scroll_delta(
                HelpHubState.scroll_y, 200.0, HelpHubState.max_scroll
            )
            _clamp_scroll()
            try:
                if _hub_canvas is not None:
                    _hub_canvas.show()
            except Exception:
                pass
            _block_key_event(evt)
            return True
        if key in ("pageup", "page_up"):
            HelpHubState.scroll_y = apply_scroll_delta(
                HelpHubState.scroll_y, -200.0, HelpHubState.max_scroll
            )
            _clamp_scroll()
            try:
                if _hub_canvas is not None:
                    _hub_canvas.show()
            except Exception:
                pass
            _block_key_event(evt)
            return True
        if len(key) == 1 and 32 <= ord(key) <= 126:
            HelpHubState.filter_text = help_edit_filter_text(
                HelpHubState.filter_text, key, alt=False, cmd=False
            )
            _recompute_search_results()
            _block_key_event(evt)
            return True
        # Swallow all other keys while hub is visible to avoid fallthrough.
        _block_key_event(evt)
        return True
    except Exception as e:
        _log(f"hub key handler exception: {e}")
        _block_key_event(evt)
        return True


_hub_key_handler = _on_key


def _cheat_sheet_text() -> str:
    lines = [
        "Model Help Hub cheat sheet",
        "Core commands:",
        "- model help hub",
        "- model quick help / model show grammar",
        "- model patterns / model pattern menu <prompt>",
        "- model run suggest / model run suggestions",
        "- model history list / history drawer",
        "- model provider list / provider use <name> / provider status",
        "- model help (HTML docs)",
        "Who / Why / How (ADR 040):",
        "- Persona (Who): voice, audience, tone",
        "- Intent (Why): purpose",
        "- Contract (How): completeness, scope, method, form, channel",
        "- Presets: small Who/Why bundles (for example, 'Teach junior dev', 'Executive brief').",
        "Axes (examples):",
        "- completeness: skim | gist | full | deep",
        "- scope: narrow | focus | bound | edges",
        "- method: steps | plan | rigor | flow | debugging",
        "- form: plain | bullets | table | code | checklist | adr",
        "- channel: slack | jira | presenterm | html | announce",
        "Hints:",
        "- Form and channel are optional singletons; defaults/last-run apply when omitted; legacy style tokens are removed (use form/channel).",
        "- Every run needs exactly one directional lens (fog/fig/dig/ong/rog/bog/jog).",
        "Persona presets: peer | coach | mentor | stakeholder | design | pm | exec",
        "Intent presets: teach | decide | plan | evaluate | brainstorm | appreciate | persuade | coach | collaborate | entertain",
        "- Use More actions… → Open Help Hub in confirmation",
        "- Say 'model help filter <phrase>' to search in Hub",
    ]
    return "\n".join(lines)


def _wrap_text(text: str, max_width_px: int, approx_char_px: int = 8) -> List[str]:
    """Very small word-wrap helper for canvas text."""
    if max_width_px <= 0:
        return [text]
    max_chars = max(int(max_width_px // max(approx_char_px, 4)), 8)
    words = text.split()
    lines: List[str] = []
    current: List[str] = []
    for w in words:
        if len(" ".join(current + [w])) > max_chars:
            if current:
                lines.append(" ".join(current))
                current = [w]
            else:
                lines.append(w)
                current = []
        else:
            current.append(w)
    if current:
        lines.append(" ".join(current))
    if not lines:
        return [text]
    return lines


def _adr_links_text() -> str:
    return "\n".join(
        [
            "ADR links (paths):",
            "docs/adr/005-orthogonal-prompt-modifiers-and-defaults.md",
            "docs/adr/006-pattern-picker-and-recap.md",
            "docs/adr/008-prompt-recipe-suggestion-assistant.md",
            "docs/adr/012-style-and-method-prompt-refactor.md",
            "docs/adr/013-static-prompt-axis-refinement-and-streamlining.md",
            "docs/adr/019-meta-interpretation-channel-and-surfaces.md",
            "docs/adr/020-richer-meta-interpretation-structure.md",
            "docs/adr/022-canvas-quick-help-gui.md",
            "docs/adr/027-request-state-machine-and-progress-surfaces.md",
            "docs/adr/028-help-hub-and-discoverability.md",
            "docs/adr/040-axis-families-and-persona-contract-simplification.md",
        ]
    )


def _default_prompt_for_menu() -> Optional[str]:
    prompt = getattr(GPTState, "last_static_prompt", "") or ""
    return prompt or None


def _build_buttons() -> List[HubButton]:
    return [
        HubButton(
            label="Quick help",
            description="Open grammar quick reference",
            handler=_navigate_and_close(lambda: actions.user.model_help_canvas_open()),
            voice_hint="Say: model quick help",
        ),
        HubButton(
            label="Patterns",
            description="Open curated model patterns",
            handler=_navigate_and_close(lambda: actions.user.model_pattern_gui_open()),
            voice_hint="Say: model patterns",
        ),
        HubButton(
            label="Prompt pattern menu",
            description="Open presets for the last prompt",
            handler=_navigate_and_close(_open_prompt_pattern_menu),
            voice_hint="Say: model pattern menu <prompt>",
        ),
        HubButton(
            label="Suggestions",
            description="Reopen prompt recipe suggestions",
            handler=_navigate_and_close(
                lambda: actions.user.model_prompt_recipe_suggestions_gui_open()
            ),
            voice_hint="Say: model run suggestions",
        ),
        HubButton(
            label="History",
            description="Open request history drawer",
            handler=_navigate_and_close(
                lambda: actions.user.request_history_drawer_toggle()
            ),
            voice_hint="Say: model history drawer",
        ),
        HubButton(
            label="Providers",
            description="List/switch model providers",
            handler=_navigate_and_close(lambda: actions.user.model_provider_list()),
            voice_hint="Say: model provider list",
        ),
        HubButton(
            label="HTML docs",
            description="Open full docs in browser",
            handler=_navigate_and_close(lambda: actions.user.gpt_help()),
            voice_hint="Say: model help",
        ),
        HubButton(
            label="ADR links",
            description="Copy key ADR paths to clipboard",
            handler=_copy_adr_links,
            voice_hint="Say: model help hub (then choose ADR links)",
        ),
        HubButton(
            label="Copy cheat sheet",
            description="Copy a short command cheat sheet",
            handler=_copy_cheat_sheet,
            voice_hint="Say: model help hub (then copy)",
        ),
        HubButton(
            label="Close",
            description="Close the Help Hub",
            handler=lambda: help_hub_close(),
            voice_hint="Say: model help hub",
        ),
    ]


def _open_prompt_pattern_menu() -> None:
    prompt = _default_prompt_for_menu()
    if prompt:
        actions.user.prompt_pattern_gui_open_for_static_prompt(prompt)
    else:
        # Fall back to quick help if no last prompt is known.
        actions.user.model_help_canvas_open()


def _copy_cheat_sheet() -> None:
    try:
        clip.set_text(_cheat_sheet_text())
        actions.app.notify("Help Hub: Cheat sheet copied")
    except Exception:
        pass


def _copy_adr_links() -> None:
    try:
        clip.set_text(_adr_links_text())
        actions.app.notify("Help Hub: ADR links copied")
    except Exception:
        pass


def _navigate_and_close(handler: Callable[[], None]) -> Callable[[], None]:
    """Return a handler that closes Help Hub before navigation.

    This keeps overlay UIs from stacking by ensuring that when a Help Hub
    button opens another surface (quick help, patterns, history, etc.), the
    hub itself closes first.
    """

    def _wrapped() -> None:
        try:
            help_hub_close()
        except Exception:
            pass
        try:
            handler()
        except Exception:
            pass

    return _wrapped


def help_hub_open():
    """Open Help Hub canvas."""
    global _buttons, _layout_log_count, _scroll_log_count, _last_layout_signature
    global _global_key_handler_registered, _tap_key_handler_registered
    _buttons = _build_buttons()
    _build_search_index()
    _recompute_search_results()
    _close_overlapping_surfaces()
    HelpHubState.scroll_y = 0.0
    _layout_log_count = 0
    _scroll_log_count = 0
    _last_layout_signature = None
    _ensure_canvas()
    if _hub_canvas is None:
        try:
            _copy_cheat_sheet()
            actions.app.notify("Help Hub: unable to open; cheat sheet copied")
        except Exception:
            actions.app.notify("Help Hub: unable to open")
        return
    HelpHubState.showing = True
    if _hub_key_handler is None:
        _ensure_canvas()
    _log(f"hub key handler object: {_hub_key_handler!r}")
    if not _global_key_handler_registered and _hub_key_handler is not None:
        try:
            tap.register(tap.KEY | tap.HOOK, _hub_key_handler)
            _tap_key_handler_registered = True
            _global_key_handler_registered = True
            _log("help hub key tap handler registered")
        except Exception as e:
            _log(f"help hub key tap register failed: {e}")
    try:
        _hub_canvas.move(80, 80)
    except Exception:
        pass
    try:
        _hub_canvas.register("focus", lambda *_: None)
    except Exception as e:
        _log(f"help hub focus register failed: {e}")
    try:
        _hub_canvas.show()
        try:
            # Some runtimes require an explicit focus request; this may be a no-op elsewhere.
            focus_fn = getattr(_hub_canvas, "focus", None)
            if callable(focus_fn):
                focus_fn()
                _log("help hub focus() invoked on canvas")
        except Exception as e:
            _log(f"help hub focus() failed: {e}")
    except Exception as e:
        _log(f"help hub show failed: {e}")


def help_hub_close():
    """Close Help Hub canvas."""
    global _hub_canvas, _global_key_handler_registered, _tap_key_handler_registered
    HelpHubState.showing = False
    HelpHubState.filter_text = ""
    HelpHubState.show_onboarding = False
    if _tap_key_handler_registered:
        try:
            tap.unregister(tap.KEY | tap.HOOK, _hub_key_handler)
        except Exception as e:
            _log(f"help hub key tap unregister failed: {e}")
        _tap_key_handler_registered = False
    _global_key_handler_registered = False
    if _hub_canvas is not None:
        try:
            _hub_canvas.hide()
        except Exception as e:
            _log(f"help hub hide failed: {e}")


def help_hub_test_click(label: str) -> None:
    """Helper for tests: invoke a hub button by label."""
    for btn in _buttons:
        if btn.label == label:
            btn.handler()
            return
    for res in _search_results:
        if res.label == label:
            res.handler()
            return


def help_hub_set_filter(text: str) -> None:
    HelpHubState.filter_text = text
    _recompute_search_results()
    if not HelpHubState.showing:
        help_hub_open()


def help_hub_pick_result(index: int) -> None:
    """Invoke the Nth search result (1-based)."""
    if index < 1 or index > len(_search_results):
        return
    res = _search_results[index - 1]
    try:
        res.handler()
    except Exception:
        pass


def help_hub_onboarding() -> None:
    HelpHubState.show_onboarding = True
    help_hub_open()


def _read_list_items(filename: str) -> List[str]:
    current_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "GPT", "lists")
    )
    path = os.path.join(current_dir, filename)
    items: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" in line:
                    key, _ = line.split(":", 1)
                    items.append(key.strip())
    except FileNotFoundError:
        return []
    return items


def build_search_index(
    buttons: Sequence[HubButton],
    patterns,
    presets,
    read_list_items: Callable[[str], List[str]] = _read_list_items,
    catalog: Optional[dict] = None,
) -> List[HubButton]:
    """Pure helper: construct the Help Hub search index.

    Delegates to the HelpDomain ``help_index`` façade so index construction
    semantics live in the help domain, while this helper adapts entries into
    ``HubButton`` instances for the canvas UI.
    """
    logical_entries = help_index(
        buttons, patterns, presets, read_list_items, catalog=catalog
    )

    entries: List[HubButton] = []
    for entry in logical_entries:
        # ``help_index`` currently returns ``HelpIndexEntry`` instances, but we
        # only rely on the public attributes here so the domain layer can
        # evolve independently.
        entries.append(
            HubButton(
                label=getattr(entry, "label", ""),
                description=getattr(entry, "description", ""),
                handler=getattr(entry, "handler", lambda: None),
                voice_hint=getattr(entry, "voice_hint", ""),
            )
        )

    return entries


def _build_search_index() -> None:
    global _search_index
    _search_index = build_search_index(
        _buttons, PATTERNS, PROMPT_PRESETS, _read_list_items, catalog=axis_catalog()
    )


def search_results_for(query: str, index: List[HubButton]) -> List[HubButton]:
    """Pure helper: compute search results for a query and index.

    Delegates to the HelpDomain façade so search semantics are centralised in
    ``helpDomain`` while keeping this backward-compatible entrypoint.
    """

    # ``help_search`` already implements the case-insensitive substring match
    # on labels that used to live here.
    results = help_search(query, index)
    # Narrow the result type back to ``HubButton`` for callers in this module.
    return [item for item in results if isinstance(item, HubButton)]


def _recompute_search_results() -> None:
    global _search_results
    _search_results = search_results_for(HelpHubState.filter_text, _search_index)
    _log(
        f"filter={(HelpHubState.filter_text or '').lower()!r}, results={len(_search_results)}"
    )
    _clamp_scroll()


def _clamp_scroll() -> None:
    HelpHubState.scroll_y = clamp_scroll(HelpHubState.scroll_y, HelpHubState.max_scroll)


def _handle_scroll_delta(evt) -> None:
    """Normalize scroll delta from various Talon event shapes and apply it."""
    try:
        # Try the common dy / wheel_y fields first.
        raw = getattr(evt, "dy", None) or getattr(evt, "wheel_y", None)
        # Talon sometimes provides delta_y, pixels.y, or degrees.y
        if raw is None:
            raw = getattr(evt, "delta_y", None)
        if raw is None:
            pixels = getattr(evt, "pixels", None)
            if pixels is not None and hasattr(pixels, "y"):
                raw = getattr(pixels, "y", None)
        if raw is None:
            degrees = getattr(evt, "degrees", None)
            if degrees is not None and hasattr(degrees, "y"):
                raw = getattr(degrees, "y", None)
        if raw is None:
            if _scroll_log_count < 6:
                globals()["_scroll_log_count"] = _scroll_log_count + 1
            return
        try:
            raw = float(raw)
        except Exception:
            if _scroll_log_count < 6:
                globals()["_scroll_log_count"] = _scroll_log_count + 1
            return
        if not raw:
            return
        new_scroll = HelpHubState.scroll_y - raw * 40.0
        HelpHubState.scroll_y = clamp_scroll(new_scroll, HelpHubState.max_scroll)
        _clamp_scroll()
        if _scroll_log_count < 6:
            globals()["_scroll_log_count"] = _scroll_log_count + 1
        try:
            if _hub_canvas is not None:
                _hub_canvas.show()
        except Exception:
            pass
    except Exception:
        return


def _handle_click(x: float, y: float) -> bool:
    """Handle click targets inside the hub. Returns True if handled.

    Button and result activation is now handled via HelpDomain through the
    main ``_on_mouse`` handler; this helper keeps only the close affordance so
    click semantics stay centralised while the close box remains cheap to hit.
    """
    # Close if we hit the explicit close box.
    close_rect = _button_bounds.get("__close__")
    if close_rect is None:
        try:
            if _hub_canvas is not None and hasattr(_hub_canvas, "rect"):
                cr = _hub_canvas.rect
                close_rect = skia.Rect(
                    cr.x + _PANEL_WIDTH - _PADDING_X - 24, cr.y + 2, 22, 22
                )
        except Exception:
            close_rect = None
    if close_rect and _rect_contains(close_rect, x, y):
        _log(f"click close at ({x},{y}) in {close_rect}")
        help_hub_close()
        return True

    return False


def focusable_items_for(
    filter_text: str, buttons: Sequence[HubButton], results: Sequence[HubButton]
) -> List[tuple[str, str]]:
    """Pure helper: ordered list of (kind,label) focus targets.

    Delegates to the HelpDomain façade so the core navigation contract lives in
    ``helpDomain`` while callers here retain the same signature.
    """

    return help_focusable_items(filter_text, buttons, results)


def _focusable_items() -> List[tuple[str, str]]:
    """Return an ordered list of (kind,label) focus targets."""
    return focusable_items_for(
        HelpHubState.filter_text or "", _buttons, _search_results
    )


def _next_focus_label(current: str, delta: int, items: List[tuple[str, str]]) -> str:
    """Compute the next focus label given current label and step.

    Delegates to the HelpDomain façade so the navigation core is centralised in
    ``helpDomain`` while existing tests can still target this helper.
    """

    return help_next_focus_label(current, delta, items)


def _focus_step(delta: int) -> None:
    items = _focusable_items()
    if not items:
        return
    current = HelpHubState.hover_label or ""
    new_label = _next_focus_label(current, delta, items)
    if not new_label:
        return
    HelpHubState.hover_label = new_label
    try:
        if _hub_canvas is not None:
            _hub_canvas.show()
    except Exception:
        pass


def _activate_focus() -> bool:
    """Activate the currently focused hub item, if any.

    Resolution of which object to invoke is delegated to the HelpDomain
    façade so that Help Hub remains a thin adapter over the domain semantics.
    """

    label = HelpHubState.hover_label or ""
    target = help_activation_target(label, _buttons, _search_results)
    if target is None:
        return False
    try:
        handler = getattr(target, "handler", None)
        if callable(handler):
            handler()
    except Exception:
        pass
    return True


@mod.action_class
class UserActions:
    def help_hub_open():
        """Open the Help Hub canvas"""
        if _reject_if_request_in_flight():
            return
        help_hub_open()

    def help_hub_close():
        """Close the Help Hub canvas"""
        if _reject_if_request_in_flight():
            return
        help_hub_close()

    def help_hub_toggle():
        """Toggle the Help Hub canvas"""
        if _reject_if_request_in_flight():
            return
        if HelpHubState.showing:
            help_hub_close()
        else:
            help_hub_open()

    def help_hub_copy_cheat_sheet():
        """Copy the Help Hub cheat sheet to the clipboard"""
        if _reject_if_request_in_flight():
            return
        _copy_cheat_sheet()

    def help_hub_test_click(label: str):
        """Test helper: invoke a hub button by label (for unit tests)."""
        if _reject_if_request_in_flight():
            return
        help_hub_test_click(label)

    def help_hub_onboarding():
        """Open Help Hub with onboarding tips shown"""
        if _reject_if_request_in_flight():
            return
        HelpHubState.show_onboarding = True
        help_hub_open()

    def help_hub_set_filter(text: str):
        """Set Help Hub filter (opens the hub if needed)"""
        if _reject_if_request_in_flight():
            return
        help_hub_set_filter(text)

    def help_hub_pick_result(index: int):
        """Activate Nth search result (1-based)"""
        if _reject_if_request_in_flight():
            return
        help_hub_pick_result(index)
