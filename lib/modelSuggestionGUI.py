from dataclasses import dataclass
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

from .canvasFont import apply_canvas_typeface
from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState
from .talonSettings import ApplyPromptConfiguration, modelPrompt
from .personaConfig import PERSONA_PRESETS, INTENT_PRESETS
from .suggestionCoordinator import (
    suggestion_entries_with_metadata,
    suggestion_source,
    set_last_recipe_from_selection,
    suggestion_grammar_phrase,
)
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
    # Structured Persona/Intent axes (Who/Why). These are optional and left
    # empty when a suggestion does not provide a stance in axis form.
    persona_voice: str = ""
    persona_audience: str = ""
    persona_tone: str = ""
    intent_purpose: str = ""
    # Flexible, model-authored stance string. This is typically a
    # voice-friendly command like "persona teach junior dev · intent teach"
    # or "model write as teacher to junior engineer kindly for teaching".
    stance_command: str = ""
    # Short natural-language explanation of when to use this suggestion.
    why: str = ""


class SuggestionGUIState:
    suggestions: List[Suggestion] = []


class SuggestionCanvasState:
    """State specific to the canvas-based suggestion window."""

    showing: bool = False
    scroll_y: float = 0.0


_suggestion_canvas: Optional[canvas.Canvas] = None
_suggestion_button_bounds: Dict[int, Tuple[int, int, int, int]] = {}
_suggestion_hover_close: bool = False
_suggestion_hover_index: Optional[int] = None
_suggestion_drag_offset: Optional[Tuple[float, float]] = None

