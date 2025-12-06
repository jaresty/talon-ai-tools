from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState
from .talonSettings import ApplyPromptConfiguration, modelPrompt
from .modelPatternGUI import (
    _axis_value,
    _parse_recipe,
    COMPLETENESS_MAP,
    METHOD_MAP,
    SCOPE_MAP,
    STYLE_MAP,
    DIRECTIONAL_MAP,
)

mod = Module()
ctx = Context()
mod.tag(
    "model_suggestion_window_open",
    desc="Tag for enabling suggestion commands when the suggestion window is open",
)

try:  # Talon runtime
    from talon.types import Rect
except Exception:  # Tests / stubs

    class Rect:  # type: ignore[override]
        def __init__(self, x: float, y: float, width: float, height: float):
            self.x = x
            self.y = y
            self.width = width
            self.height = height


@dataclass
class Suggestion:
    name: str
    recipe: str


class SuggestionGUIState:
    suggestions: List[Suggestion] = []


class SuggestionCanvasState:
    """State specific to the canvas-based suggestion window."""

    showing: bool = False


_suggestion_canvas: Optional[canvas.Canvas] = None
_suggestion_button_bounds: Dict[int, Tuple[int, int, int, int]] = {}

# Simple geometry defaults to keep the panel centered and readable.
_PANEL_WIDTH = 720
_PANEL_HEIGHT = 520


def _load_source_spoken_map() -> dict[str, str]:
    """Map canonical model source keys to spoken tokens (for example, 'clipboard' -> 'clip')."""
    mapping: dict[str, str] = {}
    try:
        current_dir = os.path.dirname(__file__)
        path = Path(current_dir).parent / "GPT" / "lists" / "modelSource.talon-list"
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if (
                    not stripped
                    or stripped.startswith("#")
                    or stripped.startswith("list:")
                    or stripped.startswith("-")
                ):
                    continue
                if ":" not in stripped:
                    continue
                spoken, value = (part.strip() for part in stripped.split(":", 1))
                if spoken and value:
                    mapping[value] = spoken
    except FileNotFoundError:
        # If the list is missing, fall back to default behaviour (no source hint).
        mapping = {}
    return mapping


SOURCE_SPOKEN_MAP = _load_source_spoken_map()


def _debug(msg: str) -> None:
    """Lightweight debug logging for the suggestion canvas."""
    try:
        print(f"GPT suggestion canvas: {msg}")
    except Exception:
        pass


