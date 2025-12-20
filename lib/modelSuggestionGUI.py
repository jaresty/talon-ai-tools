from dataclasses import dataclass
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

from .canvasFont import apply_canvas_typeface
from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState
from .talonSettings import (
    ApplyPromptConfiguration,
    modelPrompt,
    safe_model_prompt,
    _canonicalise_axis_tokens,
)
from .personaConfig import persona_intent_maps
from .stanceValidation import valid_stance_command
from .suggestionCoordinator import (
    suggestion_entries_with_metadata,
    suggestion_source,
    set_last_recipe_from_selection,
    suggestion_grammar_phrase,
    suggestion_context,
)
from .modelPatternGUI import (
    _axis_value,
    _parse_recipe,
    COMPLETENESS_MAP,
    METHOD_MAP,
    SCOPE_MAP,
    FORM_MAP,
    CHANNEL_MAP,
    DIRECTIONAL_MAP,
)
from .requestBus import is_in_flight as bus_is_in_flight
from .requestGating import try_begin_request
from .requestLog import drop_reason_message, set_drop_reason
from .modelHelpers import notify
from .stanceDefaults import stance_defaults_lines
from .overlayHelpers import apply_canvas_blocking, clamp_scroll
from .overlayLifecycle import close_overlays, close_common_overlays
from .overlayLifecycle import close_overlays

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


_ALIAS_NORMALISE_PATTERN = re.compile(r"[^a-z0-9]+")


def _normalise_alias_token(raw: str) -> str:
    token = str(raw or "").strip().lower()
    if not token:
        return ""
    token = _ALIAS_NORMALISE_PATTERN.sub(" ", token)
    token = re.sub(r"\s+", " ", token)
    return token.strip()


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
    # Model-provided reasoning for the stance/axes choice.
    reasoning: str = ""
    # Snapshot metadata for presets/aliases captured during suggestion parsing.
    persona_preset_key: str = ""
    persona_preset_label: str = ""
    persona_preset_spoken: str = ""
    intent_preset_key: str = ""
    intent_preset_label: str = ""
    intent_display: str = ""


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
_scroll_debug_samples: int = 0
_scroll_state_debug_samples: int = 0
_WHY_REASON_LABEL = "Why:"
_AXES_LEGEND = "Axes: Completeness | Scope | Method | Form | Channel | Directional"
_SECONDARY_INDENT = 12
_REASONING_COLOR = "555555"
_WHY_COLOR = "111111"
_REASONING_INDENT = _SECONDARY_INDENT + 8
_AXES_WRAP_MAX_CHARS = 90

# Simple geometry defaults to keep the panel centered and readable.
_PANEL_WIDTH = 840
# Give suggestions more vertical room before scrolling while still
# respecting screen margins on smaller displays.
_PANEL_HEIGHT = 880


def _persona_maps():
    try:
        return persona_intent_maps()
    except Exception:
        return None


def _canonical_persona_token(axis: str, value: str) -> str:
    try:
        from . import personaConfig

        return personaConfig.canonical_persona_token(axis, value)
    except Exception:
        return str(value or "").strip()


def _persona_presets():
    """Return the latest persona presets (reload-safe)."""

    maps = _persona_maps()
    if maps is None:
        return ()
    return tuple(maps.persona_presets.values())


def _persona_preset_map() -> dict[str, object]:
    """Return a name->PersonaPreset map built from the latest presets."""

    maps = _persona_maps()
    if maps is None:
        return {}

    preset_map: dict[str, object] = {}
    for alias, canonical in maps.persona_preset_aliases.items():
        preset = maps.persona_presets.get(canonical)
        if preset is not None:
            preset_map.setdefault(alias, preset)
    return preset_map


def _normalize_intent(value: str) -> str:
    """Normalise an intent token using the latest personaConfig helpers."""
    try:
        from . import personaConfig

        return personaConfig.normalize_intent_token(value)
    except Exception:
        return str(value or "").strip()


