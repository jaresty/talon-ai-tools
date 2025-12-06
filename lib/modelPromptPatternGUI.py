from dataclasses import dataclass
import os
from typing import Dict, Literal, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState

try:
    # Prefer the shared static prompt domain helpers when available.
    from .staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile
except ImportError:  # Talon may have an older module state cached
    from .staticPromptConfig import STATIC_PROMPT_CONFIG

    def get_static_prompt_profile(name: str):
        return STATIC_PROMPT_CONFIG.get(name)

    def get_static_prompt_axes(name: str) -> dict[str, str]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, str] = {}
        for axis in ("completeness", "scope", "method", "style"):
            value = profile.get(axis)
            if value:
                axes[axis] = value
        return axes
from .talonSettings import ApplyPromptConfiguration, modelPrompt

mod = Module()
ctx = Context()
mod.tag(
    "model_prompt_pattern_window_open",
    desc="Tag for enabling prompt-specific pattern commands when the prompt pattern picker is open",
)


PatternDomain = Literal["prompt"]


class PromptPatternGUIState:
    static_prompt: Optional[str] = None


@dataclass(frozen=True)
class PromptAxisPattern:
    name: str
    description: str
    completeness: str
    scope: str
    method: str
    style: str
    directional: str


class PromptPatternCanvasState:
    """State specific to the canvas-based prompt pattern picker."""

    showing: bool = False
    scroll_y: float = 0.0


_prompt_pattern_canvas: Optional[canvas.Canvas] = None
_prompt_pattern_button_bounds: Dict[str, Tuple[int, int, int, int]] = {}
_prompt_pattern_hover_close: bool = False
_prompt_pattern_hover_name: Optional[str] = None

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
    """Load a Talon list file as key -> description mapping."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
    mapping: dict[str, str] = {}
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
                    key, value = line.split(":", 1)
                    mapping[key.strip()] = value.strip()
    except FileNotFoundError:
        return {}
    return mapping


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
STYLE_MAP = _load_axis_map("styleModifier.talon-list")
DIRECTIONAL_MAP = _load_axis_map("directionalModifier.talon-list")


PROMPT_PRESETS: list[PromptAxisPattern] = [
    PromptAxisPattern(
        name="Quick gist",
        description="Short, focused summary of the main points.",
        completeness="gist",
        scope="focus",
        method="",
        style="plain",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Deep narrow rigor",
        description="Thorough, narrow analysis with explicit reasoning.",
        completeness="full",
        scope="narrow",
        method="rigor",
        style="plain",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Bulleted summary",
        description="Compact bullet-point summary for quick scanning.",
        completeness="gist",
        scope="focus",
        method="",
        style="bullets",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Abstraction ladder",
        description="Place the focal problem in the middle, with reasons above and consequences below.",
        completeness="full",
        scope="focus",
        method="ladder",
        style="plain",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Cluster items",
        description="Group related items into labeled categories; clustered output only.",
        completeness="full",
        scope="narrow",
        method="cluster",
        style="plain",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Rank items",
        description="Sort items in order of importance to the audience.",
        completeness="full",
        scope="narrow",
        method="prioritize",
        style="plain",
        directional="fog",
    ),
]


def _ensure_prompt_pattern_canvas() -> canvas.Canvas:
    """Create the prompt pattern canvas if needed and register handlers."""
    global _prompt_pattern_canvas
    if _prompt_pattern_canvas is not None:
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
        _prompt_pattern_canvas = canvas.Canvas.from_rect(rect)
        try:
            _prompt_pattern_canvas.blocks_mouse = True
        except Exception:
            pass
    except Exception:
        _prompt_pattern_canvas = canvas.Canvas.from_screen(screen)

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_prompt_patterns(c)

    _prompt_pattern_canvas.register("draw", _on_draw)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot, pattern selection, hover, and drag."""
        try:
            global _prompt_pattern_hover_close, _prompt_pattern_hover_name
            rect = getattr(_prompt_pattern_canvas, "rect", None)
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

            # Track hover state for the close hotspot and pattern buttons.
            if event_type in ("mousemove", "mouse_move") and button not in (0, 1):
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

            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Close hotspot in top-right header band.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("prompt pattern canvas close click detected")
                    actions.user.prompt_pattern_gui_close()
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
                            _run_prompt_pattern(PromptPatternGUIState.static_prompt, pattern)
                            break
                    return

            # Minimal drag: allow moving the panel by dragging the header.
            if event_type in ("mousemove", "mouse_move") and button in (0, 1):
                if 0 <= local_y <= header_height:
                    try:
                        dx = gpos.x - rect.x
                        dy = gpos.y - rect.y
                        _prompt_pattern_canvas.move(rect.x + dx, rect.y + dy)
                    except Exception:
                        pass
                return

            # Vertical scroll via mouse wheel when available.
            if event_type in ("mouse_scroll", "wheel", "scroll"):
                dy = getattr(evt, "dy", 0) or getattr(evt, "wheel_y", 0)
                try:
                    dy = float(dy)
                except Exception:
                    dy = 0.0
                if dy and rect is not None:
                    line_h = 18
                    row_height = line_h * 5
                    # Approximate the same body region used in _draw_prompt_patterns.
                    body_top = rect.y + 60 + line_h * 6
                    body_bottom = rect.y + rect.height - line_h * 2
                    visible_height = max(body_bottom - body_top, row_height)
                    total_content_height = row_height * len(PROMPT_PRESETS)
                    max_scroll = max(total_content_height - visible_height, 0)
                    new_scroll = PromptPatternCanvasState.scroll_y - dy * 40.0
                    PromptPatternCanvasState.scroll_y = max(min(new_scroll, max_scroll), 0.0)
                return
        except Exception:
            return

    try:
        _prompt_pattern_canvas.register("mouse", _on_mouse)
    except Exception:
        _debug("mouse handler registration failed for prompt pattern canvas")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = getattr(evt, "key", "") or ""
            if key.lower() in ("escape", "esc"):
                actions.user.prompt_pattern_gui_close()
        except Exception:
            return

    try:
        _prompt_pattern_canvas.register("key", _on_key)
    except Exception:
        _debug("key handler registration failed for prompt pattern canvas")

    return _prompt_pattern_canvas