def _ensure_suggestion_canvas() -> canvas.Canvas:
    """Create the suggestion canvas if needed and register handlers."""
    global _suggestion_canvas
    if _suggestion_canvas is not None:
        return _suggestion_canvas

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
        _suggestion_canvas = canvas.Canvas.from_rect(rect)
        try:
            _suggestion_canvas.blocks_mouse = True
        except Exception:
            pass
    except Exception:
        _suggestion_canvas = canvas.Canvas.from_screen(screen)

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_suggestions(c)

    _suggestion_canvas.register("draw", _on_draw)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot and suggestion selection."""
        try:
            rect = getattr(_suggestion_canvas, "rect", None)
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

            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Close hotspot in top-right header band.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("suggestion canvas close click detected")
                    actions.user.model_prompt_recipe_suggestions_gui_close()
                    return

                # Button hits for suggestions.
                for index, (bx1, by1, bx2, by2) in list(
                    _suggestion_button_bounds.items()
                ):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    if 0 <= index < len(SuggestionGUIState.suggestions):
                        suggestion = SuggestionGUIState.suggestions[index]
                        _debug(f"suggestion clicked: {suggestion.name}")
                        _run_suggestion(suggestion)
                    return

            # Minimal drag: allow moving the panel by dragging the header.
            if event_type in ("mousemove", "mouse_move") and button in (0, 1):
                if 0 <= local_y <= header_height:
                    try:
                        dx = gpos.x - rect.x
                        dy = gpos.y - rect.y
                        _suggestion_canvas.move(rect.x + dx, rect.y + dy)
                    except Exception:
                        pass
        except Exception:
            return

    try:
        _suggestion_canvas.register("mouse", _on_mouse)
    except Exception:
        _debug("mouse handler registration failed for suggestion canvas")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = getattr(evt, "key", "") or ""
            if key.lower() in ("escape", "esc"):
                actions.user.model_prompt_recipe_suggestions_gui_close()
        except Exception:
            return

    try:
        _suggestion_canvas.register("key", _on_key)
    except Exception:
        _debug("key handler registration failed for suggestion canvas")

    return _suggestion_canvas


def _open_suggestion_canvas() -> None:
    canvas_obj = _ensure_suggestion_canvas()
    SuggestionCanvasState.showing = True
    canvas_obj.show()


def _close_suggestion_canvas() -> None:
    global _suggestion_canvas
    SuggestionCanvasState.showing = False
    if _suggestion_canvas is None:
        return
    try:
        _suggestion_canvas.hide()
    except Exception:
        pass


def _draw_suggestions(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        return

    # Reset button bounds on each draw.
    _suggestion_button_bounds.clear()

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

    if rect is not None and hasattr(rect, "x") and hasattr(rect, "y"):
        x = rect.x + 40
        y = rect.y + 60
    else:
        x = 40
        y = 60
    line_h = 18
    approx_char = 8

    draw_text("Prompt recipe suggestions", x, y)
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * approx_char) - 16
        draw_text(close_label, close_x, close_y)
    y += line_h * 2

    suggestions = SuggestionGUIState.suggestions
    if not suggestions:
        draw_text("No suggestions available. Run 'model suggest' first.", x, y)
        return

    # Render each suggestion as a clickable row (name + grammar hint).
    for index, suggestion in enumerate(suggestions):
        label = f"[{suggestion.name}]"
        label_width = len(label) * approx_char
        row_top = y - line_h
        row_bottom = y + line_h
        if rect is not None:
            bx1 = x
            by1 = row_top
            bx2 = x + label_width
            by2 = row_bottom
        else:
            bx1 = x
            by1 = row_top
            bx2 = x + label_width
            by2 = row_bottom
        _suggestion_button_bounds[index] = (bx1, by1, bx2, by2)

        draw_text(label, x, y)
        y += line_h

        source_key = getattr(GPTState, "last_suggest_source", "")
        spoken_source = SOURCE_SPOKEN_MAP.get(source_key, "")
        base_recipe = suggestion.recipe.replace(" · ", " ")
        if spoken_source:
            grammar_phrase = f"model {spoken_source} {base_recipe}"
        else:
            grammar_phrase = f"model {base_recipe}"
        draw_text(f"Say: {grammar_phrase}", x + 4, y)
        y += line_h * 2


def _refresh_suggestions_from_state() -> None:
    SuggestionGUIState.suggestions = [
        Suggestion(name=item["name"], recipe=item["recipe"])
        for item in GPTState.last_suggested_recipes
        if item.get("name") and item.get("recipe")
    ]


def _run_suggestion(suggestion: Suggestion) -> None:
    """Execute a suggested recipe as if spoken via the model grammar."""
    static_prompt, completeness, scope, method, style, directional = _parse_recipe(
        suggestion.recipe
    )
    if not static_prompt:
        actions.app.notify("Suggestion has no static prompt; cannot run")
        return

    actions.app.notify(f"Running suggestion: {suggestion.name}")

    class Match:
        pass

    match = Match()
    setattr(match, "staticPrompt", static_prompt)
    if completeness:
        setattr(
            match,
            "completenessModifier",
            _axis_value(completeness, COMPLETENESS_MAP),
        )
    if scope:
        setattr(match, "scopeModifier", _axis_value(scope, SCOPE_MAP))
    if method:
        setattr(match, "methodModifier", _axis_value(method, METHOD_MAP))
    if style:
        setattr(match, "styleModifier", _axis_value(style, STYLE_MAP))
    if directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(directional, DIRECTIONAL_MAP),
        )

    please_prompt = modelPrompt(match)

    # Prefer the source used when generating these suggestions, falling back
    # to the current default source when unavailable.
    source_key = getattr(GPTState, "last_suggest_source", "") or settings.get(
        "user.model_default_source"
    )

    config = ApplyPromptConfiguration(
        please_prompt=please_prompt,
        model_source=create_model_source(source_key),
        additional_model_source=None,
        model_destination=create_model_destination(
            settings.get("user.model_default_destination")
        ),
    )

    # Dismiss the suggestion window immediately on selection so the
    # execution result can use the normal confirmation/destination
    # surfaces without overlapping modals.
    actions.user.model_prompt_recipe_suggestions_gui_close()
    actions.user.gpt_apply_prompt(config)

    # Keep last_recipe concise and token-based to reinforce speakable grammar.
    recipe_parts = [static_prompt]
    for token in (completeness, scope, method, style):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = completeness or ""
    GPTState.last_scope = scope or ""
    GPTState.last_method = method or ""
    GPTState.last_style = style or ""
    GPTState.last_directional = directional or ""


@mod.action_class
class UserActions:
    def model_prompt_recipe_suggestions_gui_open():
        """Open the prompt recipe suggestion canvas for the last suggestions."""
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return

        # Close related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_canvas_close()
        except Exception:
            pass

        _open_suggestion_canvas()
        ctx.tags = ["user.model_suggestion_window_open"]

    def model_prompt_recipe_suggestions_gui_close():
        """Close the prompt recipe suggestion canvas."""
        _close_suggestion_canvas()
        ctx.tags = []

    def model_prompt_recipe_suggestions_run_index(index: int):
        """Run the Nth suggested recipe (1-based index)."""
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return
        if index <= 0 or index > len(SuggestionGUIState.suggestions):
            actions.app.notify(f"No suggestion numbered {index}")
            return
        _run_suggestion(SuggestionGUIState.suggestions[index - 1])
