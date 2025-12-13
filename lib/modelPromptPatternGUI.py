from dataclasses import dataclass
import os
from typing import Dict, Literal, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

from .canvasFont import apply_canvas_typeface

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState
from .axisMappings import axis_docs_map
from .requestBus import current_state
from .requestState import RequestPhase
from .modelHelpers import notify

try:
    # Prefer the shared static prompt domain helpers when available.
    from .staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile
except ImportError:  # Talon may have an older module state cached
    from .staticPromptConfig import STATIC_PROMPT_CONFIG

    def get_static_prompt_profile(name: str):
        return STATIC_PROMPT_CONFIG.get(name)

    def get_static_prompt_axes(name: str) -> dict[str, object]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, object] = {}
        for axis in ("completeness", "scope", "method", "form", "channel"):
            value = profile.get(axis)
            if not value:
                continue
            if axis == "completeness":
                axes[axis] = str(value)
            else:
                if isinstance(value, list):
                    tokens = [str(v).strip() for v in value if str(v).strip()]
                else:
                    tokens = [str(value).strip()]
                if tokens:
                    axes[axis] = tokens
        return axes


from .talonSettings import (
    ApplyPromptConfiguration,
    _canonicalise_axis_tokens,
    modelPrompt,
    safe_model_prompt,
)

mod = Module()
ctx = Context()
mod.tag(
    "model_prompt_pattern_window_open",
    desc="Tag for enabling prompt-specific pattern commands when the prompt pattern picker is open",
)


PatternDomain = Literal["prompt"]


class PromptPatternGUIState:
    static_prompt: Optional[str] = None


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


@dataclass(frozen=True)
class PromptAxisPattern:
    name: str
    description: str
    completeness: str
    scope: str
    method: str
    form: str
    channel: str
    directional: str


class PromptPatternCanvasState:
    """State specific to the canvas-based prompt pattern picker."""

    showing: bool = False
    scroll_y: float = 0.0
    max_scroll: float = 0.0


_prompt_pattern_canvas: Optional[canvas.Canvas] = None
_prompt_pattern_handlers_registered: bool = False
_prompt_pattern_button_bounds: Dict[str, Tuple[int, int, int, int]] = {}
_prompt_pattern_hover_close: bool = False
_prompt_pattern_hover_name: Optional[str] = None
_prompt_pattern_drag_offset: Optional[Tuple[float, float]] = None
_prompt_pattern_dragging: bool = False

_PANEL_WIDTH = 720
_PANEL_HEIGHT = 600

try:  # Talon runtime
    from talon.types import Rect
except Exception:  # Tests / stubs

    class Rect:  # type: ignore[override]
        def __init__(self, x: float, y: float, width: float, height: float):
            self.x = x
            self.y = y
            self.width = width
            self.height = height


def _load_axis_map(filename: str) -> dict[str, str]:
    """Load axis descriptions from the shared axis mapping SSOT."""
    axis = filename.replace("Modifier.talon-list", "").replace(".talon-list", "")
    axis_key = {
        "completeness": "completeness",
        "scope": "scope",
        "method": "method",
        "form": "form",
        "channel": "channel",
        "directional": "directional",
    }.get(axis, "")
    if not axis_key:
        return {}
    return axis_docs_map(axis_key)


def _axis_value(token: str, mapping: dict[str, str]) -> str:
    """Map a short token (e.g. 'gist') to its full description, if available."""
    if not token:
        return ""
    return mapping.get(token, token)


def _debug(msg: str) -> None:
    """Lightweight debug logging for the prompt pattern canvas."""
    try:
        print(f"GPT prompt pattern canvas: {msg}")
    except Exception:
        pass


COMPLETENESS_MAP = _load_axis_map("completenessModifier.talon-list")
SCOPE_MAP = _load_axis_map("scopeModifier.talon-list")
METHOD_MAP = _load_axis_map("methodModifier.talon-list")
FORM_MAP = _load_axis_map("formModifier.talon-list")
CHANNEL_MAP = _load_axis_map("channelModifier.talon-list")
DIRECTIONAL_MAP = _load_axis_map("directionalModifier.talon-list")