# Simple geometry defaults to keep the panel centered and readable.
_PANEL_WIDTH = 840
_PANEL_HEIGHT = 720


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
        except Exception as e:
            _debug(f"could not set blocks_mouse: {e}")
    except Exception as e:
        _debug(f"falling back to screen canvas: {e}")
        _suggestion_canvas = canvas.Canvas.from_screen(screen)

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_suggestions(c)

    _suggestion_canvas.register("draw", _on_draw)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot, suggestion selection, hover, and drag."""
        try:
            global \
                _suggestion_hover_close, \
                _suggestion_hover_index, \
                _suggestion_drag_offset
            rect = getattr(_suggestion_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type_raw = getattr(evt, "event", "") or ""
            event_type = str(event_type_raw).lower()
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos

            local_x = pos.x
            local_y = pos.y
            if local_x < 0 or local_y < 0:
                if _suggestion_drag_offset is None:
                    return
            abs_x = rect.x + local_x
            abs_y = rect.y + local_y

            header_height = 32
            hotspot_width = 80

            # Hover feedback for the close hotspot and suggestion rows.
            if event_type in ("mousemove", "mouse_move", "mouse_drag", "mouse_dragged"):
                _suggestion_hover_close = (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                )
                hover_index: Optional[int] = None
                for index, (bx1, by1, bx2, by2) in list(
                    _suggestion_button_bounds.items()
                ):
                    if bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2:
                        hover_index = index
                        break
                _suggestion_hover_index = hover_index

            if event_type in (
                "mousedown",
                "mouse_down",
                "mouse_drag",
                "mouse_drag_start",
            ) and button in (0, 1, None):
                handled_click = False
                # Close hotspot in top-right header band.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("suggestion canvas close click detected")
                    actions.user.model_prompt_recipe_suggestions_gui_close()
                    handled_click = True
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
                        handled_click = True
                    return

                # Start drag anywhere that was not a button hit.
                if not handled_click:
                    _suggestion_drag_offset = (gpos.x - rect.x, gpos.y - rect.y)
                    return

            if event_type in ("mouseup", "mouse_up", "mouse_drag_end"):
                _suggestion_drag_offset = None
                return

            # Drag while moving with an active drag offset.
            if (
                event_type in ("mousemove", "mouse_move", "mouse_drag", "mouse_dragged")
                and _suggestion_drag_offset is not None
            ):
                dx, dy = _suggestion_drag_offset
                new_x = gpos.x - dx
                new_y = gpos.y - dy
                try:
                    _suggestion_canvas.move(new_x, new_y)
                except Exception:
                    _suggestion_drag_offset = None
                    _debug("suggestion canvas drag move failed; clearing drag state")
                return

            # Vertical scroll via mouse wheel when available.
            if event_type in ("mouse_scroll", "wheel", "scroll"):
                dy = getattr(evt, "dy", 0) or getattr(evt, "wheel_y", 0)
                try:
                    dy = float(dy)
                except Exception:
                    dy = 0.0
                if dy and rect is not None:
                    # Positive dy scrolls down (content up).
                    line_h = 18
                    row_height = line_h * 3
                    body_top = 60 + line_h * 2
                    body_bottom = rect.y + rect.height - line_h * 2
                    visible_height = max(body_bottom - body_top, row_height)
                    total_content_height = row_height * max(
                        len(SuggestionGUIState.suggestions), 0
                    )
                    max_scroll = max(total_content_height - visible_height, 0)
                    new_scroll = SuggestionCanvasState.scroll_y - dy * 40.0
                    SuggestionCanvasState.scroll_y = max(
                        min(new_scroll, max_scroll), 0.0
                    )
                return
        except Exception as e:
            _debug(f"suggestion canvas mouse handler error: {e}")
            return

    try:
        _suggestion_canvas.register("mouse", _on_mouse)
    except Exception as e:
        _debug(f"mouse handler registration failed for suggestion canvas: {e}")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = getattr(evt, "key", "") or ""
            if key.lower() in ("escape", "esc"):
                actions.user.model_prompt_recipe_suggestions_gui_close()
        except Exception as e:
            _debug(f"suggestion canvas key handler error: {e}")
            return

    try:
        _suggestion_canvas.register("key", _on_key)
    except Exception as e:
        _debug(f"key handler registration failed for suggestion canvas: {e}")

    return _suggestion_canvas


def _open_suggestion_canvas() -> None:
    canvas_obj = _ensure_suggestion_canvas()
    SuggestionCanvasState.showing = True
    SuggestionCanvasState.scroll_y = 0.0
    canvas_obj.show()


def _close_suggestion_canvas() -> None:
    global \
        _suggestion_canvas, \
        _suggestion_hover_close, \
        _suggestion_hover_index, \
        _suggestion_drag_offset
    SuggestionCanvasState.showing = False
    SuggestionCanvasState.scroll_y = 0.0
    _suggestion_hover_close = False
    _suggestion_hover_index = None
    _suggestion_drag_offset = None
    if _suggestion_canvas is None:
        return
    try:
        _suggestion_canvas.hide()
    except Exception as e:
        _debug(f"failed to hide suggestion canvas: {e}")


def _hydrate_axis_list(tokens: str, mapping: dict[str, str]) -> str:
    """Return hydrated axis descriptions for a space-separated token list."""
    if not tokens:
        return ""
    hydrated = []
    for token in tokens.split():
        hydrated.append(mapping.get(token, token))
    return " ".join(hydrated)


def _draw_suggestions(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        return

    # Reset button bounds on each draw.
    _suggestion_button_bounds.clear()

    paint = getattr(c, "paint", None)
    if paint is not None:
        apply_canvas_typeface(
            paint,
            settings_key="user.model_response_canvas_typeface",
            cache_key="suggestions",
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

    draw_text("Prompt recipe suggestions", x, y)
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * approx_char) - 16
        draw_text(close_label, close_x, close_y)
        if paint is not None and _suggestion_hover_close:
            try:
                underline_rect = Rect(
                    close_x, close_y + 4, len(close_label) * approx_char, 1
                )
                c.draw_rect(underline_rect)
            except Exception:
                pass
    y += line_h * 2

    suggestions = SuggestionGUIState.suggestions
    if not suggestions:
        draw_text("No suggestions available. Run 'model run suggest' first.", x, y)
        return

    # No global stance hint here: keep the panel focused on per-suggestion
    # contract and stance so it is clear which commands apply to which row.

    # Each suggestion row is rendered as:
    #   [Name]
    #   Say: model …
    #   Axes: <compact summary>
    #   (optional) S1/Why lines (stance and why on their own lines)
    # which we approximate as a fixed row height with a small gap
    # between suggestions for readability.
    row_height = line_h * 6
    body_top = y
    if rect is not None and hasattr(rect, "height"):
        # Leave extra margin above the footer tip so the last suggestion
        # does not visually collide with it. Use a slightly larger gap to
        # avoid overlap when Why text runs long.
        body_bottom = rect.y + rect.height - line_h * 4
    else:
        body_bottom = body_top + row_height * len(suggestions)
    visible_height = max(body_bottom - body_top, row_height)

    total_content_height = row_height * len(suggestions)
    max_scroll = max(total_content_height - visible_height, 0)
    scroll_y = max(min(SuggestionCanvasState.scroll_y, max_scroll), 0)
    SuggestionCanvasState.scroll_y = scroll_y

    start_index = int(scroll_y // row_height)
    offset_y = body_top - (scroll_y % row_height)

    # Render each visible suggestion as a clickable row.
    for index in range(start_index, len(suggestions)):
        suggestion = suggestions[index]
        row_y = offset_y + (index - start_index) * row_height
        if row_y > body_bottom:
            break

        label = f"[{suggestion.name}]"
        label_width = len(label) * approx_char
        row_top = row_y - line_h
        row_bottom = row_y + line_h
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

        draw_text(label, x, row_y)
        if _suggestion_hover_index == index and rect is not None and paint is not None:
            try:
                underline_rect = Rect(x, row_y + 4, label_width, 1)
                c.draw_rect(underline_rect)
            except Exception:
                pass
        row_y += line_h

        source_key = getattr(GPTState, "last_suggest_source", "")
        grammar_phrase = suggestion_grammar_phrase(
            suggestion.recipe, source_key, SOURCE_SPOKEN_MAP
        )
        draw_text(f"Say: {grammar_phrase}", x + 4, row_y)
        row_y += line_h

        static_prompt, completeness, scope, method, style, directional = _parse_recipe(
            suggestion.recipe
        )
        # Render a compact axes summary instead of full hydrated descriptions
        # to keep the suggestions panel readable.
        summary_parts: list[str] = []
        if completeness:
            summary_parts.append(f"C:{completeness}")
        if scope:
            summary_parts.append(f"S:{scope}")
        if method:
            summary_parts.append(f"M:{method}")
        if style:
            summary_parts.append(f"St:{style}")
        if directional:
            summary_parts.append(f"D:{directional}")
        if summary_parts:
            draw_text(f"Axes: {' '.join(summary_parts)}", x + 4, row_y)

    # Use the remaining row height to show an optional, compact stance
    # and explanation. Stance is expressed in terms of Persona/Intent axes
    # plus a flexible, voice-friendly stance_command when present.
    has_persona_axes = bool(
        getattr(suggestion, "persona_voice", "")
        or getattr(suggestion, "persona_audience", "")
        or getattr(suggestion, "persona_tone", "")
    )
    has_intent_axis = bool(getattr(suggestion, "intent_purpose", ""))
    has_stance_command = bool(suggestion.stance_command)
    has_why = bool(suggestion.why)

    if has_persona_axes or has_intent_axis or has_stance_command or has_why:
        row_y += line_h
        # Put the concrete voice command first so users know exactly what to say.
        if has_stance_command:
            draw_text(f"Say: {suggestion.stance_command}", x + 4, row_y)
            row_y += line_h
        if has_persona_axes or has_intent_axis:
            draw_text("Stance:", x + 4, row_y)
            row_y += line_h
            if has_persona_axes:
                persona_bits = [
                    b
                    for b in [
                        getattr(suggestion, "persona_voice", ""),
                        getattr(suggestion, "persona_audience", ""),
                        getattr(suggestion, "persona_tone", ""),
                    ]
                    if b
                ]
                if persona_bits:
                    # Label these as Who (axes) to distinguish them from the
                    # `persona` command, which takes presets rather than raw
                    # axis tokens.
                    draw_text(
                        "  Who: " + " · ".join(persona_bits),
                        x + 4,
                        row_y,
                    )
                    row_y += line_h
            if has_intent_axis:
                # Label the purpose axis as Why (axis) so it is clearly the
                # Intent axis, not the `intent` command.
                draw_text(
                    f"  Why: {getattr(suggestion, 'intent_purpose', '')}",
                    x + 4,
                    row_y,
                )
                row_y += line_h
        if has_why:
            # Keep Why reasonably compact; truncate if extremely long.
            why_text = f"Why: {suggestion.why}"
            draw_text(why_text[:200], x + 4, row_y)
    else:
        # Lightweight spacer below Axes when no stance/why metadata.
        row_y += line_h

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

    # Optional global reset hint, kept compact and non-interactive to
    # avoid changing per-suggestion behaviour while still advertising
    # the stance reset command described in ADR 040/041.
    if rect is not None:
        tip = 'Tip: say "model reset writing" to reset stance.'
        tip_y = rect.y + rect.height - line_h
        draw_text(tip, rect.x + 40, tip_y)


def _refresh_suggestions_from_state() -> None:
    SuggestionGUIState.suggestions = [
        Suggestion(
            name=item["name"],
            recipe=item["recipe"],
            persona_voice=item.get("persona_voice", ""),
            persona_audience=item.get("persona_audience", ""),
            persona_tone=item.get("persona_tone", ""),
            intent_purpose=item.get("intent_purpose", ""),
            stance_command=item.get("stance_command", ""),
            why=item.get("why", ""),
        )
        for item in suggestion_entries_with_metadata()
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
    source_key = suggestion_source(settings.get("user.model_default_source"))

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
    set_last_recipe_from_selection(
        static_prompt,
        completeness,
        scope,
        method,
        style,
        directional,
    )


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
        """Run a suggestion by 1-based index from the cached list."""
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return
        if index <= 0 or index > len(SuggestionGUIState.suggestions):
            actions.app.notify("Suggestion index out of range")
            return

        suggestion = SuggestionGUIState.suggestions[index - 1]
        _run_suggestion(suggestion)
