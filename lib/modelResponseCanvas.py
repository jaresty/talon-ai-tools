from typing import Callable, Optional, Any, Dict

from talon import Context, Module, actions, canvas, clip, ui, skia, settings
import traceback
import time

from .axisJoin import axis_join
from .canvasFont import apply_canvas_typeface, draw_text_with_emoji_fallback

from .modelState import GPTState
from .modelDestination import _parse_meta
from .requestGating import request_is_in_flight
from .requestBus import current_state
from .historyLifecycle import (
    RequestPhase,
    RequestState,
    last_drop_reason,
    set_drop_reason,
)
from .responseCanvasFallback import (
    clear_response_fallback,
    fallback_for,
)

from .surfaceGuidance import guard_surface_request

from .axisConfig import axis_docs_for
from .axisMappings import axis_registry_tokens
from .suggestionCoordinator import (
    last_recipe_snapshot,
    last_recap_snapshot,
    suggestion_grammar_phrase,
)
from .stanceDefaults import stance_defaults_lines
from .overlayHelpers import apply_canvas_blocking, clamp_scroll
from .overlayLifecycle import close_overlays, close_common_overlays
from .personaConfig import persona_intent_maps
from .personaOrchestrator import get_persona_intent_orchestrator
from . import personaConfig as _persona_config_module

mod = Module()
ctx = Context()


DEFAULT_TRACE_CANVAS_FLOW = 0


class ResponseCanvasState:
    """State specific to the canvas-based response viewer.

    The scroll implementation for the answer body does a fair amount of
    line-wrapping work on each draw. To keep scroll and scrollbar updates
    responsive for long responses, we cache the wrapped lines keyed by the
    answer text and an approximate character width.
    """

    showing: bool = False
    scroll_y: float = 0.0
    meta_expanded: bool = False
    max_scroll: float = 1e9
    # Cache for wrapped answer lines so scroll draws stay lightweight.
    lines_cache_key: tuple[str, int] | None = None
    lines_cache: list[str] | None = None
    # Request id the user pinned when expanding meta; used to avoid collapsing
    # within the same request even if ids firm up mid-stream.
    meta_pinned_request_id: str = ""
    suppress_hide_reset: bool = False
    previous_window = None
    last_close_event: float = 0.0


_EVENT_LOG_LIMIT = 0  # disable event logging in production
_event_log_count = 0
_last_draw_error: Optional[str] = None

try:
    _last_meta_signature
except NameError:
    _last_meta_signature = None


def _capture_previous_focus() -> None:
    if getattr(ResponseCanvasState, "showing", False):
        return
    try:
        window = ui.active_window()
    except Exception:
        window = None
    try:
        has_focus = callable(getattr(window, "focus", None))
    except Exception:
        has_focus = False
    try:
        ResponseCanvasState.previous_window = window if has_focus else None
    except Exception:
        pass


def _restore_previous_focus() -> None:
    try:
        window = getattr(ResponseCanvasState, "previous_window", None)
    except Exception:
        window = None
    try:
        ResponseCanvasState.previous_window = None
    except Exception:
        pass
    if not window:
        return
    try:
        focus = getattr(window, "focus", None)
        if callable(focus):
            focus()
    except Exception:
        pass


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""

    try:
        return request_is_in_flight()
    except Exception:
        return False


def _reject_if_request_in_flight(*, allow_inflight: bool = False) -> bool:
    """Return True when the response canvas should abort due to gating."""

    def _handle_block(reason: str, message: str) -> None:
        if reason != "in_flight":
            return
        try:
            GPTState.suppress_response_canvas_close = False
        except Exception:
            pass
        try:
            state = _current_request_state()
        except Exception:
            state = None
        phase = getattr(state, "phase", None)
        if phase not in (RequestPhase.SENDING, RequestPhase.STREAMING):
            return
        try:
            from .pillCanvas import show_pill  # type: ignore circular

            phase_label = (
                "Model: sending…"
                if phase is RequestPhase.SENDING
                else "Model: streaming…"
            )
            show_pill(phase_label, phase)
        except Exception:
            pass

    return guard_surface_request(
        surface="response_canvas",
        source="modelResponseCanvas",
        state_getter=_current_request_state,
        on_block=_handle_block,
        allow_inflight=allow_inflight,
    )


def _hydrate_axis(axis: str, token_str: str) -> str:
    """Return hydrated description(s) for a space-separated token string.

    Uses the AxisDocs façade so response surfaces share the same
    documentation source as quick help and other Concordance views.
    """
    tokens = [t for t in token_str.split() if t]
    if not tokens:
        return ""
    docs = axis_docs_for(axis)
    mapping = {doc.key: doc.description for doc in docs}
    hydrated = [mapping.get(token, token) for token in tokens]
    return " ".join(hydrated) if hydrated else token_str