PROMPT_PRESETS: list[PromptAxisPattern] = [
    PromptAxisPattern(
        name="Quick gist",
        description="Short, focused summary of the main points.",
        completeness="gist",
        scope="focus",
        method="",
        form="plain",
        channel="",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Deep narrow rigor",
        description="Thorough, narrow analysis with explicit reasoning.",
        completeness="full",
        scope="narrow",
        method="rigor",
        form="plain",
        channel="",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Bulleted summary",
        description="Compact bullet-point summary for quick scanning.",
        completeness="gist",
        scope="focus",
        method="",
        form="bullets",
        channel="",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Abstraction ladder",
        description="Place the focal problem in the middle, with reasons above and consequences below.",
        completeness="full",
        scope="focus",
        method="ladder",
        form="plain",
        channel="",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Cluster items",
        description="Group related items into labeled categories; clustered output only.",
        completeness="full",
        scope="narrow",
        method="cluster",
        form="plain",
        channel="",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Rank items",
        description="Sort items in order of importance to the audience.",
        completeness="full",
        scope="narrow",
        method="prioritize",
        form="plain",
        channel="",
        directional="fog",
    ),
]


def _ensure_prompt_pattern_canvas() -> canvas.Canvas:
    """Create the prompt pattern canvas if needed and register handlers."""
    global _prompt_pattern_canvas, _prompt_pattern_handlers_registered
    if _prompt_pattern_canvas is not None and _prompt_pattern_handlers_registered:
        return _prompt_pattern_canvas

    screen = ui.main_screen()
    try:
        screen_x = getattr(screen, "x", 0)
        screen_y = getattr(screen, "y", 0)
        screen_width = getattr(screen, "width", _PANEL_WIDTH + 80)
        screen_height = getattr(screen, "height", _PANEL_HEIGHT + 80)
        margin_x = 40
        margin_y = 40

        panel_width = min(_PANEL_WIDTH, max(screen_width - 2 * margin_x, 480))
        panel_height = min(_PANEL_HEIGHT, max(screen_height - 2 * margin_y, 360))

        start_x = screen_x + max((screen_width - panel_width) // 2, margin_x)
        start_y = screen_y + max((screen_height - panel_height) // 2, margin_y)
        rect = Rect(start_x, start_y, panel_width, panel_height)
        # Mirror the plain pattern canvas creation: from_rect + blocks_mouse.
        _prompt_pattern_canvas = canvas.Canvas.from_rect(rect)
        try:
            _prompt_pattern_canvas.blocks_mouse = True
            # Some runtimes expose block_mouse instead; set both to be safe.
            if hasattr(_prompt_pattern_canvas, "block_mouse"):
                _prompt_pattern_canvas.block_mouse = True  # type: ignore[attr-defined]
        except Exception:
            pass
        _prompt_pattern_handlers_registered = False
    except Exception:
        _prompt_pattern_canvas = canvas.Canvas.from_screen(screen)
        _prompt_pattern_handlers_registered = False

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_prompt_patterns(c)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot, pattern selection, hover, and drag (mirrors response canvas)."""
        try:
            global \
                _prompt_pattern_hover_close, \
                _prompt_pattern_hover_name, \
                _prompt_pattern_drag_offset, \
                _prompt_pattern_dragging, \
                _mouse_log_count
            _mouse_log_count = globals().get("_mouse_log_count", 0)
            rect = getattr(_prompt_pattern_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if pos is None and rect is not None:
                gp = getattr(evt, "gpos", None)
                if gp is not None:

                    class _Local:
                        def __init__(self, x: float, y: float):
                            self.x = x
                            self.y = y

                    pos = _Local(gp.x - rect.x, gp.y - rect.y)
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
                _prompt_pattern_hover_close = (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                )
                hover_name: Optional[str] = None
                for key, (bx1, by1, bx2, by2) in list(
                    _prompt_pattern_button_bounds.items()
                ):
                    if bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2:
                        hover_name = key
                        break
                _prompt_pattern_hover_name = hover_name

            # Handle close click and drag start.
            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Close hotspot in top-right header band.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    actions.user.prompt_pattern_gui_close()
                    _prompt_pattern_drag_offset = None
                    _prompt_pattern_dragging = False
                    return

                # Pattern buttons.
                for key, (bx1, by1, bx2, by2) in list(
                    _prompt_pattern_button_bounds.items()
                ):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    if not PromptPatternGUIState.static_prompt:
                        return
                    name = key
                    for pattern in PROMPT_PRESETS:
                        if pattern.name == name:
                            _run_prompt_pattern(
                                PromptPatternGUIState.static_prompt, pattern
                            )
                            break
                    return

                # Start drag anywhere else.
                _prompt_pattern_drag_offset = (gpos.x - rect.x, gpos.y - rect.y)
                _prompt_pattern_dragging = True
                return

            # End drag on mouse up.
            if event_type in ("mouseup", "mouse_up"):
                _prompt_pattern_drag_offset = None
                _prompt_pattern_dragging = False
                return

            # Drag while moving (include mouse_drag).
            if (
                event_type in ("mousemove", "mouse_move", "mouse_drag")
                and _prompt_pattern_drag_offset is not None
            ):
                dx, dy = _prompt_pattern_drag_offset
                new_x = gpos.x - dx
                new_y = gpos.y - dy
                try:
                    _prompt_pattern_canvas.move(new_x, new_y)
                except Exception:
                    _prompt_pattern_drag_offset = None
                    _prompt_pattern_dragging = False
        except Exception as e:
            try:
                _debug(f"mouse handler error: {e}")
            except Exception:
                pass
            return
        finally:
            try:
                _mouse_log_count = _mouse_log_count + 1
                globals()["_mouse_log_count"] = _mouse_log_count
            except Exception:
                pass

    def _on_scroll(evt) -> None:  # pragma: no cover - visual only
        """Handle high-level scroll events (pixels/degrees) for prompt patterns."""
        try:
            rect = getattr(_prompt_pattern_canvas, "rect", None)
            if rect is None:
                return
            raw = None
            pixels = getattr(evt, "pixels", None)
            degrees = getattr(evt, "degrees", None)
            dy = getattr(evt, "dy", None)
            delta_y = getattr(evt, "delta_y", None)
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
            if not raw:
                return
            max_scroll = max(PromptPatternCanvasState.max_scroll, 0.0)
            new_scroll = PromptPatternCanvasState.scroll_y - raw * 40.0
            PromptPatternCanvasState.scroll_y = max(min(new_scroll, max_scroll), 0.0)
            try:
                _prompt_pattern_canvas.show()
            except Exception:
                pass
        except Exception:
            return

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = getattr(evt, "key", "") or ""
            if key.lower() in ("escape", "esc"):
                actions.user.prompt_pattern_gui_close()
        except Exception:
            return

    def _register_handlers() -> None:
        """Register all prompt pattern canvas handlers exactly once."""
        global _prompt_pattern_handlers_registered
        if _prompt_pattern_handlers_registered or _prompt_pattern_canvas is None:
            return
        try:
            _prompt_pattern_canvas.register("draw", _on_draw)
        except Exception:
            _debug("draw handler registration failed for prompt pattern canvas")
        for evt_name in ("mouse", "mouse_move", "mouse_drag"):
            try:
                _prompt_pattern_canvas.register(evt_name, _on_mouse)
            except Exception:
                _debug(
                    f"mouse handler registration failed for prompt pattern canvas ({evt_name})"
                )
        for evt_name in ("scroll", "wheel", "mouse_scroll"):
            try:
                _prompt_pattern_canvas.register(evt_name, _on_scroll)
            except Exception:
                _debug(
                    f"prompt pattern scroll handler registration failed for '{evt_name}'"
                )
        try:
            _prompt_pattern_canvas.register("key", _on_key)
        except Exception:
            _debug("key handler registration failed for prompt pattern canvas")
        _prompt_pattern_handlers_registered = True

    _register_handlers()

    return _prompt_pattern_canvas


def _open_prompt_pattern_canvas(static_prompt: str) -> None:
    canvas_obj = _ensure_prompt_pattern_canvas()
    PromptPatternGUIState.static_prompt = static_prompt
    PromptPatternCanvasState.showing = True
    PromptPatternCanvasState.scroll_y = 0.0
    # Reset per-show debug counters and drag state.
    globals()["_mouse_log_count"] = 0
    globals()["_mouse_experiment_count"] = 0
    globals()["_prompt_pattern_drag_offset"] = None
    globals()["_prompt_pattern_dragging"] = False
    try:
        setattr(canvas_obj, "_trace_count", 0)
    except Exception:
        pass
    canvas_obj.show()


def _close_prompt_pattern_canvas() -> None:
    global \
        _prompt_pattern_canvas, \
        _prompt_pattern_hover_close, \
        _prompt_pattern_hover_name
    PromptPatternCanvasState.showing = False
    _prompt_pattern_hover_close = False
    _prompt_pattern_hover_name = None
    if _prompt_pattern_canvas is None:
        return
    try:
        _prompt_pattern_canvas.hide()
    except Exception:
        pass


def _draw_prompt_patterns(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        return

    _prompt_pattern_button_bounds.clear()

    paint = getattr(c, "paint", None)
    if paint is not None:
        apply_canvas_typeface(
            paint,
            settings_key="user.model_response_canvas_typeface",
            cache_key="prompt_patterns",
        )

    if rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            paint.color = "FFFFFF"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(rect)
            # Subtle outline so the canvas reads as a coherent panel.
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.STROKE
            paint.color = "C0C0C0"
            c.draw_rect(
                Rect(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1)
            )
            if old_style is not None:
                paint.style = old_style
            paint.color = old_color or "000000"
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    if rect is not None and hasattr(rect, "x") and hasattr(rect, "y"):
        x = rect.x + 40
        y = rect.y + 60
    else:
        x = 40
        y = 60
    line_h = 18
    approx_char = 8

    draw_text("Prompt patterns", x, y)
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * approx_char) - 16
        draw_text(close_label, close_x, close_y)
        if paint is not None and _prompt_pattern_hover_close:
            try:
                underline_rect = Rect(
                    close_x, close_y + 4, len(close_label) * approx_char, 1
                )
                c.draw_rect(underline_rect)
            except Exception:
                pass
    y += line_h

    static_prompt = PromptPatternGUIState.static_prompt
    if not static_prompt:
        draw_text("No static prompt selected.", x, y)
        return

    draw_text(f"Prompt: {static_prompt}", x, y)
    y += line_h
    profile = get_static_prompt_profile(static_prompt)
    description = profile["description"] if profile is not None else None
    if description:
        draw_text(description, x, y)
        y += line_h * 2

    axes: list[str] = []
    profile_axes = get_static_prompt_axes(static_prompt)
    for label in ("completeness", "scope", "method", "form", "channel"):
        value = profile_axes.get(label)
        if not value:
            continue
        if isinstance(value, list):
            rendered = " ".join(str(v) for v in value)
        else:
            rendered = str(value)
        if rendered:
            axes.append(f"{label.capitalize()}: {rendered}")
    if axes:
        draw_text("Profile defaults:", x, y)
        y += line_h
        for line in axes:
            draw_text(f"  {line}", x, y)
            y += line_h
        y += line_h

    draw_text("Grammar template:", x, y)
    y += line_h
    draw_text(
        f"  model run {static_prompt} [completeness] [scope] [scope] [method] [method] [method] [form] [channel] <directional lens>",
        x,
        y,
    )
    y += line_h * 2

    draw_text("Patterns for this prompt:", x, y)
    y += line_h * 2

    # Scrollable list of presets (flat line-based rendering).
    if rect is not None and hasattr(rect, "height"):
        body_top = y
        body_bottom = rect.y + rect.height - line_h * 3
    else:
        body_top = y
        body_bottom = y + line_h * len(PROMPT_PRESETS) * 6
    visible_height = max(body_bottom - body_top, line_h * 6)

    def _wrap(text: str, max_chars: int) -> list[str]:
        if max_chars <= 0:
            return [text]
        words = text.split()
        lines: list[str] = []
        current: list[str] = []
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
        return lines or [text]

    max_chars = max(int((rect.width - 80) // max(approx_char, 6)), 18) if rect else 60

    # Build a flat list of drawable lines with heights.
    flat_lines: list[tuple[str, int, str]] = []
    for pat in PROMPT_PRESETS:
        recipe_tokens = [static_prompt]
        for token in (
            pat.completeness,
            pat.scope,
            pat.method,
            pat.form,
            pat.channel,
            pat.directional,
        ):
            if token:
                recipe_tokens.append(token)
        recipe_str = " · ".join(recipe_tokens)
        say_line = f"Say (grammar): model {recipe_str.replace(' · ', ' ')}"
        flat_lines.append((f"[{pat.name}]", line_h, "name"))
        for section, kind in (
            (recipe_str, "recipe"),
            (say_line, "say"),
            (pat.description, "desc"),
        ):
            for wrapped in _wrap(section, max_chars):
                flat_lines.append((wrapped, line_h, kind))
        flat_lines.append(("", line_h, "spacer"))

    total_content_height = sum(h for _, h, _ in flat_lines)
    max_scroll = max(total_content_height - visible_height, 0)
    scroll_y = max(min(PromptPatternCanvasState.scroll_y, max_scroll), 0)
    PromptPatternCanvasState.scroll_y = scroll_y
    PromptPatternCanvasState.max_scroll = max_scroll

    # Render visible lines only.
    cursor_y = body_top - scroll_y
    idx = 0
    while idx < len(flat_lines) and cursor_y + flat_lines[idx][1] < body_top:
        cursor_y += flat_lines[idx][1]
        idx += 1
    current_pattern = None
    for text_line, height, kind in flat_lines[idx:]:
        if cursor_y > body_bottom:
            break
        if kind == "name":
            current_pattern = text_line.strip("[]")
            draw_text(text_line, x, cursor_y)
            _prompt_pattern_button_bounds[current_pattern] = (
                x,
                cursor_y - line_h,
                x + len(text_line) * approx_char,
                cursor_y + line_h,
            )
            if (
                _prompt_pattern_hover_name == current_pattern
                and rect is not None
                and paint is not None
            ):
                try:
                    underline_rect = Rect(
                        x, cursor_y + 4, len(text_line) * approx_char, 1
                    )
                    c.draw_rect(underline_rect)
                except Exception:
                    pass
        elif kind in ("recipe", "say", "desc"):
            draw_text(text_line, x, cursor_y)
        cursor_y += height

    # Draw a simple scrollbar when needed.
    if max_scroll > 0 and rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            track_x = rect.x + rect.width - 12
            track_y = body_top
            track_height = visible_height
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.STROKE
            paint.color = "DDDDDD"
            c.draw_rect(Rect(track_x, track_y, 6, track_height))
            thumb_height = max(
                int(visible_height * visible_height / total_content_height), 20
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
                Rect(track_x + 1, track_y + thumb_offset + 1, 4, thumb_height - 2)
            )
            if old_style is not None and hasattr(paint, "Style"):
                paint.style = old_style
            if old_color is not None:
                paint.color = old_color
        except Exception:
            pass

    draw_text(
        "Tip: Say 'close pattern menu' to close this menu.", x, body_bottom + line_h
    )


def _run_prompt_pattern(static_prompt: str, pattern: PromptAxisPattern) -> None:
    """Execute a prompt-specific axis pattern as if spoken via the model grammar."""
    actions.app.notify(f"Running prompt pattern: {static_prompt} · {pattern.name}")

    # Enforce axis caps and single directional lens for prompt patterns.
    canonical_scope = _canonicalise_axis_tokens("scope", pattern.scope.split())
    canonical_method = _canonicalise_axis_tokens("method", pattern.method.split())
    canonical_form = _canonicalise_axis_tokens("form", pattern.form.split())
    canonical_channel = _canonicalise_axis_tokens("channel", pattern.channel.split())
    canonical_directional = _canonicalise_axis_tokens(
        "directional", pattern.directional.split()
    )
    if not canonical_directional:
        notify("GPT: prompt pattern is missing a directional lens; skipping.")
        return

    class Match:
        pass

    match = Match()
    setattr(match, "staticPrompt", static_prompt)
    if pattern.completeness:
        setattr(
            match,
            "completenessModifier",
            _axis_value(pattern.completeness, COMPLETENESS_MAP),
        )
    canonical_scope_str = " ".join(canonical_scope)
    canonical_method_str = " ".join(canonical_method)
    canonical_form_str = " ".join(canonical_form)
    canonical_channel_str = " ".join(canonical_channel)
    canonical_directional_str = " ".join(canonical_directional)
    if canonical_scope:
        setattr(match, "scopeModifier", _axis_value(canonical_scope_str, SCOPE_MAP))
    if canonical_method:
        setattr(match, "methodModifier", _axis_value(canonical_method_str, METHOD_MAP))
    if canonical_form:
        setattr(match, "formModifier", _axis_value(canonical_form_str, FORM_MAP))
    if canonical_channel:
        setattr(
            match,
            "channelModifier",
            _axis_value(canonical_channel_str, CHANNEL_MAP),
        )
    if canonical_directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(canonical_directional_str, DIRECTIONAL_MAP),
        )

    please_prompt = safe_model_prompt(match)
    if not please_prompt:
        return

    config = ApplyPromptConfiguration(
        please_prompt=please_prompt,
        model_source=create_model_source(settings.get("user.model_default_source")),
        additional_model_source=None,
        model_destination=create_model_destination(
            settings.get("user.model_default_destination")
        ),
    )

    actions.user.gpt_apply_prompt(config)

    # Keep last_recipe concise and token-based to reinforce speakable grammar.
    recipe_parts = [static_prompt]
    if pattern.completeness:
        recipe_parts.append(pattern.completeness)
    for tokens in (
        canonical_scope,
        canonical_method,
        canonical_form,
        canonical_channel,
    ):
        token = " ".join(tokens) if tokens else ""
        if token:
            recipe_parts.append(token)
    recipe_parts.append(" ".join(canonical_directional))
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = pattern.completeness or ""
    GPTState.last_scope = " ".join(canonical_scope)
    GPTState.last_method = " ".join(canonical_method)
    GPTState.last_form = " ".join(canonical_form)
    GPTState.last_channel = " ".join(canonical_channel)
    GPTState.last_directional = " ".join(canonical_directional)
    GPTState.last_axes = {
        "completeness": [pattern.completeness] if pattern.completeness else [],
        "scope": canonical_scope,
        "method": canonical_method,
        "form": canonical_form,
        "channel": canonical_channel,
        "directional": canonical_directional,
    }

    actions.user.prompt_pattern_gui_close()


@mod.action_class
class UserActions:
    def prompt_pattern_gui_open_for_static_prompt(static_prompt: str):
        """Open the prompt pattern picker GUI for a specific static prompt"""
        if _reject_if_request_in_flight():
            return
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_canvas_close()
        except Exception:
            pass
        _open_prompt_pattern_canvas(static_prompt)
        ctx.tags = ["user.model_prompt_pattern_window_open"]

    def prompt_pattern_gui_close():
        """Close the prompt pattern picker GUI"""
        if _reject_if_request_in_flight():
            return
        _close_prompt_pattern_canvas()
        ctx.tags = []

    def prompt_pattern_run_preset(preset_name: str):
        """Run a prompt pattern by preset name for the current static prompt"""
        if _reject_if_request_in_flight():
            return
        static_prompt = PromptPatternGUIState.static_prompt
        if not static_prompt:
            actions.app.notify("No prompt selected for patterns")
            return
        for pattern in PROMPT_PRESETS:
            if pattern.name.lower() == preset_name.lower():
                _run_prompt_pattern(static_prompt, pattern)
                break

    def prompt_pattern_save_source_to_file():
        """Save the most recent model response to a file via the confirmation GUI helper."""
        if _reject_if_request_in_flight():
            return
        try:
            actions.user.confirmation_gui_save_to_file()
        except Exception:
            actions.app.notify(
                "GPT: Could not save response to file from prompt patterns"
            )