def _open_prompt_pattern_canvas(static_prompt: str) -> None:
    canvas_obj = _ensure_prompt_pattern_canvas()
    PromptPatternGUIState.static_prompt = static_prompt
    PromptPatternCanvasState.showing = True
    PromptPatternCanvasState.scroll_y = 0.0
    canvas_obj.show()


def _close_prompt_pattern_canvas() -> None:
    global _prompt_pattern_canvas, _prompt_pattern_hover_close, _prompt_pattern_hover_name
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
    for label in ("completeness", "scope", "method", "style"):
        value = profile_axes.get(label)
        if value:
            axes.append(f"{label.capitalize()}: {value}")
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
        f"  model {static_prompt} [completeness] [scope] [method] [style] <directional lens>",
        x,
        y,
    )
    y += line_h * 2

    draw_text("Patterns for this prompt:", x, y)
    y += line_h * 2

    # Scrollable list of presets.
    if rect is not None and hasattr(rect, "height"):
        body_top = y
        body_bottom = rect.y + rect.height - line_h * 2
    else:
        body_top = y
        body_bottom = y + line_h * len(PROMPT_PRESETS) * 5
    visible_height = max(body_bottom - body_top, line_h * 4)

    # Approximate each preset row height: [Name], recipe, "Say", description, spacer.
    row_height = line_h * 5
    total_content_height = row_height * len(PROMPT_PRESETS)
    max_scroll = max(total_content_height - visible_height, 0)
    scroll_y = max(min(PromptPatternCanvasState.scroll_y, max_scroll), 0)
    PromptPatternCanvasState.scroll_y = scroll_y

    start_index = int(scroll_y // row_height)
    offset_y = body_top - (scroll_y % row_height)

    for idx in range(start_index, len(PROMPT_PRESETS)):
        pattern = PROMPT_PRESETS[idx]
        row_y = offset_y + (idx - start_index) * row_height
        if row_y > body_bottom:
            break

        label = f"[{pattern.name}]"
        draw_text(label, x, row_y)
        _prompt_pattern_button_bounds[pattern.name] = (
            x,
            row_y - line_h,
            x + len(label) * approx_char,
            row_y + line_h,
        )
        if (
            _prompt_pattern_hover_name == pattern.name
            and rect is not None
            and paint is not None
        ):
            try:
                underline_rect = Rect(x, row_y + 4, len(label) * approx_char, 1)
                c.draw_rect(underline_rect)
            except Exception:
                pass
        row_y += line_h

        recipe_tokens = [static_prompt]
        for token in (
            pattern.completeness,
            pattern.scope,
            pattern.method,
            pattern.style,
            pattern.directional,
        ):
            if token:
                recipe_tokens.append(token)
        recipe_str = " · ".join(recipe_tokens)
        draw_text(recipe_str, x, row_y)
        row_y += line_h
        draw_text(
            f"Say (grammar): model {recipe_str.replace(' · ', ' ')}",
            x,
            row_y,
        )
        row_y += line_h
        draw_text(pattern.description, x, row_y)

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
            thumb_height = max(int(visible_height * visible_height / total_content_height), 20)
            if max_scroll > 0:
                thumb_offset = int((scroll_y / max_scroll) * (visible_height - thumb_height))
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

    draw_text("Tip: Say 'close pattern menu' to close this menu.", x, body_bottom + line_h // 2)


def _run_prompt_pattern(static_prompt: str, pattern: PromptAxisPattern) -> None:
    """Execute a prompt-specific axis pattern as if spoken via the model grammar."""
    actions.app.notify(f"Running prompt pattern: {static_prompt} · {pattern.name}")

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
    if pattern.scope:
        setattr(match, "scopeModifier", _axis_value(pattern.scope, SCOPE_MAP))
    if pattern.method:
        setattr(match, "methodModifier", _axis_value(pattern.method, METHOD_MAP))
    if pattern.style:
        setattr(match, "styleModifier", _axis_value(pattern.style, STYLE_MAP))
    if pattern.directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(pattern.directional, DIRECTIONAL_MAP),
        )

    please_prompt = modelPrompt(match)

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
    for token in (
        pattern.completeness,
        pattern.scope,
        pattern.method,
        pattern.style,
    ):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = pattern.completeness or ""
    GPTState.last_scope = pattern.scope or ""
    GPTState.last_method = pattern.method or ""
    GPTState.last_style = pattern.style or ""
    GPTState.last_directional = pattern.directional or ""

    actions.user.prompt_pattern_gui_close()


@mod.action_class
class UserActions:
    def prompt_pattern_gui_open_for_static_prompt(static_prompt: str):
        """Open the prompt pattern picker GUI for a specific static prompt"""
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
        _close_prompt_pattern_canvas()
        ctx.tags = []

    def prompt_pattern_run_preset(preset_name: str):
        """Run a prompt pattern by preset name for the current static prompt"""
        static_prompt = PromptPatternGUIState.static_prompt
        if not static_prompt:
            actions.app.notify("No prompt selected for patterns")
            return
        for pattern in PROMPT_PRESETS:
            if pattern.name.lower() == preset_name.lower():
                _run_prompt_pattern(static_prompt, pattern)
                break