def _wrap_text(text: str, max_chars: int = 96) -> list[str]:
    """Naive word-wrap for canvas text rendering."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    count = 0
    for word in words:
        if count + len(word) + (1 if current else 0) > max_chars and current:
            lines.append(" ".join(current))
            current = [word]
            count = len(word)
        else:
            current.append(word)
            count += len(word) + (1 if len(current) > 1 else 0)
    if current:
        lines.append(" ".join(current))
    return lines


def _prefer_canvas_progress() -> bool:
    try:
        kind = getattr(GPTState, "current_destination_kind", "") or ""
    except Exception:
        kind = ""
    return kind in ("window", "default")


def _current_request_state() -> RequestState:
    try:
        return current_state()
    except Exception:
        return RequestState()


def _reset_meta_if_new_signature(
    recipe_snapshot: dict[str, object],
    recap_snapshot: dict[str, str],
    request_id: str,
) -> None:
    """Collapse meta when a new request arrives; preserve it for inflight updates."""
    last_signature = globals().get("_last_meta_signature")
    if not isinstance(last_signature, tuple):
        last_signature = None
    prev_request_id = last_signature[0] if last_signature else ""
    effective_request_id = request_id or prev_request_id
    signature = (
        effective_request_id,
        str(recap_snapshot.get("response", "")),
        str(recap_snapshot.get("meta", "")),
        str(recipe_snapshot.get("recipe", "")),
    )
    if last_signature is None:
        globals()["_last_meta_signature"] = signature
        return

    pinned_id = getattr(ResponseCanvasState, "meta_pinned_request_id", "") or ""
    if ResponseCanvasState.meta_expanded and not pinned_id and effective_request_id:
        # Remember the request id associated with this manual expansion so we
        # can keep meta open across streaming → completion updates.
        ResponseCanvasState.meta_pinned_request_id = effective_request_id
        pinned_id = effective_request_id

    is_new_request = False
    if (
        ResponseCanvasState.meta_expanded
        and pinned_id
        and effective_request_id
        and effective_request_id != pinned_id
    ):
        is_new_request = True
    elif (
        not ResponseCanvasState.meta_expanded
        and bool(prev_request_id)
        and bool(request_id)
        and request_id != prev_request_id
    ):
        is_new_request = True

    if is_new_request:
        ResponseCanvasState.meta_expanded = False
        ResponseCanvasState.meta_pinned_request_id = ""
        try:
            GPTState.suppress_response_canvas_close = False
        except Exception:
            pass
    elif signature != last_signature and not ResponseCanvasState.meta_expanded:
        # Only collapse on updates for the same request when the user has not
        # explicitly expanded meta.
        ResponseCanvasState.meta_expanded = False
        ResponseCanvasState.meta_pinned_request_id = ""

    globals()["_last_meta_signature"] = signature


_response_canvas: Optional[canvas.Canvas] = None
_response_draw_handlers: list[Callable] = []
_response_button_bounds: dict[str, tuple[int, int, int, int]] = {}
_response_drag_offset: Optional[tuple[float, float]] = None
_response_hover_close: bool = False
_response_hover_button: Optional[str] = None
_response_mouse_log_count: int = 0
_response_handlers_registered: bool = False
_last_hide_handler: Optional[Callable] = None
_last_recap_log: Optional[tuple[str, str, str, str, str, str]] = None
_PERSONA_INTENT_MAPS_CACHE = None
_get_persona_orchestrator = get_persona_intent_orchestrator


def reset_persona_intent_maps_cache() -> None:
    global _PERSONA_INTENT_MAPS_CACHE
    _PERSONA_INTENT_MAPS_CACHE = None


def _persona_intent_maps_cached():
    global _PERSONA_INTENT_MAPS_CACHE
    if _PERSONA_INTENT_MAPS_CACHE is None:
        _PERSONA_INTENT_MAPS_CACHE = persona_intent_maps()
    return _PERSONA_INTENT_MAPS_CACHE


if hasattr(_persona_config_module, "persona_intent_maps_reset"):
    _original_persona_intent_maps_reset = (
        _persona_config_module.persona_intent_maps_reset
    )

    def _persona_intent_maps_reset_proxy(*args, **kwargs):
        reset_persona_intent_maps_cache()
        return _original_persona_intent_maps_reset(*args, **kwargs)

    _persona_config_module.persona_intent_maps_reset = _persona_intent_maps_reset_proxy


def _coerce_text(value) -> str:
    """Best-effort convert various payloads to displayable text."""
    try:
        if isinstance(value, str):
            return value
        if hasattr(value, "display_text"):
            return getattr(value, "display_text", "") or ""
        if hasattr(value, "browser_lines"):
            lines = getattr(value, "browser_lines", None)
            if isinstance(lines, list):
                return "\n".join(str(item) for item in lines)
            if isinstance(lines, str):
                return lines
        if value is None:
            return ""
        return str(value)
    except Exception:
        return ""


def _debug(msg: str) -> None:
    try:
        print(f"GPT response canvas: {msg}")
    except Exception:
        pass


def _trace_canvas_event(event: str, **data) -> None:
    try:
        enabled = bool(
            settings.get("user.gpt_trace_canvas_flow", DEFAULT_TRACE_CANVAS_FLOW)
        )
    except Exception:
        enabled = False
    if not enabled:
        return
    parts = [f"[canvas-flow] {event}"]
    if data:
        details = " ".join(f"{key}={value!r}" for key, value in data.items())
        parts.append(details)
    message = " ".join(parts)
    try:
        print(message)
    except Exception:
        pass
    try:
        stack = "".join(traceback.format_stack(limit=8))
        if stack:
            print(stack)
    except Exception:
        pass


def _reset_event_log() -> None:
    """No-op: event logging disabled in production for performance."""
    globals()["_event_log_count"] = 0


def _log_event(evt, extra: str = "") -> None:
    """No-op when logging is disabled."""
    return


def _log_canvas_close(reason: str) -> None:
    """Best-effort tracing for unexpected canvas closes."""
    try:
        state = _current_request_state()
    except Exception:
        state = RequestState()
    try:
        phase = getattr(state, "phase", None)
        surface = getattr(state, "active_surface", None)
    except Exception:
        phase = None
        surface = None
    try:
        showing = getattr(ResponseCanvasState, "showing", False)
    except Exception:
        showing = False
    _debug(f"close reason={reason} showing={showing} phase={phase} surface={surface}")
    _trace_canvas_event(
        "canvas_close",
        reason=reason,
        showing=showing,
        phase=str(phase),
        surface=str(surface),
    )


def _guard_response_canvas(allow_inflight: bool = False) -> bool:
    """Return True when the action should abort due to an in-flight request.

    When ``allow_inflight`` is True, the shared guard only bypasses
    ``in_flight`` blocks while still enforcing other drop reasons.
    """
    return _reject_if_request_in_flight(allow_inflight=allow_inflight)


def _ensure_response_canvas() -> canvas.Canvas:
    """Create the response canvas if needed and register handlers."""
    global _response_canvas, _response_handlers_registered, _last_hide_handler
    _reset_event_log()

    def _reset_response_scroll_state() -> None:
        """Reset scroll-related state when the canvas is hidden or reopened.

        This keeps wrapped-line caches in sync with the current answer text
        and avoids carrying large cached lists across unrelated responses.
        """
        try:
            ResponseCanvasState.showing = False
            ResponseCanvasState.scroll_y = 0.0
            ResponseCanvasState.max_scroll = 1e9
            ResponseCanvasState.lines_cache_key = None
            ResponseCanvasState.lines_cache = None
        except Exception:
            pass

    def _hide_handler():
        try:
            clear_response_fallback(getattr(GPTState, "last_request_id", None))
        except Exception:
            pass
        _log_canvas_close("canvas hide handler")
        try:
            reset_ok = not getattr(ResponseCanvasState, "suppress_hide_reset", False)
            if reset_ok:
                _reset_response_scroll_state()
                ResponseCanvasState.meta_expanded = False
                ResponseCanvasState.meta_pinned_request_id = ""
                try:
                    GPTState.suppress_response_canvas_close = False
                except Exception:
                    pass
        except Exception:
            pass
        try:
            ResponseCanvasState.showing = False
            try:
                GPTState.response_canvas_showing = False
            except Exception:
                pass
        except Exception:
            pass
        _restore_previous_focus()

    _last_hide_handler = _hide_handler

    def _prime_footer_bounds_for_tests(c: canvas.Canvas) -> None:
        """Populate footer button bounds when draw is not invoked (tests)."""
        rect = getattr(c, "rect", None)
        if rect is None:
            return
        x = getattr(rect, "x", 0) + 40
        footer_y = getattr(rect, "y", 0) + getattr(rect, "height", 300) - 60 + 18 // 2
        btn_labels = [
            ("paste", "[Paste response]"),
            ("copy", "[Copy response]"),
            ("discard", "[Discard response]"),
            ("context", "[Pass to context]"),
            ("query", "[Pass to query]"),
            ("thread", "[Pass to thread]"),
            ("browser", "[Open browser]"),
            ("analyze", "[Analyze prompt]"),
        ]
        btn_x = x
        approx_char = 8
        max_footer_x = getattr(rect, "x", 0) + getattr(rect, "width", 1000) - 40
        for key, label in btn_labels:
            width = len(label) * approx_char
            if btn_x + width > max_footer_x:
                footer_y += 18 * 2
                btn_x = x
            label_x = btn_x
            _response_button_bounds[key] = (
                int(label_x),
                int(footer_y - 18),
                int(label_x + width),
                int(footer_y),
            )
            btn_x += width + approx_char

    if _response_canvas is not None:
        return _response_canvas

    screen = ui.main_screen()
    try:
        screen_x = getattr(screen, "x", 0)
        screen_y = getattr(screen, "y", 0)
        screen_width = getattr(screen, "width", 1600)
        screen_height = getattr(screen, "height", 900)
        margin_x = 40
        margin_y = 32
        panel_width = min(900, max(screen_width - 2 * margin_x, 600))
        max_available_height = max(screen_height - 2 * margin_y, 480)
        preferred_height = max(int(screen_height * 0.85), 520)
        panel_height = min(preferred_height, max_available_height, 1000)
        start_x = screen_x + max((screen_width - panel_width) // 2, margin_x)
        start_y = screen_y + max((screen_height - panel_height) // 2, margin_y)
        rect = ui.Rect(start_x, start_y, panel_width, panel_height)
        _response_canvas = canvas.Canvas.from_rect(rect)
    except Exception:
        _response_canvas = canvas.Canvas.from_screen(screen)

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        global _last_draw_error
        for handler in list(_response_draw_handlers):
            try:
                handler(c)
            except Exception as e:
                # Log the first error per draw; suppress repeats until next draw.
                if _last_draw_error != str(e):
                    try:
                        _debug(f"response canvas draw handler error: {e}")
                    except Exception:
                        pass
                    _last_draw_error = str(e)

    if _response_canvas is not None:
        try:
            apply_canvas_blocking(_response_canvas)
        except Exception:
            pass
        if not _response_handlers_registered:
            _response_canvas.register("draw", _on_draw)

        def _on_hide(*_args, **_kwargs):
            _hide_handler()

        try:
            _last_hide_handler = _on_hide
            _response_canvas.register("hide", _on_hide)
        except Exception:
            pass
        try:
            setattr(_response_canvas, "_on_hide_handler", _on_hide)
        except Exception:
            pass

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        try:
            global \
                _response_drag_offset, \
                _response_hover_close, \
                _response_hover_button, \
                _response_mouse_log_count
            rect = getattr(_response_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type_raw = getattr(evt, "event", "") or ""
            event_type = str(event_type_raw).lower()
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos
            try:
                from talon import ctrl as _ctrl  # type: ignore

                mouse_x, mouse_y = _ctrl.mouse_pos()
            except Exception:
                mouse_x = getattr(gpos, "x", 0.0)
                mouse_y = getattr(gpos, "y", 0.0)

            local_x = pos.x
            local_y = pos.y
            if local_x < 0 or local_y < 0:
                return
            abs_x = rect.x + local_x
            abs_y = rect.y + local_y

            if event_type in ("mousemove", "mouse_move"):
                hover_key: Optional[str] = None
                for key, (bx1, by1, bx2, by2) in list(_response_button_bounds.items()):
                    if bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2:
                        hover_key = key
                        break
                _response_hover_button = hover_key
                _response_hover_close = hover_key == "close"

            # Handle close click and drag start.
            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Button hits in header/footer.
                for key, (bx1, by1, bx2, by2) in list(_response_button_bounds.items()):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    # Use the same selection as the body: prefer the current
                    # confirmation text, then fall back to the last response.
                    answer = (
                        getattr(GPTState, "text_to_confirm", "")
                        or getattr(GPTState, "last_response", "")
                        or ""
                    )
                    try:
                        if key == "cancel":
                            actions.user.gpt_cancel_request()
                        elif key in ("meta_toggle", "meta_toggle_region"):
                            ResponseCanvasState.meta_expanded = (
                                not ResponseCanvasState.meta_expanded
                            )
                            if ResponseCanvasState.meta_expanded:
                                # Pin to the current request id so inflight
                                # completions don't auto-collapse meta.
                                ResponseCanvasState.meta_pinned_request_id = (
                                    getattr(GPTState, "last_request_id", "") or ""
                                )
                            else:
                                ResponseCanvasState.meta_pinned_request_id = ""
                            _response_canvas.show()
                        elif key == "paste":
                            try:
                                from .modelConfirmationGUI import (
                                    ConfirmationGUIState,
                                )  # type: ignore circular
                            except Exception:
                                ConfirmationGUIState = None  # type: ignore
                            presentation = None
                            display_thread = False
                            last_item_text = ""
                            if ConfirmationGUIState is not None:
                                try:
                                    presentation = (
                                        ConfirmationGUIState.current_presentation
                                    )
                                    display_thread = ConfirmationGUIState.display_thread
                                    last_item_text = ConfirmationGUIState.last_item_text
                                except Exception:
                                    presentation = None
                            actions.user.model_response_canvas_close()
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            if ConfirmationGUIState is not None:
                                try:
                                    ConfirmationGUIState.current_presentation = (
                                        presentation
                                    )
                                    ConfirmationGUIState.display_thread = display_thread
                                    ConfirmationGUIState.last_item_text = last_item_text
                                except Exception:
                                    pass
                            if answer:
                                try:
                                    GPTState.text_to_confirm = answer
                                except Exception:
                                    pass
                            actions.user.confirmation_gui_paste()
                        elif key == "copy":
                            actions.user.confirmation_gui_copy()
                            actions.user.model_response_canvas_close()
                        elif key == "discard":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.model_response_canvas_close()
                        elif key == "context":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.confirmation_gui_pass_context()
                            actions.user.model_response_canvas_close()
                        elif key == "query":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.confirmation_gui_pass_query()
                            actions.user.model_response_canvas_close()
                        elif key == "thread":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.confirmation_gui_pass_thread()
                            actions.user.model_response_canvas_close()
                        elif key == "browser":
                            if answer:
                                actions.user.gpt_open_browser(answer)
                            else:
                                actions.user.confirmation_gui_open_browser()
                            actions.user.model_response_canvas_close()
                        elif key == "analyze":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.confirmation_gui_analyze_prompt()
                            actions.user.model_response_canvas_close()
                        elif key == "patterns":
                            close_overlays(
                                (getattr(actions.user, "confirmation_gui_close", None),)
                            )
                            actions.user.confirmation_gui_open_pattern_menu_for_prompt()
                            actions.user.model_response_canvas_close()
                        elif key == "quick_help":
                            actions.user.model_help_canvas_open_for_last_recipe()
                    except Exception:
                        pass
                    if key == "close":
                        ResponseCanvasState.showing = False
                        ResponseCanvasState.scroll_y = 0.0
                        try:
                            _response_canvas.hide()
                        except Exception:
                            pass
                        _response_drag_offset = None
                        return
                    return

                # Start drag anywhere else.
                _response_drag_offset = (mouse_x - rect.x, mouse_y - rect.y)
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
                return

            # Drag while moving.
            if (
                event_type
                in ("mouse", "mousemove", "mouse_move", "mouse_drag", "mouse_dragged")
                and _response_drag_offset is not None
            ):
                dx, dy = _response_drag_offset
                new_x = mouse_x - dx
                new_y = mouse_y - dy
                try:
                    _response_canvas.move(new_x, new_y)
                except Exception:
                    _response_drag_offset = None
        except Exception:
            return

    if not _response_handlers_registered:
        try:
            _response_canvas.register("mouse", _on_mouse)
        except Exception:
            pass

    def _on_scroll(evt) -> None:  # pragma: no cover - visual only
        """Handle high-level scroll events when the runtime exposes them."""
        try:
            rect = getattr(_response_canvas, "rect", None)
            if rect is None:
                return
            _log_event(evt, extra="scroll_evt")
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
                ResponseCanvasState.scroll_y = clamp_scroll(
                    ResponseCanvasState.scroll_y - raw, ResponseCanvasState.max_scroll
                )
        except Exception:
            return

    if not _response_handlers_registered:
        for evt_name in ("scroll", "wheel", "mouse_scroll"):
            try:
                _response_canvas.register(evt_name, _on_scroll)
            except Exception:
                pass

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = (getattr(evt, "key", "") or "").lower()
            if key in ("escape", "esc"):
                ResponseCanvasState.showing = False
                try:
                    _response_canvas.hide()
                except Exception:
                    pass
            elif key in ("pagedown", "page_down"):
                ResponseCanvasState.scroll_y = clamp_scroll(
                    ResponseCanvasState.scroll_y + 200, ResponseCanvasState.max_scroll
                )
            elif key in ("pageup", "page_up"):
                ResponseCanvasState.scroll_y = clamp_scroll(
                    ResponseCanvasState.scroll_y - 200, ResponseCanvasState.max_scroll
                )
            elif key in ("down", "j"):
                ResponseCanvasState.scroll_y = clamp_scroll(
                    ResponseCanvasState.scroll_y + 40, ResponseCanvasState.max_scroll
                )
            elif key in ("up", "k"):
                ResponseCanvasState.scroll_y = clamp_scroll(
                    ResponseCanvasState.scroll_y - 40, ResponseCanvasState.max_scroll
                )
        except Exception:
            return

    if not _response_handlers_registered:
        try:
            _response_canvas.register("key", _on_key)
        except Exception:
            pass
    # Populate footer button bounds immediately so tests have hit targets even
    # when the canvas stub does not auto-draw.
    try:
        _prime_footer_bounds_for_tests(_response_canvas)
    except Exception:
        pass
    # Prime an initial draw so hit targets exist even when the canvas stub
    # does not automatically trigger draw() in tests.
    try:
        _on_draw(_response_canvas)
    except Exception:
        pass

    _response_handlers_registered = True

    return _response_canvas


def register_response_draw_handler(handler: Callable) -> None:
    if handler not in _response_draw_handlers:
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
    raw_lines = _coerce_text(answer).splitlines() or [answer]
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

    approx_char = 8
    state = _current_request_state()
    phase = getattr(state, "phase", RequestPhase.IDLE)
    state_request_id = getattr(state, "request_id", None) or ""
    cancel_requested = getattr(state, "cancel_requested", False)
    prefer_progress = _prefer_canvas_progress()
    inflight = phase in (
        RequestPhase.SENDING,
        RequestPhase.STREAMING,
        RequestPhase.CANCELLED,
    )

    # Header with close affordance and optional progress/cancel controls.
    draw_text("Model response viewer", x, y)
    close_y = rect.y + 24 if rect is not None else y
    right_cursor = rect.x + rect.width - 16 if rect is not None else None

    def _header_label(label: str, key: Optional[str] = None, hover: bool = False):
        nonlocal right_cursor
        if right_cursor is None:
            return
        width = len(label) * approx_char
        right_cursor -= width
        draw_text(label, right_cursor, close_y)
        if key:
            _response_button_bounds[key] = (
                right_cursor,
                close_y - line_h,
                right_cursor + width,
                close_y + line_h,
            )
            if hover:
                try:
                    underline_rect = ui.Rect(right_cursor, close_y + 4, width, 1)
                    # Draw an underline using a dedicated Paint to avoid clashes.
                    underline_paint = getattr(skia, "Paint", None)
                    if underline_paint is not None:
                        p = underline_paint()
                        p.color = default_text_color or "FFFFFF"
                        c.draw_rect(underline_rect, p)
                    else:
                        if paint is not None:
                            old_color = getattr(paint, "color", None)
                            paint.color = default_text_color or "FFFFFF"
                            c.draw_rect(underline_rect, paint)
                            if old_color is not None:
                                paint.color = old_color
                        else:
                            c.draw_rect(underline_rect)
                except Exception as e:
                    _debug(f"response close underline draw failed: {e}")
        right_cursor -= approx_char * 2

    status_label = ""
    cancel_label = ""
    if phase is RequestPhase.SENDING:
        status_label = "Sending…"
        if not cancel_requested:
            cancel_label = "[Cancel]"
    elif phase is RequestPhase.STREAMING:
        status_label = "Streaming…"
        if not cancel_requested:
            cancel_label = "[Cancel]"
    elif phase is RequestPhase.CANCELLED:
        status_label = "Cancel requested"
    elif phase is RequestPhase.ERROR:
        status_label = "Failed"
    elif phase is RequestPhase.DONE:
        status_label = "Done"

    _header_label("[X]", key="close", hover=_response_hover_button == "close")
    if cancel_label:
        _header_label(
            cancel_label,
            key="cancel",
            hover=_response_hover_button == "cancel",
        )
    if status_label:
        _header_label(status_label)
    y += line_h

    # Compact prompt recap under the title so users can see which recipe and
    # spoken form produced the current response. Prefer the structured
    # axis fields when available so we keep this recap concise and
    # token-based even if older code paths stored a verbose last_recipe.
    recipe_snapshot = last_recipe_snapshot()
    recap_snapshot = last_recap_snapshot()
    # Use the request id from the current request state when deciding whether
    # meta should reset; when the id is missing, preserve the previous pinned
    # id instead of falling back to any global last_request_id.
    _reset_meta_if_new_signature(
        recipe_snapshot,
        recap_snapshot,
        state_request_id,
    )
    recipe = recipe_snapshot.get("recipe", "") or ""
    static_prompt = recipe_snapshot.get("static_prompt", "") or ""
    axes_tokens = {
        "completeness": recipe_snapshot.get("completeness", ""),
        "scope": recipe_snapshot.get("scope_tokens", []) or [],
        "method": recipe_snapshot.get("method_tokens", []) or [],
        "form": recipe_snapshot.get("form_tokens", []) or [],
        "channel": recipe_snapshot.get("channel_tokens", []) or [],
    }

    try:
        persona_maps = _persona_intent_maps_cached()
    except Exception:
        persona_maps = None

    try:
        orchestrator = _get_persona_orchestrator()
    except Exception:
        orchestrator = None

    persona_presets_lookup: dict[str, Any] = {}
    if orchestrator and getattr(orchestrator, "persona_presets", None):
        persona_presets_lookup.update(dict(orchestrator.persona_presets or {}))
    if persona_maps and getattr(persona_maps, "persona_presets", None):
        persona_presets_lookup.update(dict(persona_maps.persona_presets or {}))

    persona_aliases_lookup: dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "persona_aliases", None):
        for alias, canonical in dict(orchestrator.persona_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                persona_aliases_lookup.setdefault(alias_key, canonical_value)
    if persona_maps and getattr(persona_maps, "persona_preset_aliases", None):
        for alias, canonical in dict(persona_maps.persona_preset_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                persona_aliases_lookup.setdefault(alias_key, canonical_value)

    axis_alias_lookup: dict[str, dict[str, str]] = {}
    if orchestrator and getattr(orchestrator, "axis_alias_map", None):
        for axis, mapping in dict(orchestrator.axis_alias_map or {}).items():
            axis_key = str(axis or "").strip().lower()
            if not axis_key:
                continue
            aliases = axis_alias_lookup.setdefault(axis_key, {})
            for alias, canonical in dict(mapping or {}).items():
                alias_key = str(alias or "").strip().lower()
                canonical_value = str(canonical or "").strip()
                if alias_key and canonical_value:
                    aliases.setdefault(alias_key, canonical_value)
    if persona_maps and getattr(persona_maps, "persona_axis_tokens", None):
        for axis, mapping in dict(persona_maps.persona_axis_tokens or {}).items():
            axis_key = str(axis or "").strip().lower()
            if not axis_key:
                continue
            aliases = axis_alias_lookup.setdefault(axis_key, {})
            for alias, canonical in dict(mapping or {}).items():
                alias_key = str(alias or "").strip().lower()
                canonical_value = str(canonical or "").strip()
                if alias_key and canonical_value:
                    aliases.setdefault(alias_key, canonical_value)

    intent_presets_lookup: dict[str, Any] = {}
    if orchestrator and getattr(orchestrator, "intent_presets", None):
        intent_presets_lookup.update(dict(orchestrator.intent_presets or {}))
    if persona_maps and getattr(persona_maps, "intent_presets", None):
        intent_presets_lookup.update(dict(persona_maps.intent_presets or {}))

    intent_aliases_lookup: dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_aliases", None):
        for alias, canonical in dict(orchestrator.intent_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                intent_aliases_lookup.setdefault(alias_key, canonical_value)
    if persona_maps and getattr(persona_maps, "intent_preset_aliases", None):
        for alias, canonical in dict(persona_maps.intent_preset_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                intent_aliases_lookup.setdefault(alias_key, canonical_value)

    intent_synonyms_lookup: dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_synonyms", None):
        for alias, canonical in dict(orchestrator.intent_synonyms or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                intent_synonyms_lookup.setdefault(alias_key, canonical_value)
    if persona_maps and getattr(persona_maps, "intent_synonyms", None):
        for alias, canonical in dict(persona_maps.intent_synonyms or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_value = str(canonical or "").strip()
            if alias_key and canonical_value:
                intent_synonyms_lookup.setdefault(alias_key, canonical_value)

    intent_display_lookup: dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_display_map", None):
        for key, value in dict(orchestrator.intent_display_map or {}).items():
            canonical_key = str(key or "").strip()
            display_value = str(value or "").strip()
            if canonical_key and display_value:
                intent_display_lookup.setdefault(canonical_key.lower(), display_value)
    if persona_maps and getattr(persona_maps, "intent_display_map", None):
        for key, value in dict(persona_maps.intent_display_map or {}).items():
            canonical_key = str(key or "").strip()
            display_value = str(value or "").strip()
            if canonical_key and display_value:
                intent_display_lookup.setdefault(canonical_key.lower(), display_value)

    def _canonical_axis_token(axis: str, raw_value: str) -> str:
        token = str(raw_value or "").strip()
        if not token:
            return ""
        axis_key = str(axis or "").strip()
        axis_lower = axis_key.lower()
        if orchestrator:
            try:
                canonical = orchestrator.canonical_axis_token(axis_lower, token)
            except Exception:
                canonical = ""
            if canonical:
                return canonical
        alias_map = axis_alias_lookup.get(axis_lower, {})
        canonical = alias_map.get(token.lower())
        if canonical:
            return canonical
        try:
            registry = axis_registry_tokens(axis_key)
        except Exception:
            registry = []
        for value in registry:
            if value and value.lower() == token.lower():
                return value
        return token

    def _canonical_persona_key_value(*aliases: str) -> str:
        for alias in aliases:
            candidate = str(alias or "").strip()
            if not candidate:
                continue
            if orchestrator:
                try:
                    canonical = orchestrator.canonical_persona_key(candidate)
                except Exception:
                    canonical = ""
                if canonical:
                    return canonical
            canonical = persona_aliases_lookup.get(candidate.lower())
            if canonical:
                return canonical
        return ""

    def _canonical_intent_key_value(*aliases: str) -> str:
        for alias in aliases:
            candidate = str(alias or "").strip()
            if not candidate:
                continue
            if orchestrator:
                try:
                    canonical = orchestrator.canonical_intent_key(candidate)
                except Exception:
                    canonical = ""
                if canonical:
                    return canonical
            lower = candidate.lower()
            canonical = intent_aliases_lookup.get(lower)
            if canonical:
                return canonical
            synonym = intent_synonyms_lookup.get(lower)
            if synonym:
                return synonym
        return ""

    axis_parts: list[str] = []
    if static_prompt:
        axis_parts.append(static_prompt)
    last_completeness = axis_join(
        axes_tokens, "completeness", getattr(GPTState, "last_completeness", "") or ""
    )
    last_scope = axis_join(
        axes_tokens, "scope", getattr(GPTState, "last_scope", "") or ""
    )
    last_method = axis_join(
        axes_tokens, "method", getattr(GPTState, "last_method", "") or ""
    )
    last_form = axis_join(axes_tokens, "form", getattr(GPTState, "last_form", "") or "")
    last_channel = axis_join(
        axes_tokens, "channel", getattr(GPTState, "last_channel", "") or ""
    )
    for value in (
        last_completeness,
        last_scope,
        last_method,
        last_form,
        last_channel,
    ):
        if value:
            axis_parts.append(value)

    persona_key_raw = str(recipe_snapshot.get("persona_preset_key") or "").strip()
    persona_label_raw = str(recipe_snapshot.get("persona_preset_label") or "").strip()
    persona_spoken_raw = str(recipe_snapshot.get("persona_preset_spoken") or "").strip()
    persona_voice = _canonical_axis_token(
        "voice", str(recipe_snapshot.get("persona_voice") or "")
    )
    persona_audience = _canonical_axis_token(
        "audience", str(recipe_snapshot.get("persona_audience") or "")
    )
    persona_tone = _canonical_axis_token(
        "tone", str(recipe_snapshot.get("persona_tone") or "")
    )
    persona_axes_bits = [
        bit for bit in (persona_voice, persona_audience, persona_tone) if bit
    ]
    persona_axes_compact = " · ".join(persona_axes_bits)
    persona_alias = (persona_spoken_raw or persona_label_raw or persona_key_raw).strip()

    canonical_persona = _canonical_persona_key_value(
        persona_alias,
        persona_spoken_raw,
        persona_label_raw,
        persona_key_raw,
    )
    if not canonical_persona:
        canonical_persona = persona_key_raw
    preset_for_persona = (
        persona_presets_lookup.get(canonical_persona) if canonical_persona else None
    )
    if (
        preset_for_persona is None
        and persona_presets_lookup
        and (persona_voice or persona_audience or persona_tone)
    ):
        voice_l = persona_voice.lower()
        audience_l = persona_audience.lower()
        tone_l = persona_tone.lower()
        for candidate in persona_presets_lookup.values():
            c_voice = (getattr(candidate, "voice", "") or "").lower()
            c_audience = (getattr(candidate, "audience", "") or "").lower()
            c_tone = (getattr(candidate, "tone", "") or "").lower()
            if c_voice and c_voice != voice_l:
                continue
            if c_audience and c_audience != audience_l:
                continue
            if c_tone and c_tone != tone_l:
                continue
            if not (c_voice or c_audience or c_tone):
                continue
            preset_for_persona = candidate
            canonical_persona = (
                getattr(candidate, "key", canonical_persona) or canonical_persona
            )
            break

    persona_display = persona_alias or canonical_persona
    if preset_for_persona is not None:
        fallback_display = (
            getattr(preset_for_persona, "spoken", None)
            or getattr(preset_for_persona, "label", None)
            or canonical_persona
        )
        fallback_display = str(fallback_display or "").strip()
        if fallback_display:
            persona_display = fallback_display

    persona_summary_line = ""
    if persona_display:
        descriptor = persona_display
        if (
            canonical_persona
            and descriptor
            and canonical_persona
            and descriptor.lower() != canonical_persona.lower()
        ):
            descriptor = f"{descriptor} ({canonical_persona})"
        persona_summary_line = descriptor
        if persona_axes_compact:
            persona_summary_line = f"{persona_summary_line} ({persona_axes_compact})"
    elif persona_axes_compact:
        persona_summary_line = persona_axes_compact

    intent_key_raw = str(recipe_snapshot.get("intent_preset_key") or "").strip()
    intent_label_raw = str(recipe_snapshot.get("intent_preset_label") or "").strip()
    intent_purpose_raw = str(recipe_snapshot.get("intent_purpose") or "").strip()
    intent_display = str(recipe_snapshot.get("intent_display") or "").strip()

    canonical_intent = _canonical_intent_key_value(
        intent_key_raw,
        intent_label_raw,
        intent_display,
        intent_purpose_raw,
    )
    if not canonical_intent and intent_purpose_raw:
        canonical_intent = (
            intent_synonyms_lookup.get(intent_purpose_raw.lower()) or intent_purpose_raw
        )

    intent_preset = (
        intent_presets_lookup.get(canonical_intent) if canonical_intent else None
    )
    if intent_preset is not None:
        canonical_intent = intent_preset.key or canonical_intent
        display_value = (
            intent_display_lookup.get(canonical_intent.lower())
            or intent_display_lookup.get((intent_preset.intent or "").lower())
            or (getattr(intent_preset, "label", "") or canonical_intent)
        )
        intent_display = display_value or intent_display
        if not intent_purpose_raw:
            intent_purpose_raw = intent_preset.intent or intent_purpose_raw
    else:
        if not canonical_intent:
            canonical_intent = intent_purpose_raw or intent_key_raw or intent_label_raw
        if not intent_display:
            intent_display = (
                intent_display_lookup.get((intent_purpose_raw or "").lower())
                or intent_display_lookup.get((intent_key_raw or "").lower())
                or intent_display_lookup.get((intent_label_raw or "").lower())
                or canonical_intent
                or ""
            )

    intent_summary_line = ""
    if intent_display:
        descriptor = intent_display
        if (
            canonical_intent
            and descriptor
            and descriptor.lower() != str(canonical_intent or "").lower()
        ):
            descriptor = f"{descriptor} ({canonical_intent})"
        intent_summary_line = descriptor
    elif canonical_intent:
        intent_summary_line = str(canonical_intent)

    hydrated_parts: list[str] = []
    if persona_summary_line:
        hydrated_parts.append(f"Persona: {persona_summary_line}")
    if intent_summary_line:
        hydrated_parts.append(f"Intent: {intent_summary_line}")

    recipe_tokens = " · ".join(axis_parts) if axis_parts else ""
    if recipe_tokens:
        recipe = recipe_tokens
    # If only static prompt is present but we have a legacy recipe, keep the legacy recipe
    # so older flows that only set last_recipe still show a full recap.
    if recipe_tokens and len(axis_parts) <= 1 and recipe_snapshot.get("recipe", ""):
        recipe = recipe_snapshot.get("recipe", "")
    if recipe:
        draw_text("Talon GPT Result", x, y)
        y += line_h
        draw_text("Prompt recap", x, y)
        y += line_h
        directional = recipe_snapshot.get("directional", "") or ""
        if directional:
            recipe_text = f"{recipe} · {directional}"
            grammar_phrase = suggestion_grammar_phrase(
                recipe_text, getattr(GPTState, "last_again_source", ""), {}
            )
        else:
            recipe_text = recipe
            grammar_phrase = suggestion_grammar_phrase(
                recipe_text, getattr(GPTState, "last_again_source", ""), {}
            )
        draw_text(f"Recipe: {recipe_text}", x, y)
        y += line_h
        draw_text(f"Say: {grammar_phrase}", x, y)
        y += line_h
        for line in stance_defaults_lines():
            for wrapped in _wrap_text(line):
                draw_text(wrapped, x, y)
                y += line_h
        draw_text(
            "Axes: single directional lens; form/channel singletons when used.",
            x,
            y,
        )
        y += line_h
        if persona_summary_line:
            for wrapped in _wrap_text(f"Persona: {persona_summary_line}"):
                draw_text(wrapped, x, y)
                y += line_h
        if intent_summary_line:
            for wrapped in _wrap_text(f"Intent: {intent_summary_line}"):
                draw_text(wrapped, x, y)
                y += line_h
        # Hydrated axis details stay hidden until the meta panel is expanded.
        last_completeness = axis_join(
            axes_tokens,
            "completeness",
            getattr(GPTState, "last_completeness", "") or "",
        )
        last_scope = axis_join(
            axes_tokens, "scope", getattr(GPTState, "last_scope", "") or ""
        )
        last_method = axis_join(
            axes_tokens, "method", getattr(GPTState, "last_method", "") or ""
        )
        last_form = axis_join(
            axes_tokens, "form", getattr(GPTState, "last_form", "") or ""
        )
        last_channel = axis_join(
            axes_tokens, "channel", getattr(GPTState, "last_channel", "") or ""
        )
        try:
            if any(
                (
                    last_completeness,
                    last_scope,
                    last_method,
                    last_form,
                    last_channel,
                    directional,
                )
            ):
                global _last_recap_log
                snapshot = (
                    static_prompt,
                    last_completeness,
                    last_scope,
                    last_method,
                    last_form,
                    last_channel,
                    directional,
                )
                if snapshot != _last_recap_log:
                    _debug(
                        "recap state "
                        f"static={static_prompt!r} C={last_completeness!r} "
                        f"S={last_scope!r} M={last_method!r} "
                        f"F={last_form!r} Ch={last_channel!r} D={directional!r}"
                    )
                    _last_recap_log = snapshot
        except Exception:
            pass
        if last_completeness:
            hydrated_parts.append(
                f"C: {_hydrate_axis('completeness', last_completeness)}"
            )
        if last_scope:
            hydrated_parts.append(f"S: {_hydrate_axis('scope', last_scope)}")
        if last_method:
            hydrated_parts.append(f"M: {_hydrate_axis('method', last_method)}")
        if last_form:
            hydrated_parts.append(f"F: {_hydrate_axis('form', last_form)}")
        if last_channel:
            hydrated_parts.append(f"Ch: {_hydrate_axis('channel', last_channel)}")

    # Optional diagnostic meta section and toggle under the recap.
    meta = recap_snapshot.get("meta", "").strip()
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
    # Keep meta compact: show interpretation and hydrated axes, but omit the
    # full prompt to avoid duplicating the model's own interpretation recap.
    meta_content = bool(meta or hydrated_parts)

    if meta_content and rect is not None:
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
    if ResponseCanvasState.meta_expanded and meta_content:
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
            int(
                (rect.width - (detail_x - (rect.x if rect else 0)) - 40)
                // approx_char_width
            ),
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

        if hydrated_parts:
            details_text = " · ".join(hydrated_parts)
            label = "Stance details"
            for wrapped in _wrap_meta(f"{label}: {details_text}"):
                draw_text(wrapped, detail_x, y)
                y += line_h
            y += line_h // 2

        if parsed_meta:
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
        meta_content
        and rect is not None
        and meta_region_top is not None
        and meta_region_bottom is None
    ):
        # Meta was present but not expanded; treat just the band as clickable.
        meta_region_bottom = y
    if (
        meta_content
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

    # Body: scrollable answer text. While inflight on a canvas-progress
    # destination, prefer the streaming buffer and avoid showing stale
    # last_response content.
    streaming_snapshot = getattr(GPTState, "last_streaming_snapshot", {}) or {}
    streaming_adapter = None
    try:
        from . import streamingCoordinator as _streaming_coordinator

        streaming_adapter = getattr(
            _streaming_coordinator, "canvas_view_from_snapshot", None
        )
    except Exception:
        streaming_adapter = None
    streaming_text = _coerce_text(streaming_snapshot.get("text", ""))
    streaming_error_message = _coerce_text(streaming_snapshot.get("error_message", ""))
    streaming_completed = bool(streaming_snapshot.get("completed"))
    streaming_errored = bool(streaming_snapshot.get("errored"))
    if streaming_adapter is not None and streaming_snapshot:
        try:
            snapshot_view = streaming_adapter(streaming_snapshot) or {}
            streaming_text = _coerce_text(snapshot_view.get("text", streaming_text))
            streaming_error_message = _coerce_text(
                snapshot_view.get("error_message", streaming_error_message)
            )
            status = str(snapshot_view.get("status") or "")
            streaming_completed = streaming_completed or status == "completed"
            streaming_errored = streaming_errored or status == "errored"
        except Exception:
            pass

    text_to_confirm_raw = getattr(GPTState, "text_to_confirm", "")
    text_to_confirm = _coerce_text(text_to_confirm_raw)
    last_response = _coerce_text(recap_snapshot.get("response", ""))

    # Use the same text pipeline for streaming and final views by preferring
    # the confirmation text (which has already gone through meta/markdown
    # splitting) when available. Fall back to the last recorded response and
    # then, as a last resort, the raw streaming text.
    if text_to_confirm:
        answer = text_to_confirm
    elif last_response:
        answer = last_response
    else:
        answer = streaming_text

    # Limit debug logging to inflight progress draws; stay silent on DONE/IDLE.
    # Debug logging silenced for steady state; re-enable selectively when needed.
    if not answer:
        if prefer_progress:
            if phase is RequestPhase.SENDING:
                draw_text("Waiting for model response (sending)…", x, y)
                return
            if phase is RequestPhase.STREAMING:
                # If no streaming snapshot yet, show any cached append text.
                try:
                    req_id = getattr(GPTState, "last_request_id", "")
                except Exception:
                    req_id = ""
                cached = fallback_for(req_id)
                if cached:
                    answer = cached
                else:
                    draw_text("Streaming… awaiting first chunk", x, y)
                    return
            if phase is RequestPhase.CANCELLED:
                draw_text("Cancel requested; waiting for model to stop…", x, y)
                return
        if streaming_errored and streaming_error_message:
            draw_text(f"Streaming error: {streaming_error_message}", x, y)
            return
        draw_text("No last response available.", x, y)
        return

    visible_height = body_bottom - body_top
    # Simple line-based scrolling: normalise answer into display lines,
    # including basic bullet formatting, wrapping, and blank-line compression.
    approx_char_width = 8
    max_chars = max(int((rect.width - 80) // approx_char_width), 40) if rect else 80

    cache_key = (answer, max_chars)
    lines_cache_key = getattr(ResponseCanvasState, "lines_cache_key", None)
    cached_lines = getattr(ResponseCanvasState, "lines_cache", None)
    cache_miss = lines_cache_key != cache_key or not cached_lines
    wrap_duration_ms = 0.0
    wrap_started = time.perf_counter()
    if cache_miss:
        lines = _format_answer_lines(answer, max_chars)
        ResponseCanvasState.lines_cache_key = cache_key
        ResponseCanvasState.lines_cache = list(lines)
        wrap_duration_ms = (time.perf_counter() - wrap_started) * 1000.0
    else:
        lines = cached_lines or []
    if not lines:
        lines = [""]

    # Compute content height and clamp scroll offset so we cannot scroll past
    # the end of the content.
    content_height = len(lines) * line_h
    max_scroll = max(content_height - visible_height, 0)
    scroll_y = clamp_scroll(ResponseCanvasState.scroll_y, max_scroll)
    ResponseCanvasState.scroll_y = scroll_y
    start_index = int(scroll_y // line_h)
    offset_y = body_top - (scroll_y % line_h)

    draw_started = time.perf_counter()
    drawn_lines = 0
    for idx in range(start_index, len(lines)):
        ly = offset_y + (idx - start_index) * line_h
        if ly > body_bottom:
            break
        line_text = lines[idx] or " "
        drawn_lines += 1
        # Prefer an emoji-aware draw helper so runs containing emoji can use
        # a more compatible typeface when available, while keeping layout
        # consistent with the existing fixed-width assumptions.
        try:
            draw_text_with_emoji_fallback(
                c,
                line_text,
                x,
                ly,
                approx_char_width=approx_char_width,
            )
        except Exception:
            # Fallback to a simple draw if anything goes wrong.
            draw_text(line_text, x, ly)
    draw_duration_ms = (time.perf_counter() - draw_started) * 1000.0

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
            thumb_height = max(
                int(visible_height * visible_height / content_height), 20
            )
            if max_scroll > 0:
                thumb_offset = int(
                    (scroll_y / max_scroll) * (visible_height - thumb_height)
                )
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

    _trace_canvas_event(
        "draw_stats",
        lines_total=f"{len(lines)}",
        lines_drawn=f"{drawn_lines}",
        scroll_y=f"{round(float(scroll_y), 2)}",
        max_scroll=f"{round(float(max_scroll), 2)}",
        cache_miss=f"{cache_miss}",
        wrap_ms=f"{round(wrap_duration_ms, 3)}",
        draw_ms=f"{round(draw_duration_ms, 3)}",
    )

    # Record max_scroll for event handlers that clamp scroll offsets.
    ResponseCanvasState.max_scroll = max_scroll

    # Footer buttons. We intentionally do not clear _response_button_bounds
    # here so that the header meta toggle bounds remain registered; the
    # bounds map was cleared at the start of this draw.
    footer_y = body_bottom + line_h // 2
    btn_labels = [
        ("paste", "[Paste response]"),
        ("copy", "[Copy response]"),
        ("discard", "[Discard response]"),
        ("context", "[Pass to context]"),
        ("query", "[Pass to query]"),
        ("thread", "[Pass to thread]"),
        ("browser", "[Open browser]"),
        ("analyze", "[Analyze prompt]"),
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
        if _response_hover_button == key and rect is not None and paint is not None:
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
    def model_response_canvas_refresh():
        """Force a redraw of the response canvas if it is showing."""
        if _guard_response_canvas(allow_inflight=True):
            return
        if _response_canvas is None:
            return
        try:
            restore_meta_expanded = ResponseCanvasState.meta_expanded
            restore_meta_pinned = ResponseCanvasState.meta_pinned_request_id
            ResponseCanvasState.suppress_hide_reset = True
            _response_canvas.show()
            ResponseCanvasState.showing = True
            ResponseCanvasState.meta_expanded = restore_meta_expanded
            ResponseCanvasState.meta_pinned_request_id = restore_meta_pinned
            try:
                GPTState.suppress_response_canvas_close = True
            except Exception:
                pass
        except Exception:
            pass
        finally:
            ResponseCanvasState.suppress_hide_reset = False

    def model_response_canvas_open():
        """Open the canvas-based response viewer for the last model answer (idempotent)."""
        state = _current_request_state()
        prefer_progress = _prefer_canvas_progress()
        inflight = state.phase in (
            RequestPhase.SENDING,
            RequestPhase.STREAMING,
            RequestPhase.CANCELLED,
        )
        if _guard_response_canvas(allow_inflight=inflight):
            return
        if not inflight and not (
            getattr(GPTState, "last_response", "")
            or getattr(GPTState, "text_to_confirm", "")
        ):
            return
        _capture_previous_focus()
        close_common_overlays(actions.user, exclude={"model_response_canvas_close"})
        canvas_obj = _ensure_response_canvas()
        if ResponseCanvasState.showing:
            return
        ResponseCanvasState.showing = True
        _trace_canvas_event(
            "canvas_open",
            inflight=inflight,
            prefer_progress=prefer_progress,
            phase=str(getattr(state, "phase", None)),
            destination=getattr(GPTState, "current_destination_kind", None),
        )
        try:
            ctx.tags = ["user.model_window_open"]
        except Exception:
            pass
        try:
            GPTState.response_canvas_showing = True
        except Exception:
            pass
        try:
            from .pillCanvas import hide_pill  # type: ignore circular

            hide_pill()
        except Exception:
            pass
        ResponseCanvasState.scroll_y = 0.0
        ResponseCanvasState.max_scroll = 1e9
        ResponseCanvasState.lines_cache_key = None
        ResponseCanvasState.lines_cache = None
        # Always start with meta collapsed; the band still shows a short
        # summary so the initial view is response-first.
        ResponseCanvasState.meta_expanded = False
        ResponseCanvasState.meta_pinned_request_id = ""
        try:
            GPTState.suppress_response_canvas_close = True
        except Exception:
            pass
        canvas_obj.show()

    def model_response_canvas_toggle():
        """Toggle the canvas-based response viewer open/closed."""
        if _guard_response_canvas(allow_inflight=True):
            return
        canvas_obj = _ensure_response_canvas()
        state = None
        if ResponseCanvasState.showing:
            _log_canvas_close("toggle close")
            try:
                ResponseCanvasState.last_close_event = time.time()
            except Exception:
                pass
            ResponseCanvasState.showing = False
            try:
                setattr(GPTState, "response_canvas_manual_close", True)
            except Exception:
                pass

            try:
                GPTState.response_canvas_showing = False
            except Exception:
                pass
            ResponseCanvasState.scroll_y = 0.0
            ResponseCanvasState.max_scroll = 1e9
            ResponseCanvasState.lines_cache_key = None
            ResponseCanvasState.lines_cache = None
            ResponseCanvasState.meta_expanded = False
            ResponseCanvasState.meta_pinned_request_id = ""
            try:
                canvas_obj.hide()
            except Exception:
                pass
            try:
                clear_response_fallback(getattr(GPTState, "last_request_id", None))
            except Exception:
                pass
            try:
                GPTState.suppress_response_canvas_close = False
            except Exception:
                pass
            try:
                ctx.tags = []
            except Exception:
                pass
            try:
                state = _current_request_state()
            except Exception:
                state = None
            _restore_previous_focus()
        else:
            _capture_previous_focus()
            close_common_overlays(
                actions.user, exclude={"model_response_canvas_close"}, passive=True
            )

            try:
                setattr(GPTState, "response_canvas_manual_close", False)
            except Exception:
                pass

            ResponseCanvasState.showing = True
            try:
                ctx.tags = ["user.model_window_open"]
            except Exception:
                pass
            try:
                GPTState.response_canvas_showing = True
            except Exception:
                pass
            ResponseCanvasState.scroll_y = 0.0
            ResponseCanvasState.max_scroll = 1e9
            ResponseCanvasState.lines_cache_key = None
            ResponseCanvasState.lines_cache = None
            ResponseCanvasState.meta_expanded = False
            ResponseCanvasState.meta_pinned_request_id = ""
            try:
                GPTState.suppress_response_canvas_close = True
            except Exception:
                pass
            canvas_obj.show()

        if state and getattr(state, "phase", None) in (
            RequestPhase.SENDING,
            RequestPhase.STREAMING,
        ):
            try:
                from .pillCanvas import show_pill  # type: ignore circular

                phase_label = (
                    "Model: sending…"
                    if state.phase is RequestPhase.SENDING
                    else "Model: streaming…"
                )
                show_pill(phase_label, state.phase)
            except Exception:
                pass

    def model_response_canvas_close():
        """Explicitly close the response viewer"""
        _trace_canvas_event(
            "canvas_close.begin",
            showing=getattr(ResponseCanvasState, "showing", False),
            destination=getattr(GPTState, "current_destination_kind", None),
        )
        if _guard_response_canvas(allow_inflight=True):
            return
        try:
            setattr(GPTState, "response_canvas_manual_close", True)
        except Exception:
            pass
        if _response_canvas is None:
            _log_canvas_close("close w/o canvas")
            ResponseCanvasState.showing = False
            try:
                setattr(GPTState, "response_canvas_manual_close", True)
            except Exception:
                pass
            try:
                ctx.tags = []
            except Exception:
                pass
            _restore_previous_focus()
            return
        try:
            clear_response_fallback(getattr(GPTState, "last_request_id", None))
        except Exception:
            pass
        _log_canvas_close("explicit close")
        ResponseCanvasState.showing = False
        try:
            ctx.tags = []
        except Exception:
            pass
        try:
            GPTState.response_canvas_showing = False
        except Exception:
            pass
        ResponseCanvasState.scroll_y = 0.0
        ResponseCanvasState.max_scroll = 1e9
        ResponseCanvasState.lines_cache_key = None
        ResponseCanvasState.lines_cache = None
        ResponseCanvasState.meta_expanded = False
        ResponseCanvasState.meta_pinned_request_id = ""
        try:
            _response_canvas.hide()
        except Exception:
            pass
        try:
            GPTState.suppress_response_canvas_close = False
        except Exception:
            pass
        try:
            state = _current_request_state()
        except Exception:
            state = None
        _restore_previous_focus()
        if state and getattr(state, "phase", None) in (
            RequestPhase.SENDING,
            RequestPhase.STREAMING,
        ):
            try:
                from .pillCanvas import show_pill  # type: ignore circular

                phase_label = (
                    "Model: sending…"
                    if state.phase is RequestPhase.SENDING
                    else "Model: streaming…"
                )
                show_pill(phase_label, state.phase)
            except Exception:
                pass
        _trace_canvas_event(
            "canvas_close.end",
            showing=getattr(ResponseCanvasState, "showing", False),
            destination=getattr(GPTState, "current_destination_kind", None),
            phase=str(getattr(state, "phase", None)),
        )