def _wrap_lines_count(
    text: str,
    x_pos: int,
    rect: Optional["canvas.Rect"],
    approx_char: int = 8,
    line_h: int = 20,
    max_chars_override: Optional[int] = None,
) -> int:
    """Return the number of wrapped lines for a given string."""
    if not text:
        return 0
    max_chars = max_chars_override or 80
    try:
        if rect is not None and hasattr(rect, "width") and hasattr(rect, "x"):
            right_margin = rect.x + rect.width - 40
            available_px = max(right_margin - x_pos, 160)
            candidate = max(int(available_px // approx_char), 20)
            max_chars = min(max_chars, candidate) if max_chars_override else candidate
    except Exception:
        max_chars = max_chars_override or 80

    words = text.split()
    line_words: list[str] = []
    current_len = 0
    lines = 0
    for word in words:
        extra = len(word) if not line_words else len(word) + 1
        if line_words and current_len + extra > max_chars:
            lines += 1
            line_words = [word]
            current_len = len(word)
        else:
            line_words.append(word)
            current_len += extra
    if line_words:
        lines += 1
    return lines


def _measure_suggestion_height(
    suggestion: Suggestion,
    x_pos: int,
    rect: Optional["canvas.Rect"],
    approx_char: int,
    line_h: int,
) -> int:
    """Approximate the rendered height of a suggestion row."""
    h = 0
    stance_info = _suggestion_stance_info(suggestion)
    # Label, Say, Axes (axes summary always present if any recipe parts).
    h += line_h  # label
    source_key = getattr(GPTState, "last_suggest_source", "")
    grammar_phrase = suggestion_grammar_phrase(
        suggestion.recipe, source_key, SOURCE_SPOKEN_MAP
    )
    say_lines = _wrap_lines_count(
        f"Say: {grammar_phrase}", x_pos + 4, rect, approx_char, line_h
    )
    h += line_h * max(say_lines, 1)
    h += line_h // 3  # breathing room after commands
    # Axes line (may be empty but draw once when non-empty).
    (
        _static_prompt,
        completeness,
        scope,
        method,
        form,
        channel,
        directional,
    ) = _parse_recipe(suggestion.recipe)
    axes_text = _axes_summary(completeness, scope, method, form, channel, directional)
    if axes_text:
        lines = _wrap_lines_count(
            f"Axes: {axes_text}",
            x_pos + 4,
            rect,
            approx_char,
            line_h,
            max_chars_override=_AXES_WRAP_MAX_CHARS,
        )
        h += line_h * max(lines, 1)
        h += line_h // 3  # separation before stance block

    persona_bits = stance_info["persona_bits"]
    intent_display = stance_info["intent_display"]
    stance_text = stance_info.get("stance_display", stance_info["stance_command"])
    has_persona_axes = bool(persona_bits)
    has_intent_axis = bool(intent_display)
    has_stance_command = bool(stance_text)
    why_text = stance_info["why_text"]
    has_why = bool(why_text)
    reasoning_text = getattr(suggestion, "reasoning", "").strip()
    has_reasoning = bool(reasoning_text)

    if (
        has_persona_axes
        or has_intent_axis
        or has_stance_command
        or has_why
        or has_reasoning
    ):
        h += line_h  # spacing before stance block
        if has_stance_command:
            lines = _wrap_lines_count(
                f"Say (stance): {stance_text}",
                x_pos + 4,
                rect,
                approx_char,
                line_h,
                max_chars_override=_AXES_WRAP_MAX_CHARS,
            )
            h += line_h * max(lines, 1)
        if has_persona_axes:
            h += line_h  # persona line
        if has_intent_axis:
            h += line_h  # intent line
        if has_why:
            # Slight breathing room before the Why block to separate it from stance info.
            h += line_h // 2
            reason_text = f"{_WHY_REASON_LABEL} {why_text}"
            lines = _wrap_lines_count(
                reason_text,
                x_pos + 4,
                rect,
                approx_char,
                line_h,
                max_chars_override=_AXES_WRAP_MAX_CHARS,
            )
            h += line_h * max(lines, 1)
        if has_reasoning:
            reason_text = f"Reasoning: {reasoning_text}"
            lines = _wrap_lines_count(
                reason_text,
                x_pos + 4 + _REASONING_INDENT,
                rect,
                approx_char,
                line_h,
                max_chars_override=_AXES_WRAP_MAX_CHARS,
            )
            h += line_h * max(lines, 1)
        h += line_h // 3  # breathing room before next suggestion

    # Spacer between rows to match the draw path's trailing gap.
    h += int(line_h * 2.2)
    return h


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""

    try:
        return bus_is_in_flight()
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""

    allowed, reason = try_begin_request(source="modelSuggestionGUI")
    if not allowed and reason == "in_flight":
        message = drop_reason_message("in_flight")
        try:
            set_drop_reason("in_flight")
        except Exception:
            pass
        notify(message)
        return True
    return False


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


def _axes_summary(
    completeness: str,
    scope: str,
    method: str,
    form: str,
    channel: str,
    directional: str,
) -> str:
    """Return a compact, legible axes summary with abbreviated labels."""
    parts: list[str] = []
    if completeness:
        parts.append(f"C {completeness}")
    if scope:
        parts.append(f"S {scope}")
    if method:
        parts.append(f"M {method}")
    if form:
        parts.append(f"F {form}")
    if channel:
        parts.append(f"Ch {channel}")
    if directional:
        parts.append(f"D {directional}")
    return " | ".join(parts)


def _persona_long_form(stance_command: str, persona_bits: list[str]) -> str:
    """Return a long-form 'model write ...' stance for persona presets."""
    if not stance_command:
        return ""
    stance_l = stance_command.strip().lower()
    if not stance_l.startswith("persona "):
        return ""
    preset_name = stance_l[len("persona ") :].strip()
    if not preset_name:
        return ""

    axes = [bit for bit in persona_bits if bit]
    preset = _persona_preset_map().get(preset_name)
    if not axes and preset:
        axes = [
            value for value in (preset.voice, preset.audience, preset.tone) if value
        ]
    if not axes:
        return ""
    return "model write " + " ".join(axes)


def _match_persona_preset(
    voice: str, audience: str, tone: str
) -> Optional["PersonaPreset"]:
    """Return a PersonaPreset matching the provided axes, if any."""

    voice_token = _canonical_persona_token("voice", voice)
    audience_token = _canonical_persona_token("audience", audience)
    tone_token = _canonical_persona_token("tone", tone)
    maps = _persona_maps()
    if maps is None:
        return None
    for preset in maps.persona_presets.values():
        preset_voice = (preset.voice or "").strip()
        preset_audience = (preset.audience or "").strip()
        preset_tone = (preset.tone or "").strip()
        # Require a match for each axis the preset declares; ignore axes the
        # preset leaves empty (for example, tone is optional).
        if preset_voice and preset_voice != voice_token:
            continue
        if preset_audience and preset_audience != audience_token:
            continue
        if preset_tone and preset_tone != tone_token:
            continue
        # Avoid false positives when no axes are present.
        if not (preset_voice or preset_audience or preset_tone):
            continue
        return preset
    return None


def _preset_from_command(stance_command: str) -> Optional["PersonaPreset"]:
    """Return a PersonaPreset for a 'persona <...>' command token when present."""
    cmd = (stance_command or "").strip().lower()
    if not cmd.startswith("persona "):
        return None
    name = cmd[len("persona ") :].strip()
    if not name:
        return None
    return _persona_preset_map().get(name)


def _suggestion_stance_info(suggestion: Suggestion) -> dict[str, object]:
    """Return precomputed stance fields (persona/intent/stance/why) for display."""
    voice_token = _canonical_persona_token(
        "voice", getattr(suggestion, "persona_voice", "")
    )
    audience_token = _canonical_persona_token(
        "audience", getattr(suggestion, "persona_audience", "")
    )
    tone_token = _canonical_persona_token(
        "tone", getattr(suggestion, "persona_tone", "")
    )
    persona_bits = [bit for bit in (voice_token, audience_token, tone_token) if bit]
    intent_text = getattr(suggestion, "intent_purpose", "").strip()
    intent_display_meta = (getattr(suggestion, "intent_display", "") or "").strip()
    intent_display = (
        intent_display_meta or _normalize_intent(intent_text) or intent_text
    )
    persona_preset_key = (getattr(suggestion, "persona_preset_key", "") or "").strip()
    persona_preset_spoken = (
        getattr(suggestion, "persona_preset_spoken", "") or ""
    ).strip()
    persona_preset_label = (
        getattr(suggestion, "persona_preset_label", "") or ""
    ).strip()
    intent_preset_key = (getattr(suggestion, "intent_preset_key", "") or "").strip()
    intent_preset_label = (getattr(suggestion, "intent_preset_label", "") or "").strip()
    maps = _persona_maps()
    if maps is not None:
        display_map_raw = getattr(maps, "intent_display_map", {}) or {}
        display_map: dict[str, str] = {}
        try:
            display_map = {
                str(key or "").strip(): str(value or "").strip()
                for key, value in dict(display_map_raw).items()
                if str(key or "").strip()
            }
        except Exception:
            display_map = {}
        if display_map:
            intent_candidates = []
            if intent_display_meta:
                intent_candidates.extend(
                    [intent_display_meta, intent_display_meta.lower()]
                )
            normalized_intent = _normalize_intent(intent_text)
            if normalized_intent:
                intent_candidates.extend([normalized_intent, normalized_intent.lower()])
            if intent_preset_key:
                intent_candidates.extend([intent_preset_key, intent_preset_key.lower()])
            if intent_preset_label:
                intent_candidates.extend(
                    [intent_preset_label, intent_preset_label.lower()]
                )
            if intent_text:
                intent_candidates.extend([intent_text, intent_text.lower()])
            for candidate in intent_candidates:
                candidate_key = str(candidate or "").strip()
                if not candidate_key:
                    continue
                alias = display_map.get(candidate_key) or display_map.get(
                    candidate_key.lower()
                )
                if alias:
                    intent_display = alias
                    break
    if not intent_display and (intent_preset_label or intent_preset_key):
        intent_display = intent_preset_label or intent_preset_key
    raw_stance = (getattr(suggestion, "stance_command", "") or "").strip()

    stance_command = raw_stance if valid_stance_command(raw_stance) else ""
    generated_from_axes = False

    # If no explicit stance is provided, try to synthesise one from axes.
    if not stance_command:
        axis_parts = persona_bits
        if axis_parts:
            candidate = "model write " + " ".join(axis_parts)
            if valid_stance_command(candidate):
                stance_command = candidate
                generated_from_axes = True
    # If we still do not have a stance command but the axes match a persona
    # preset, surface the persona command so the Say section always shows a
    # concrete utterance (for example, "persona stake").
    if (not raw_stance or generated_from_axes) and persona_bits:
        preset = _match_persona_preset(voice_token, audience_token, tone_token)
        if preset is not None:
            stance_command = f"persona {preset.key}"

    preset_for_command = _preset_from_command(stance_command)
    if preset_for_command is None and persona_preset_key:
        maps = _persona_maps()
        if maps is not None:
            preset_candidate = maps.persona_presets.get(persona_preset_key)
            if preset_candidate is not None:
                preset_for_command = preset_candidate
                if not stance_command:
                    candidate_command = f"persona {persona_preset_key}"
                    if valid_stance_command(candidate_command):
                        stance_command = candidate_command

    persona_display_alias = (
        persona_preset_spoken or persona_preset_label or persona_preset_key
    )
    if persona_display_alias.lower().startswith("persona "):
        persona_display_alias = persona_display_alias[len("persona ") :].strip()
    persona_display = None
    if preset_for_command is not None:
        spoken = (preset_for_command.spoken or "").strip() or preset_for_command.key
        persona_display = f"persona {spoken}"
    if persona_display is None and persona_display_alias:
        persona_display = f"persona {persona_display_alias}"

    long_form = _persona_long_form(stance_command, persona_bits)
    # Prefer a model-write form for the Say line so it always matches grammar.
    primary_command = long_form or stance_command or ""
    secondary_command = None
    if (
        persona_display
        and primary_command
        and not primary_command.lower().startswith("persona ")
    ):
        secondary_command = persona_display
    if not primary_command:
        primary_command = persona_display or ""
    stance_display = primary_command
    if secondary_command:
        stance_display = f"{primary_command} ({secondary_command})"
    if stance_display and not stance_display.lower().startswith(
        ("model write", "persona ")
    ):
        axes_phrase = " ".join(persona_bits)
        if axes_phrase:
            stance_display = f"model write {axes_phrase}"
            if secondary_command:
                stance_display = f"{stance_display} ({secondary_command})"
    # Show companion intent command alongside the stance so users see both explicit commands.
    if intent_display and stance_command:
        stance_display = f"{stance_display} · intent {intent_display}"
    persona_axes_summary = " · ".join(persona_bits)

    why_text = (getattr(suggestion, "why", "") or "").strip()

    return {
        "persona_bits": persona_bits,
        "intent_text": intent_text,
        "intent_display": intent_display,
        "stance_command": stance_command,
        "stance_display": stance_display,
        "persona_display": persona_display or persona_axes_summary,
        "persona_axes_summary": persona_axes_summary,
        "stance_long_form": long_form,
        "why_text": why_text,
    }


def _log_scroll_event(event_type: str, evt) -> None:
    """Log diagnostic details for scroll events when deltas are zero."""

    global _scroll_debug_samples
    if _scroll_debug_samples >= 5:
        return
    try:
        attrs = {
            "event": event_type,
            "dy": getattr(evt, "dy", None),
            "wheel_y": getattr(evt, "wheel_y", None),
            "delta_y": getattr(evt, "delta_y", None),
        }
        delta_obj = getattr(evt, "delta", None)
        if delta_obj is not None:
            try:
                attrs["delta.y"] = getattr(delta_obj, "y", None)
                attrs["delta.x"] = getattr(delta_obj, "x", None)
            except Exception:
                attrs["delta_repr"] = repr(delta_obj)
        # Log a few other common fields to spot platform-specific names.
        for field in ("scroll_y", "scroll", "phase", "type", "name"):
            try:
                val = getattr(evt, field, None)
                if val is not None:
                    attrs[field] = val
            except Exception:
                pass
        try:
            attrs["repr"] = repr(evt)
        except Exception:
            pass
        try:
            attrs["dir"] = [k for k in dir(evt) if not k.startswith("_")]
        except Exception:
            pass
        _debug(f"scroll debug attrs={attrs}")
    except Exception:
        pass
    _scroll_debug_samples += 1


def _extract_scroll_delta(evt) -> float:
    """Best-effort scroll delta extractor across Talon event shapes."""

    dy = (
        getattr(evt, "dy", 0)
        or getattr(evt, "wheel_y", 0)
        or getattr(evt, "delta_y", 0)
        or getattr(getattr(evt, "delta", None) or {}, "y", 0)
    )
    if dy:
        return float(dy)

    # Talon ScrollEvent often surfaces pixels/degrees.
    try:
        pixels = getattr(evt, "pixels", None)
        if pixels is not None:
            py = getattr(pixels, "y", 0)
            if py:
                return float(py)
    except Exception:
        pass
    try:
        degrees = getattr(evt, "degrees", None)
        if degrees is not None:
            dy_deg = getattr(degrees, "y", 0)
            if dy_deg:
                return float(dy_deg)
    except Exception:
        pass
    return 0.0


def _install_callback_shim(c: canvas.Canvas) -> None:
    """Ensure the canvas exposes a _callbacks dict for tests and register shimming."""
    try:
        callbacks = getattr(c, "_callbacks", None)
    except Exception:
        callbacks = None
    if not isinstance(callbacks, dict):
        callbacks = {}
        try:
            setattr(c, "_callbacks", callbacks)
        except Exception:
            pass

    orig_register = getattr(c, "register", None)

    def _register(event: str, cb) -> None:
        try:
            callbacks.setdefault(event, []).append(cb)
        except Exception:
            pass
        if callable(orig_register):
            try:
                orig_register(event, cb)
            except Exception:
                pass

    try:
        c.register = _register  # type: ignore[attr-defined]
    except Exception:
        pass


def _ensure_suggestion_canvas() -> canvas.Canvas:
    """Create the suggestion canvas if needed and register handlers."""
    global _suggestion_canvas
    if _suggestion_canvas is None:
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
        except Exception as e:
            _debug(f"falling back to screen canvas: {e}")
            _suggestion_canvas = canvas.Canvas.from_screen(screen)

    if _suggestion_canvas is not None:
        apply_canvas_blocking(_suggestion_canvas)
        _install_callback_shim(_suggestion_canvas)

    callbacks = getattr(_suggestion_canvas, "_callbacks", {}) or {}
    # Ensure the callbacks dict is visible on the canvas for test inspection.
    try:
        setattr(_suggestion_canvas, "_callbacks", callbacks)
    except Exception:
        pass

    def _register_if_missing(event: str, cb) -> None:
        existing = callbacks.get(event)
        if existing:
            return
        callbacks.setdefault(event, []).append(cb)
        try:
            _suggestion_canvas.register(event, cb)
        except Exception as e:
            _debug(f"suggestion handler registration failed for '{event}': {e}")

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_suggestions(c)

    _register_if_missing("draw", _on_draw)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot, suggestion selection, hover, and drag."""
        try:
            global \
                _suggestion_hover_close, \
                _suggestion_hover_index, \
                _suggestion_drag_offset
            dy = 0.0
            rect = getattr(_suggestion_canvas, "rect", None)
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
                    _suggestion_drag_offset = (mouse_x - rect.x, mouse_y - rect.y)
                    return

            if event_type in ("mouseup", "mouse_up", "mouse_drag_end"):
                _suggestion_drag_offset = None
                return

            # Drag while moving with an active drag offset.
            if (
                event_type
                in ("mouse", "mousemove", "mouse_move", "mouse_drag", "mouse_dragged")
                and _suggestion_drag_offset is not None
            ):
                dx, dy = _suggestion_drag_offset
                new_x = mouse_x - dx
                new_y = mouse_y - dy
                try:
                    _suggestion_canvas.move(new_x, new_y)
                except Exception:
                    _suggestion_drag_offset = None
                    _debug("suggestion canvas drag move failed; clearing drag state")
                return

            # Vertical scroll via mouse wheel/trackpad when available.
            if event_type in (
                "mouse_scroll",
                "wheel",
                "scroll",
                "mouse_wheel",
                "mousewheel",
            ):
                dy = _extract_scroll_delta(evt)
                if dy:
                    _scroll_suggestions(dy)
                return
        except Exception as e:
            _debug(f"suggestion canvas mouse handler error: {e}")
            return

    _register_if_missing("mouse", _on_mouse)

    def _on_scroll(evt) -> None:  # pragma: no cover - visual only
        """Handle scroll events exposed separately from mouse callbacks."""
        try:
            raw = _extract_scroll_delta(evt)
            _scroll_suggestions(raw)
        except Exception as e:
            _debug(f"suggestion scroll handler error: {e}")

    for evt_name in ("scroll", "wheel", "mouse_scroll", "mouse_wheel", "mousewheel"):
        _register_if_missing(evt_name, _on_scroll)

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


def _scroll_suggestions(raw_delta: float) -> None:  # pragma: no cover - visual only
    """Apply a scroll delta to the suggestion list."""
    try:
        global _scroll_state_debug_samples
        rect = getattr(_suggestion_canvas, "rect", None)

        if rect is None:
            return
        delta = float(raw_delta or 0.0)
        if not delta:
            return
        line_h = 20
        approx_char = 8
        ctx = suggestion_context()
        stance_lines = stance_defaults_lines(ctx or None)
        body_top = rect.y + 60 + line_h * 2
        if stance_lines:
            body_top += line_h  # label
            body_top += line_h * len(stance_lines)
            body_top += line_h // 2
        # Account for the axes legend row so scroll math matches the draw path.
        if SuggestionGUIState.suggestions:
            legend_lines = _wrap_lines_count(
                _AXES_LEGEND,
                rect.x + 40 + _SECONDARY_INDENT,
                rect,
                approx_char,
                line_h,
            )
            if legend_lines:
                body_top += line_h * legend_lines
                body_top += line_h // 2
        body_bottom = rect.y + rect.height - line_h * 4
        visible_height = max(body_bottom - body_top, line_h * 4)
        measured_heights = [
            _measure_suggestion_height(s, rect.x + 40, rect, approx_char, line_h)
            for s in SuggestionGUIState.suggestions
        ]
        total_content_height = sum(measured_heights)
        # Match the draw path slack so the handler and renderer share bounds.
        max_scroll = max(total_content_height - visible_height + line_h * 6, 0)
        # Further slow the scroll sensitivity so wheel/trackpad deltas move the
        # list in smaller steps; Talon surfaces high raw deltas on some platforms.
        old_scroll = float(getattr(SuggestionCanvasState, "scroll_y", 0.0) or 0.0)
        new_scroll = old_scroll - delta * 10.0
        clamped = clamp_scroll(new_scroll, max_scroll)
        SuggestionCanvasState.scroll_y = clamped
        # Lightweight debug logging so we can inspect scroll behaviour at the edges
        if _scroll_state_debug_samples < 50:
            _debug(
                "scroll delta=%s old=%s new=%s clamped=%s max_scroll=%s visible_height=%s total_content_height=%s"
                % (
                    delta,
                    old_scroll,
                    new_scroll,
                    clamped,
                    max_scroll,
                    visible_height,
                    total_content_height,
                )
            )
            _scroll_state_debug_samples += 1
    except Exception as e:
        _debug(f"suggestion scroll handler error: {e}")


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
    line_h = 20
    approx_char = 8

    def _draw_wrapped(
        text: str,
        x_pos: int,
        y_pos: int,
        indent: int = 0,
        visible_top: Optional[int] = None,
        visible_bottom: Optional[int] = None,
        color: Optional[str] = None,
        max_chars_override: Optional[int] = None,
    ) -> int:
        """Draw text wrapped to the panel width and return new y."""
        x_draw = x_pos + indent
        lines = _wrap_lines_count(
            text,
            x_draw,
            rect,
            approx_char,
            line_h,
            max_chars_override=max_chars_override,
        )
        if not lines:
            return y_pos
        words = text.split()
        max_chars = max_chars_override or 80
        try:
            if rect is not None and hasattr(rect, "width") and hasattr(rect, "x"):
                right_margin = rect.x + rect.width - 40
                available_px = max(right_margin - x_draw, 160)
                candidate = max(int(available_px // approx_char), 20)
                max_chars = (
                    min(max_chars, candidate) if max_chars_override else candidate
                )
        except Exception:
            max_chars = max_chars_override or 80

        current_line: list[str] = []
        current_len = 0
        for word in words:
            extra = len(word) if not current_line else len(word) + 1
            if current_line and current_len + extra > max_chars:
                if (
                    visible_top is None
                    or visible_bottom is None
                    or (y_pos >= visible_top and y_pos <= visible_bottom - line_h)
                ):
                    old_color = (
                        getattr(paint, "color", None) if paint is not None else None
                    )
                    if paint is not None and color:
                        paint.color = color
                    draw_text(" ".join(current_line), x_draw, y_pos)
                    if paint is not None and color:
                        paint.color = old_color or "000000"
                y_pos += line_h
                current_line = [word]
                current_len = len(word)
            else:
                current_line.append(word)
                current_len += extra
        if current_line:
            if (
                visible_top is None
                or visible_bottom is None
                or (y_pos >= visible_top and y_pos <= visible_bottom - line_h)
            ):
                old_color = getattr(paint, "color", None) if paint is not None else None
                if paint is not None and color:
                    paint.color = color
                draw_text(" ".join(current_line), x_draw, y_pos)
                if paint is not None and color:
                    paint.color = old_color or "000000"
            y_pos += line_h
        return y_pos

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

    # Context header showing stance/defaults (prefer the context captured at
    # suggestion time; fall back to current stance/default settings).
    ctx = suggestion_context()
    stance_lines = stance_defaults_lines(ctx or None)
    # Hide the context block entirely if everything is empty.
    show_context = any(
        "Voice=" in line and "–" not in line for line in stance_lines
    ) or any(
        "Defaults" in line
        and not line.endswith("Defaults: C=– S=– M=– F=– Ch=– Provider=–")
        for line in stance_lines
    )
    if stance_lines and show_context:
        label = "Context (stance/defaults):"
        draw_text(label, x, y)
        y += line_h
        filtered = [
            line
            for line in stance_lines
            if not line.endswith("Defaults: C=– S=– M=– F=– Ch=– Provider=–")
        ]
        for line in filtered:
            y = _draw_wrapped(line, x, y, indent=_SECONDARY_INDENT)
        y += line_h // 2

    # Axes legend for quick decoding of contract axes.
    if suggestions:
        y = _draw_wrapped(_AXES_LEGEND, x, y, indent=_SECONDARY_INDENT)
        y += line_h // 2

    if not suggestions:
        draw_text("No suggestions available. Run 'model run suggest' first.", x, y)
        return

    # No global stance hint here: keep the panel focused on per-suggestion
    # contract and stance so it is clear which commands apply to which row.

    # Dynamic heights to avoid overlap when stance/why text runs long.
    body_top = y
    if rect is not None and hasattr(rect, "height"):
        body_bottom = rect.y + rect.height - line_h * 4
    else:
        body_bottom = body_top + 1_000_000
    visible_height = max(body_bottom - body_top, line_h * 4)

    measured_heights = [
        _measure_suggestion_height(suggestion, x, rect, approx_char, line_h)
        for suggestion in suggestions
    ]
    total_content_height = sum(measured_heights)
    # Add a slack buffer so final rows can fully clear the visible area even
    # when rounding/measurement errors accumulate or line measurement
    # underestimates wrap. A few lines of slack avoids clipping the last row.
    max_scroll = max(total_content_height - visible_height + line_h * 6, 0)
    scroll_y = clamp_scroll(SuggestionCanvasState.scroll_y, max_scroll)
    SuggestionCanvasState.scroll_y = scroll_y

    current_y = body_top - scroll_y
    # Render each visible suggestion as a clickable row.
    for index, suggestion in enumerate(suggestions):
        row_height = (
            measured_heights[index] if index < len(measured_heights) else line_h * 6
        )
        row_start = current_y
        row_end = current_y + row_height
        # Skip rows that are fully above the visible body area.
        if row_end < body_top:
            current_y += row_height
            continue
        if row_start >= body_bottom:
            break

        row_draw_start = row_start
        row_draw_end = row_draw_start + row_height

        label_y = row_draw_start
        label = f"[{suggestion.name}]"
        label_width = len(label) * approx_char
        row_top = label_y - line_h
        row_bottom = label_y + line_h
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

        stop_rendering = False
        if label_y >= body_top and label_y <= body_bottom - line_h:
            draw_text(label, x, label_y)
            if (
                _suggestion_hover_index == index
                and rect is not None
                and paint is not None
            ):
                try:
                    underline_rect = Rect(x, label_y + 4, label_width, 1)
                    c.draw_rect(underline_rect)
                except Exception:
                    pass
        row_y = label_y + line_h
        if row_y >= body_bottom:
            stop_rendering = True

        source_key = getattr(GPTState, "last_suggest_source", "")
        grammar_phrase = suggestion_grammar_phrase(
            suggestion.recipe, source_key, SOURCE_SPOKEN_MAP
        )
        if not stop_rendering:
            row_y = _draw_wrapped(
                f"Say: {grammar_phrase}",
                x + 4,
                row_y,
                indent=0,
                visible_top=body_top,
                visible_bottom=body_bottom,
            )
            if row_y >= body_bottom:
                stop_rendering = True
            if not stop_rendering:
                row_y += line_h // 2

        (
            static_prompt,
            completeness,
            scope,
            method,
            form,
            channel,
            directional,
        ) = _parse_recipe(suggestion.recipe)
        axes_text = _axes_summary(
            completeness, scope, method, form, channel, directional
        )
        if axes_text and not stop_rendering:
            row_y = _draw_wrapped(
                f"Axes: {axes_text}",
                x + 4,
                row_y,
                indent=_SECONDARY_INDENT,
                visible_top=body_top,
                visible_bottom=body_bottom,
                max_chars_override=_AXES_WRAP_MAX_CHARS,
            )
            if row_y >= body_bottom:
                stop_rendering = True
            if not stop_rendering:
                row_y += line_h // 3

        # Use the remaining row height to show an optional, compact stance
        # and explanation. Stance is expressed in terms of Persona/Intent axes
        # plus a flexible, voice-friendly stance_command when present.
        raw_stance = (suggestion.stance_command or "").strip()
        stance_info = _suggestion_stance_info(suggestion)
        persona_bits = stance_info["persona_bits"]
        intent_display = stance_info["intent_display"]
        persona_display = stance_info.get("persona_display", "")
        persona_axes_summary = stance_info.get("persona_axes_summary", "")
        stance_text = stance_info.get("stance_display", stance_info["stance_command"])
        stance_long_form = stance_info.get("stance_long_form", "")
        why_text = stance_info["why_text"]
        reasoning_text = (getattr(suggestion, "reasoning", "") or "").strip()
        if raw_stance and not stance_info["stance_command"]:
            _debug(
                f"invalid stance_command for suggestion '{suggestion.name}': {raw_stance}"
            )
        has_persona_axes = bool(persona_bits)
        has_intent_axis = bool(intent_display)
        has_stance_command = bool(stance_text)
        has_why = bool(why_text)
        has_reasoning = bool(reasoning_text)
        primary_command = (
            stance_text
            or persona_display
            or stance_info.get("stance_command", "")
            or ""
        ).strip()
        if not primary_command and persona_bits:
            primary_command = "model write " + " ".join(persona_bits)

        if (
            has_persona_axes
            or has_intent_axis
            or has_stance_command
            or has_why
            or has_reasoning
        ) and not stop_rendering:
            row_y += line_h
            # Put the concrete voice command first so users know exactly what to say.
            intent_command = f"intent {intent_display}" if has_intent_axis else ""
            if intent_command and intent_command.lower() in primary_command.lower():
                intent_command = ""
            say_parts = [part for part in (primary_command, intent_command) if part]
            if say_parts:
                row_y = _draw_wrapped(
                    f"Say: {' · '.join(say_parts)}",
                    x + 4,
                    row_y,
                    indent=0,
                    visible_top=body_top,
                    visible_bottom=body_bottom,
                )
                if row_y >= body_bottom:
                    stop_rendering = True
            # Only show the long-form line when it adds detail beyond the
            # primary command and we do not already have a persona preset label.
            if (
                stance_long_form
                and not persona_display
                and stance_long_form.lower() != primary_command.lower()
            ):
                row_y = _draw_wrapped(
                    f"({stance_long_form})",
                    x + 4 + _SECONDARY_INDENT,
                    row_y,
                    indent=0,
                    visible_top=body_top,
                    visible_bottom=body_bottom,
                    color=_REASONING_COLOR,
                )
                if row_y >= body_bottom:
                    stop_rendering = True

            if (has_persona_axes or has_intent_axis) and not stop_rendering:
                if row_y >= body_top and row_y <= body_bottom - line_h:
                    persona_line = persona_axes_summary
                    if (
                        persona_display
                        and persona_axes_summary
                        and persona_display != persona_axes_summary
                    ):
                        persona_line = f"{persona_display} ({persona_axes_summary})"
                    elif persona_display and not persona_line:
                        persona_line = persona_display
                    # Skip the Who line when it would duplicate the primary command verbatim.
                    if (
                        persona_line
                        and primary_command
                        and persona_line.lower() == primary_command.lower()
                    ):
                        persona_line = ""
                    if persona_line:
                        persona_line = f"Who: {persona_line}"
                    intent_line = f"Intent: {intent_display}" if has_intent_axis else ""
                    spacer = "   " if persona_line and intent_line else ""
                    draw_text(
                        f"{persona_line}{spacer}{intent_line}",
                        x + 4 + _SECONDARY_INDENT,
                        row_y,
                    )
                row_y += line_h
                if row_y >= body_bottom:
                    stop_rendering = True
            if has_why and not stop_rendering:
                # Keep Why reasonably compact; wrap long lines.
                row_y += line_h // 2
                reason_text = f"{_WHY_REASON_LABEL} {why_text}"
                row_y = _draw_wrapped(
                    reason_text,
                    x + 4,
                    row_y,
                    indent=_SECONDARY_INDENT,
                    visible_top=body_top,
                    visible_bottom=body_bottom,
                    color=_WHY_COLOR,
                    max_chars_override=_AXES_WRAP_MAX_CHARS,
                )
                if row_y >= body_bottom:
                    stop_rendering = True
            if has_reasoning and not stop_rendering:
                reason_text = f"Reasoning: {reasoning_text}"
                row_y = _draw_wrapped(
                    reason_text,
                    x + 4 + _REASONING_INDENT,
                    row_y,
                    indent=0,
                    visible_top=body_top,
                    visible_bottom=body_bottom,
                    color=_REASONING_COLOR,
                    max_chars_override=_AXES_WRAP_MAX_CHARS,
                )
                if row_y >= body_bottom:
                    stop_rendering = True
        # Lightweight spacer below each row; advance by measured height so
        # scroll math stays consistent even when we clip rendering.
        if not stop_rendering:
            # Subtle separator line to delineate suggestions without heavy boxes.
            if rect is not None and paint is not None:
                sep_y = row_y + line_h // 6
                max_y = body_bottom - line_h // 4
                if sep_y < max_y:
                    old_color = getattr(paint, "color", None)
                    paint.color = "EEEEEE"
                    try:
                        # Align to text column width (same inset as content).
                        c.draw_rect(Rect(x, sep_y, rect.width - (x - rect.x) * 2, 1))
                    except Exception:
                        pass
                    if old_color is not None:
                        paint.color = old_color
            row_y += line_h // 3
        current_y = row_draw_end
        if stop_rendering:
            break

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
    try:
        maps = persona_intent_maps()
    except Exception:
        _debug(
            "persona_intent_maps unavailable; falling back to raw suggestion metadata"
        )
        maps = None

    hydrated: list[Suggestion] = []
    persona_presets = (
        getattr(maps, "persona_presets", {}) or {} if maps is not None else {}
    )
    persona_aliases = (
        getattr(maps, "persona_preset_aliases", {}) or {} if maps is not None else {}
    )
    intent_presets = (
        getattr(maps, "intent_presets", {}) or {} if maps is not None else {}
    )
    intent_aliases = (
        getattr(maps, "intent_preset_aliases", {}) or {} if maps is not None else {}
    )
    intent_synonyms = (
        getattr(maps, "intent_synonyms", {}) or {} if maps is not None else {}
    )
    intent_display_map = (
        getattr(maps, "intent_display_map", {}) or {} if maps is not None else {}
    )

    raw_suggestions = tuple(suggestion_entries_with_metadata())
    if not raw_suggestions:
        SuggestionGUIState.suggestions = []
        return

    for item in raw_suggestions:
        name = str(item.get("name") or "").strip()
        recipe = str(item.get("recipe") or "").strip()
        if not name or not recipe:
            continue

        data = dict(item)
        if maps is not None:
            persona_key = str(data.get("persona_preset_key") or "").strip()
            persona_label = str(data.get("persona_preset_label") or "").strip()
            persona_spoken = str(data.get("persona_preset_spoken") or "").strip()
            preset = None
            canonical_persona = ""
            if persona_key:
                canonical_persona = persona_key
                preset = persona_presets.get(canonical_persona)
            else:
                for alias in (persona_spoken, persona_label):
                    alias_clean = str(alias or "").strip()
                    if not alias_clean:
                        continue
                    alias_lower = alias_clean.lower()
                    alias_norm = _normalise_alias_token(alias_clean)
                    canonical = ""
                    for lookup in filter(None, [alias_lower, alias_norm]):
                        canonical = persona_aliases.get(lookup, "")
                        if canonical:
                            preset = persona_presets.get(canonical)
                            if preset is not None:
                                canonical_persona = canonical
                                break
                    if canonical_persona:
                        break
                    for lookup in filter(None, [alias_clean, alias_lower, alias_norm]):
                        candidate = persona_presets.get(lookup)
                        if candidate is not None:
                            preset = candidate
                            canonical_persona = getattr(candidate, "key", "") or ""
                            break
                    if canonical_persona:
                        break
            if preset is not None:
                target_key = preset.key
                target_label = preset.label or target_key
                target_spoken = preset.spoken or target_label or target_key
                if persona_key != target_key:
                    data["persona_preset_key"] = target_key
                if target_label and persona_label != target_label:
                    data["persona_preset_label"] = target_label
                if target_spoken and persona_spoken != target_spoken:
                    data["persona_preset_spoken"] = target_spoken
                if not str(data.get("persona_voice") or "").strip():
                    data["persona_voice"] = preset.voice or ""
                if not str(data.get("persona_audience") or "").strip():
                    data["persona_audience"] = preset.audience or ""
                if not str(data.get("persona_tone") or "").strip():
                    data["persona_tone"] = preset.tone or ""

            intent_key = str(data.get("intent_preset_key") or "").strip()
            intent_purpose = str(data.get("intent_purpose") or "").strip()
            intent_display = str(data.get("intent_display") or "").strip()
            intent_canonical = ""
            if intent_key:
                intent_canonical = intent_key
            else:
                for alias in (intent_display, intent_purpose):
                    alias_clean = str(alias or "").strip()
                    if not alias_clean:
                        continue
                    alias_lower = alias_clean.lower()
                    alias_norm = _normalise_alias_token(alias_clean)
                    for lookup in filter(None, [alias_lower, alias_norm]):
                        candidate = (
                            intent_aliases.get(lookup)
                            or intent_synonyms.get(lookup)
                            or ""
                        )
                        if candidate:
                            intent_canonical = candidate
                            break
                    if intent_canonical:
                        break
            if not intent_canonical and intent_purpose:
                normalized_purpose = (
                    _normalise_alias_token(intent_purpose) or intent_purpose
                )
                intent_canonical = (
                    intent_synonyms.get(normalized_purpose)
                    or intent_aliases.get(normalized_purpose)
                    or intent_synonyms.get(intent_purpose.lower())
                    or intent_purpose
                )
            intent_preset = (
                intent_presets.get(intent_canonical) if intent_canonical else None
            )
            if intent_preset is None and intent_presets:
                for alias in (intent_display, intent_purpose):
                    alias_clean = str(alias or "").strip()
                    if not alias_clean:
                        continue
                    alias_lower = alias_clean.lower()
                    alias_norm = _normalise_alias_token(alias_clean)
                    for preset_candidate in intent_presets.values():
                        preset_key = (
                            getattr(preset_candidate, "key", "") or ""
                        ).strip()
                        preset_label = (
                            getattr(preset_candidate, "label", "") or ""
                        ).strip()
                        preset_intent = (
                            getattr(preset_candidate, "intent", "") or ""
                        ).strip()
                        preset_keys = {
                            value
                            for value in (
                                preset_key.lower() if preset_key else "",
                                preset_label.lower() if preset_label else "",
                                preset_intent.lower() if preset_intent else "",
                                _normalise_alias_token(preset_label)
                                if preset_label
                                else "",
                                _normalise_alias_token(preset_intent)
                                if preset_intent
                                else "",
                            )
                            if value
                        }
                        if alias_lower in preset_keys or (
                            alias_norm and alias_norm in preset_keys
                        ):
                            intent_preset = preset_candidate
                            intent_canonical = preset_key
                            break
                    if intent_preset is not None:
                        break
            if intent_preset is not None:
                target_key = intent_preset.key
                target_label = intent_preset.label or target_key
                if intent_key != target_key:
                    data["intent_preset_key"] = target_key
                current_label = str(data.get("intent_preset_label") or "").strip()
                if target_label and current_label != target_label:
                    data["intent_preset_label"] = target_label
                if not intent_purpose:
                    data["intent_purpose"] = intent_preset.intent
                display_value = intent_display_map.get(
                    intent_preset.key
                ) or intent_display_map.get(intent_preset.intent)
                if display_value:
                    data["intent_display"] = display_value

        hydrated.append(
            Suggestion(
                name=name,
                recipe=recipe,
                persona_voice=str(data.get("persona_voice") or ""),
                persona_audience=str(data.get("persona_audience") or ""),
                persona_tone=str(data.get("persona_tone") or ""),
                intent_purpose=str(data.get("intent_purpose") or ""),
                stance_command=str(data.get("stance_command") or ""),
                why=str(data.get("why") or ""),
                reasoning=str(data.get("reasoning") or ""),
                persona_preset_key=str(data.get("persona_preset_key") or ""),
                persona_preset_label=str(data.get("persona_preset_label") or ""),
                persona_preset_spoken=str(data.get("persona_preset_spoken") or ""),
                intent_preset_key=str(data.get("intent_preset_key") or ""),
                intent_preset_label=str(data.get("intent_preset_label") or ""),
                intent_display=str(data.get("intent_display") or ""),
            )
        )

    SuggestionGUIState.suggestions = hydrated


def _run_suggestion(suggestion: Suggestion) -> None:
    """Execute a suggested recipe as if spoken via the model grammar."""
    (
        static_prompt,
        completeness,
        scope,
        method,
        form,
        channel,
        directional,
    ) = _parse_recipe(suggestion.recipe)
    if not static_prompt:
        actions.app.notify("Suggestion has no static prompt; cannot run")
        return
    if not directional:
        notify(
            "GPT: Suggestion has no directional lens; run a directional recipe (fog/fig/dig/ong/rog/bog/jog)."
        )
        return

    # Apply axis caps so Form/Channel remain singletons and scope/method obey soft caps.
    scope_tokens = _canonicalise_axis_tokens("scope", scope.split())
    method_tokens = _canonicalise_axis_tokens("method", method.split())
    form_tokens = _canonicalise_axis_tokens("form", form.split())
    channel_tokens = _canonicalise_axis_tokens("channel", channel.split())
    scope = " ".join(scope_tokens)
    method = " ".join(method_tokens)
    form = " ".join(form_tokens[:1])
    channel = " ".join(channel_tokens[:1])

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
    if form:
        setattr(match, "formModifier", _axis_value(form, FORM_MAP))
    if channel:
        setattr(match, "channelModifier", _axis_value(channel, CHANNEL_MAP))
    if directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(directional, DIRECTIONAL_MAP),
        )

    please_prompt = safe_model_prompt(match)
    if not please_prompt:
        return

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
        form,
        channel,
        directional,
    )


@mod.action_class
class UserActions:
    def model_prompt_recipe_suggestions_gui_open():
        """Open the prompt recipe suggestion canvas for the last suggestions."""
        if _reject_if_request_in_flight():
            return
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return

        # Close related menus to avoid overlapping overlays.
        close_common_overlays(actions.user)

        _open_suggestion_canvas()
        ctx.tags = ["user.model_suggestion_window_open"]

    def model_prompt_recipe_suggestions_gui_close():
        """Close the prompt recipe suggestion canvas."""
        if _reject_if_request_in_flight():
            return
        _close_suggestion_canvas()
        ctx.tags = []

    def model_prompt_recipe_suggestions_run_index(index: int):
        """Run a suggestion by 1-based index from the cached list."""
        if _reject_if_request_in_flight():
            return
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return
        if index <= 0 or index > len(SuggestionGUIState.suggestions):
            actions.app.notify("Suggestion index out of range")
            return

        suggestion = SuggestionGUIState.suggestions[index - 1]
        _run_suggestion(suggestion)
