import json
import os
import threading
from typing import List, Optional, Union, cast
import re

from ..lib.talonSettings import (
    ApplyPromptConfiguration,
    DEFAULT_COMPLETENESS_VALUE,
    PassConfiguration,
    _map_axis_tokens,
    _axis_tokens_to_string,
    _canonicalise_axis_tokens,
    _tokens_list,
    modelPrompt,
    safe_model_prompt,
)

from ..lib.axisMappings import axis_docs_map
from ..lib.staticPromptConfig import STATIC_PROMPT_CONFIG

try:
    from ..lib.axisCatalog import (
        axis_catalog,
        get_static_prompt_axes,
        get_static_prompt_profile,
        static_prompt_catalog,
        static_prompt_description_overrides,
    )
except ImportError:  # Talon may have a stale runtime without axisCatalog

    def get_static_prompt_profile(name: str):
        return STATIC_PROMPT_CONFIG.get(name)

    def get_static_prompt_axes(name: str) -> dict[str, object]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, object] = {}
        for axis in ("completeness", "scope", "method", "form", "channel"):
            value = profile.get(axis)
            if value:
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

    def static_prompt_catalog(static_prompt_list_path=None):
        talon_tokens = []
        try:
            current_dir = os.path.dirname(__file__)
            path = os.path.join(current_dir, "lists", "staticPrompt.talon-list")
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if not s or s.startswith("#") or s.startswith("list:") or s == "-":
                        continue
                    if ":" not in s:
                        continue
                    key, _ = s.split(":", 1)
                    key = key.strip()
                    if key:
                        talon_tokens.append(key)
        except FileNotFoundError:
            pass
        profiled = []
        for name in STATIC_PROMPT_CONFIG.keys():
            profiled.append(
                {
                    "name": name,
                    "description": STATIC_PROMPT_CONFIG.get(name, {}).get(
                        "description", ""
                    ),
                    "axes": get_static_prompt_axes(name),
                }
            )
        profiled_names = {entry["name"] for entry in profiled}
        unprofiled_tokens = [
            token for token in talon_tokens if token not in profiled_names
        ]
        return {
            "profiled": profiled,
            "talon_list_tokens": talon_tokens,
            "unprofiled_tokens": unprofiled_tokens,
        }

    def static_prompt_description_overrides() -> dict[str, str]:
        """Fallback description overrides when helpers are unavailable.

        Mirrors the semantics of lib.staticPromptConfig.static_prompt_description_overrides
        so README/help surfaces see a consistent view in older Talon runtimes.
        """
        overrides: dict[str, str] = {}
        for name, cfg in STATIC_PROMPT_CONFIG.items():
            description = str(cfg.get("description", "")).strip()
            if description:
                overrides[name] = description
        return overrides

    def axis_catalog():
        # Minimal fallback: expose axisConfig tokens without Talon list parsing.
        return {
            "axes": AXIS_KEY_TO_VALUE,
            "axis_list_tokens": {},
            "static_prompts": static_prompt_catalog(),
            "static_prompt_descriptions": static_prompt_description_overrides(),
            "static_prompt_profiles": STATIC_PROMPT_CONFIG,
        }


from ..lib.modelDestination import (
    Browser,
    Clipboard,
    Default,
    ModelDestination,
    PromptPayload,
    Silent,
    create_model_destination,
)
from ..lib.modelSource import ModelSource, create_model_source
from talon import Context, Module, actions, clip, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    format_message,
    format_messages,
    notify,
    send_request,
    messages_to_string,
    append_request_messages,
)

from ..lib.modelState import GPTState
from ..lib.modelTypes import GPTSystemPrompt
from ..lib.promptPipeline import PromptPipeline, PromptResult
from ..lib.promptSession import PromptSession
from ..lib.recursiveOrchestrator import RecursiveOrchestrator
from ..lib.modelPatternGUI import (
    DIRECTIONAL_MAP as _DIRECTIONAL_MAP,
    _axis_value_from_token,
)
from ..lib.axisMappings import axis_key_to_value_map_for
from ..lib.personaConfig import persona_docs_map
from ..lib.stanceValidation import valid_stance_command as _valid_stance_command
from ..lib.suggestionCoordinator import (
    record_suggestions,
    last_recipe_snapshot,
    recipe_header_lines_from_snapshot,
    set_last_recipe_from_selection,
    last_recap_snapshot,
    clear_recap_state,
    suggestion_source,
)

# Backward-compatible alias for directional map used during parsing.
DIRECTIONAL_MAP = _DIRECTIONAL_MAP
from ..lib.requestState import RequestPhase
from ..lib.requestBus import (
    emit_begin_send,
    emit_cancel,
    emit_complete,
    emit_fail,
    current_state,
    set_controller,
)
from ..lib.requestController import RequestUIController

# Ensure a default request UI controller is registered so cancel events have a sink.
try:
    from ..lib import requestUI  # noqa: F401
except Exception:
    pass


def _canonical_axis_value(axis: str, raw: str) -> str:
    """Return a canonical axis token for a raw value or empty if unknown.

    Only accept known axis keys; do not attempt description reverse-lookups.
    """
    if not raw:
        return ""
    raw_s = str(raw).strip()
    if not raw_s:
        return ""
    lower = raw_s.lower()
    try:
        mapping = axis_key_to_value_map_for(axis)
    except Exception:
        mapping = {}
    for key, desc in mapping.items():
        key_s = str(key).strip()
        if not key_s:
            continue
        if lower == key_s.lower():
            return key_s
    return ""


def _canonical_persona_value(axis: str, raw: str) -> str:
    """Return a canonical persona/intent token for a raw value or empty if unknown.

    Only accept known axis keys; do not attempt description reverse-lookups.
    """
    if not raw:
        return ""
    raw_s = str(raw).strip()
    if not raw_s:
        return ""
    lower = raw_s.lower()
    if axis == "intent":
        try:
            from ..lib.personaConfig import normalize_intent_token
        except Exception:
            pass
        else:
            raw_s = normalize_intent_token(raw_s)
            lower = raw_s.lower()
    try:
        docs = persona_docs_map(axis)
    except Exception:
        docs = {}
    for key, desc in docs.items():
        key_s = str(key).strip()
        if key_s and lower == key_s.lower():
            return key_s
    return ""


def _suggest_context_snapshot(sys_prompt) -> dict[str, str]:
    """Return canonical persona/intent + contract defaults for suggest."""

    def _val(attr: str, canonical_axis: Optional[str] = None, persona_axis: Optional[str] = None) -> str:
        if not sys_prompt:
            return ""
        raw = str(getattr(sys_prompt, attr, "") or "").strip()
        if persona_axis:
            return _canonical_persona_value(persona_axis, raw)
        if canonical_axis:
            return _canonical_axis_value(canonical_axis, raw)
        return raw

    return {
        "voice": _val("voice", persona_axis="voice"),
        "audience": _val("audience", persona_axis="audience"),
        "tone": _val("tone", persona_axis="tone"),
        "intent": _val("intent", persona_axis="intent"),
        "completeness": _val("completeness", canonical_axis="completeness"),
        "scope": _val("scope", canonical_axis="scope"),
        "method": _val("method", canonical_axis="method"),
        "form": _val("form", canonical_axis="form"),
        "channel": _val("channel", canonical_axis="channel"),
    }


def _suggest_hydrated_context(sys_prompt) -> dict[str, str]:
    """Return hydrated persona/intent + contract defaults for suggest prompt text.

    Uses getters (so defaults are applied) and keeps raw hydrated strings
    without mapping back to tokens.
    """

    def _val(attr: str) -> str:
        if not sys_prompt:
            return ""
        getter = getattr(sys_prompt, f"get_{attr}", None)
        if callable(getter):
            try:
                raw = getter()
                if raw is not None:
                    return str(raw).strip()
            except Exception:
                pass
        raw = getattr(sys_prompt, attr, "")
        return str(raw or "").strip()

    return {
        "voice": _val("voice"),
        "audience": _val("audience"),
        "tone": _val("tone"),
        "intent": _val("intent"),
        "completeness": _val("completeness"),
        "scope": _val("scope"),
        "method": _val("method"),
        "form": _val("form"),
        "channel": _val("channel"),
    }


def _format_context_lines(snapshot: dict[str, str]) -> list[str]:
    """Build formatted context lines from a context snapshot dict."""
    if not snapshot:
        return []
    lines: list[str] = []
    persona_bits = [
        snapshot.get("voice", "").strip(),
        snapshot.get("audience", "").strip(),
        snapshot.get("tone", "").strip(),
    ]
    persona_bits = [b for b in persona_bits if b]
    if persona_bits:
        lines.append("Persona (Who): " + " · ".join(persona_bits))
    if snapshot.get("intent"):
        lines.append(f"Intent (Why): {snapshot['intent']}")
    axis_bits: list[str] = []
    for label, key in (
        ("Completeness", "completeness"),
        ("Scope", "scope"),
        ("Method", "method"),
        ("Form", "form"),
        ("Channel", "channel"),
    ):
        val = snapshot.get(key, "").strip()
        if val:
            axis_bits.append(f"{label}: {val}")
    if axis_bits:
        lines.append("Defaults: " + " · ".join(axis_bits))
    return lines


def _suggest_prompt_text(
    axis_docs: str,
    persona_intent_docs: str,
    static_prompt_docs: str,
    prompt_subject: str,
    content_text: str,
    context_lines: list[str],
) -> str:
    """Build the user_text for suggest requests (exposed for characterization tests)."""
    context_block = (
        "Current persona/intent/defaults sent with this request (apply when helpful):\n"
        + "\n".join(f"- {line}" for line in context_lines)
        + "\n\n"
        if context_lines
        else ""
    )

    return (
        "You are a prompt recipe assistant for the Talon `model` command.\n"
        "Based on the subject and content below, suggest 3 to 5 concrete prompt recipes.\n\n"
        "You MUST output ONLY JSON with this exact top-level shape (no markdown, backticks, or extra text):\n\n"
        "{\n"
        '  "suggestions": [\n'
        "    {\n"
        '      "name": string,\n'
        '      "recipe": string,\n'
        '      "persona_voice": string,\n'
        '      "persona_audience": string,\n'
        '      "persona_tone": string,\n'
        '      "intent_purpose": string,\n'
        '      "stance_command": string,\n'
        '      "reasoning": string,\n'
        '      "why": string\n'
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Fields:\n"
        "- name: short human-friendly label for the suggestion.\n"
        "- recipe: a contract-only axis string ordered as\n"
        "  '<staticPrompt> [· <completeness>] [· <scopeTokens>] [· <methodTokens>] [· <formToken>] [· <channelToken>] · <directional>'.\n"
        "  Include completeness/scope/method/form/channel only when they add value;\n"
        "  omit any segment entirely rather than leaving empty slots.\n"
        "- persona_voice / persona_audience / persona_tone / intent_purpose:\n"
        "  optional Persona/Intent axis tokens (Who/Why) using ONLY the values\n"
        "  from the Persona/Intent token lists below. Leave as an empty string\n"
        '  (\"\") when you cannot reasonably express the stance with these tokens.\n'
        "- The stance/defaults above were provided with this request. Prefer keeping\n"
        "  them. Only change persona_voice/persona_audience/persona_tone/\n"
        "  intent_purpose when it clearly improves the subject, and justify every\n"
        "  change (why the provided value is insufficient) in reasoning. If you keep\n"
        "  a provided value, say so explicitly. Keep intent_purpose by default; only\n"
        "  change intent when the provided intent conflicts with the subject or is\n"
        "  clearly wrong.\n"
        "- stance_command: a single-line, voice-friendly command that a user could\n"
        "  speak to set this stance. Valid forms are:\n"
        "  * Preferred (always valid):\n"
        "    'model write <persona_voice> <persona_audience> <persona_tone>'\n"
        "    using exactly the persona_voice/persona_audience/persona_tone tokens\n"
        "    you chose for this suggestion.\n"
        "    Include at least one persona axis; never output 'model write',\n"
        "    'model write plan', 'model write for teaching', or any other intent\n"
        "    token inside stance_command.\n"
        "  * Optional (only when the stance matches a known preset):\n"
        "    'persona <personaPreset>' where <personaPreset> is a name from the\n"
        "    Persona preset list (for example, 'persona teach junior dev').\n"
        "  Do NOT include intent tokens or preset names in stance_command; intent is\n"
        "  a separate `intent <intentPreset>` command captured via intent_purpose.\n"
        "  Never emit 'persona' followed directly by raw axis tokens; if you cannot\n"
        "  use a preset name, fall back to the 'model write' form above.\n"
        "- reasoning: 1–2 sentences describing why you chose this recipe/stance,\n"
        "  focusing on the axis token choices (especially staticPrompt + directional)\n"
        "  and clearly stating whether you kept or changed the provided stance/intent.\n"
        "  Start reasoning with an explicit stance/intent decision, for example:\n"
        "    'stance: kept Voice=– Audience=– Tone=–; intent: kept understand; axes: ...'\n"
        "    'stance: changed Audience=– -> stakeholders because announcement; Tone=– -> directly because execs; intent: changed understand -> inform because ...; axes: ...'\n"
        "  Include a 'because' clause for every persona/intent change; when kept, say\n"
        "  'kept' for each axis. Bias toward keeping intent; only change intent with a\n"
        "  concrete reason tied to the subject.\n"
        "- why: 1–2 sentences explaining when this suggestion is useful.\n\n"
        "Recipe rules:\n"
        "- <staticPrompt> is exactly one static prompt token (do not include multiple static prompts or combine them).\n"
        "- Directional is required: always include exactly one directional modifier from the directional list; many valid tokens contain spaces (for example, 'fly ong')—keep the full token intact.\n"
        "- <completeness> is a single token; include it only when it meaningfully shapes the response.\n"
        "- <scopeTokens> and <methodTokens> are zero or more space-separated axis tokens for that axis (respecting small caps: scope ≤ 2 tokens, method ≤ 3 tokens); omit the segment entirely when it adds no value.\n"
        "- <formToken> and <channelToken> are single axis tokens (Form and Channel are singletons); omit them when no bias is needed.\n"
        "  Examples: scopeTokens='actions edges', methodTokens='structure flow', formToken='bullets', channelToken='slack'.\n\n"
        "Persona/Intent rules (Who/Why):\n"
        "- When a different Persona/Intent stance would materially change how the\n"
        "  model should respond, you SHOULD fill persona_voice/persona_audience/\n"
        "  persona_tone/intent_purpose using ONLY the Persona/Intent token lists\n"
        "  below, and you SHOULD provide a matching stance_command for Persona\n"
        "  (voice/audience/tone) only. Intent must be expressed via intent_purpose\n"
        "  and the separate `intent <token>` command, not inside stance_command.\n"
        "- Across your 3 to 5 suggestions, include clear Persona/Intent stances for\n"
        "  at least two suggestions.\n"
        "- When you cannot sensibly express the stance with these tokens, leave\n"
        "  persona_voice/persona_audience/persona_tone/intent_purpose as empty\n"
        "  strings and rely on stance_command + why instead.\n\n"
        "Formatting rules (strict):\n"
        "- Output ONLY the JSON object described above; do NOT include prose,\n"
        "  markdown, backticks, or any other surrounding text.\n"
        "- All suggestion objects MUST include name and recipe; also fill reasoning and why for every suggestion.\n"
        "- Never invent new axis tokens: always choose from the provided axis\n"
        "  lists (for example, use the method token 'analysis' rather than a new\n"
        "  token like 'analyze'). When unsure, choose the closest valid token rather\n"
        "  than inventing a new one.\n"
        "- Keep reasoning <= 480 characters and why <= 200 characters. If you must\n"
        "  shorten, end on a complete sentence, never mid-thought.\n\n"
        "Use only tokens from the following sets where possible.\n"
        "Axis semantics and available tokens (How the model responds):\n"
        f"{axis_docs}\n\n"
        "Persona/Intent stance tokens and examples for stance commands (Who/Why):\n"
        f"{persona_intent_docs}\n\n"
        + context_block
        + "Static prompts and their semantics:\n"
        f"{static_prompt_docs}\n\n"
        f"Subject: {prompt_subject}\n\n"
        "Content:\n"
        f"{content_text}\n"
    )


def _set_setting(key: str, value) -> None:
    """Best-effort setter for Talon settings across runtimes."""
    try:
        if hasattr(settings, "set"):
            settings.set(key, value)
            return
    except Exception:
        pass
    try:
        settings[key] = value
    except Exception:
        pass


mod = Module()
ctx = Context()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)

def _persona_presets():
    """Return the latest persona presets (reload-safe)."""

    try:
        from ..lib import personaConfig

        return tuple(getattr(personaConfig, "PERSONA_PRESETS", ()))
    except Exception:
        return ()


def _intent_presets():
    """Return the latest intent presets (reload-safe)."""

    try:
        from ..lib import personaConfig

        return tuple(getattr(personaConfig, "INTENT_PRESETS", ()))
    except Exception:
        return ()


def _persona_preset_spoken_map() -> dict[str, str]:
    """Return spoken->key map for persona presets."""

    mapping: dict[str, str] = {}
    for preset in _persona_presets():
        spoken = (preset.spoken or preset.label or preset.key).strip().lower()
        if not spoken:
            continue
        mapping[spoken] = preset.key
    return mapping


def _intent_preset_spoken_map() -> dict[str, str]:
    """Return spoken->key map for intent presets."""

    mapping: dict[str, str] = {}
    for preset in _intent_presets():
        spoken = (preset.key or "").strip().lower()
        if not spoken:
            continue
        mapping[spoken] = preset.key
    return mapping


def _axis_tokens(axis: str) -> set[str]:
    """Return the latest persona/intent axis tokens."""

    try:
        return set(persona_docs_map(axis).keys())
    except Exception:
        return set()


def _refresh_persona_intent_lists() -> None:
    """Populate persona/intent preset lists from current presets."""

    persona_map = _persona_preset_spoken_map()
    intent_map = _intent_preset_spoken_map()
    try:
        ctx.lists["user.personaPreset"] = persona_map
        ctx.lists["user.intentPreset"] = intent_map
    except Exception:
        # In some runtimes, Context may not be fully initialised; fail softly.
        pass
    return None

mod.list("personaPreset", desc="Persona (Who) presets for GPT stance")
mod.list("intentPreset", desc="Intent (Why) presets for GPT stance")

# Session-scoped presets (prompt + stance + contract + directional + destination).
_PRESETS: dict[str, dict[str, object]] = {}

_refresh_persona_intent_lists()


_prompt_pipeline = PromptPipeline()
_recursive_orchestrator = RecursiveOrchestrator(_prompt_pipeline)
ASYNC_BLOCKING_SETTING = "user.model_async_blocking"
_last_inflight_warning_request_id = None
_suppress_inflight_notify_request_id = None


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is already running."""
    try:
        phase = getattr(current_state(), "phase", RequestPhase.IDLE)
        # Treat terminal phases as idle so follow-up requests are allowed.
        if phase in (
            RequestPhase.IDLE,
            RequestPhase.DONE,
            RequestPhase.ERROR,
            RequestPhase.CANCELLED,
        ):
            return False
        return phase != RequestPhase.IDLE
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""
    global _last_inflight_warning_request_id
    global _suppress_inflight_notify_request_id

    suppress_id = _suppress_inflight_notify_request_id
    try:
        suppress_id = suppress_id or getattr(GPTState, "suppress_inflight_notify_request_id", None)
    except Exception:
        pass

    try:
        state = current_state()
    except Exception:
        state = None

    try:
        phase = getattr(state, "phase", RequestPhase.IDLE)
        request_id = getattr(state, "request_id", None)
    except Exception:
        phase = RequestPhase.IDLE
        request_id = None

    if phase in (
        RequestPhase.IDLE,
        RequestPhase.DONE,
        RequestPhase.ERROR,
        RequestPhase.CANCELLED,
    ):
        _last_inflight_warning_request_id = None
        _suppress_inflight_notify_request_id = None
        try:
            if suppress_id and getattr(GPTState, "suppress_inflight_notify_request_id", None) == suppress_id:
                GPTState.suppress_inflight_notify_request_id = None
        except Exception:
            pass
        return False

    if request_id is None:
        request_id = suppress_id or "__none__"

    # When the request bus is already in-flight for the current request, suppress
    # user-facing notify so UI housekeeping (closing surfaces) during a request
    # does not emit spurious warnings.
    if request_id == suppress_id:
        return True

    if request_id == _last_inflight_warning_request_id:
        return True

    notify("GPT: A request is already running; wait for it to finish or cancel it first.")
    _last_inflight_warning_request_id = request_id
    return True


def _read_list_items(filename: str) -> list[tuple[str, str]]:
    """Read (key, description) pairs from a Talon list file in GPT/lists."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.join(current_dir, "lists")
    path = os.path.join(lists_dir, filename)
    items: list[tuple[str, str]] = []
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
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                items.append((key.strip(), value.strip()))
    except FileNotFoundError:
        return []
    return items


def _await_handle_and_insert(handle, destination: str) -> None:
    """Wait on an async handle and insert the response when ready (background)."""

    def _runner():
        try:
            handle.wait(timeout=None)
        except Exception:
            pass
        result = getattr(handle, "result", None)
        if result is None:
            notify("GPT: Async run produced no result")
            return
        try:
            actions.user.gpt_insert_response(result, destination)
        except Exception:
            notify("GPT: Failed to insert async result")

    threading.Thread(target=_runner, daemon=True).start()


def _handle_async_result(handle, destination: str, block: bool = True) -> None:
    """Insert async result, either blocking or via background wait."""
    if block:
        try:
            handle.wait(timeout=None)
        except Exception:
            pass
        result = getattr(handle, "result", None)
        if result is None:
            notify("GPT: Async run produced no result")
            return
        try:
            actions.user.gpt_insert_response(result, destination)
        except Exception:
            notify("GPT: Failed to insert async result")
        return
    # Non-blocking path: background wait and insert.
    _await_handle_and_insert(handle, destination)


def _build_axis_docs() -> str:
    """Build a text block describing all axis and directional modifiers."""
    sections = [
        ("Completeness modifiers", "completeness"),
        ("Scope modifiers", "scope"),
        ("Method modifiers", "method"),
        ("Form modifiers", "form"),
        ("Channel modifiers", "channel"),
        ("Directional modifiers", "directional"),
    ]
    catalog = axis_catalog()
    axis_tokens = catalog.get("axes", {}) or {}
    lines: list[str] = [
        "Note: Axes capture how and in what shape the model should respond (completeness, scope, method, form, channel, directional lens). "
        "Hierarchy: Completeness > Method > Scope > Form > Channel. Ambiguous tokens are assigned in that order unless explicitly prefixed "
        "(Completeness:/Method:/Scope:/Form:/Channel:). For full semantics and examples, see ADR 005/012/013/016/032 and the GPT README axis cheat sheet.\n"
    ]
    for label, axis_name in sections:
        token_map = axis_tokens.get(axis_name, {}) or {}
        if not token_map:
            # Fallback to Talon list parsing if catalog data is missing.
            filename = {
                "completeness": "completenessModifier.talon-list",
                "scope": "scopeModifier.talon-list",
                "method": "methodModifier.talon-list",
                "form": "formModifier.talon-list",
                "channel": "channelModifier.talon-list",
                "directional": "directionalModifier.talon-list",
            }.get(axis_name)
            items = _read_list_items(filename) if filename else []
        else:
            items = sorted(token_map.items(), key=lambda kv: kv[0])
        if not items:
            continue
        lines.append(f"{label}:")
        for key, desc in items:
            lines.append(f"- {key}: {desc}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _build_persona_intent_docs() -> str:
    """Build a compact cheat sheet for Persona/Intent stance tokens."""
    axes = (
        ("Voice", "voice"),
        ("Audience", "audience"),
        ("Tone", "tone"),
        ("Intent", "intent"),
    )
    lines: list[str] = [
        "Persona (Who) and Intent (Why) tokens you may use in Stance commands:",
        "",
    ]
    for label, axis in axes:
        docs = persona_docs_map(axis)
        if not docs:
            continue
        tokens = ", ".join(sorted(docs.keys()))
        if not tokens:
            continue
        lines.append(f"{label} tokens:")
        lines.append(f"- {tokens}")
        lines.append("")

    try:
        persona_presets = _persona_presets()
        intent_presets = _intent_presets()

        if persona_presets:
            lines.append("Persona presets (speakable presets for stance commands):")
            for preset in persona_presets:
                bits: list[str] = []
                if preset.voice:
                    bits.append(preset.voice)
                if preset.audience:
                    bits.append(preset.audience)
                if preset.tone:
                    bits.append(preset.tone)
                stance = " ".join(bits)
                label = preset.label or preset.key
                lines.append(f"- persona {preset.key}: {label} ({stance})")
            lines.append("")

        if intent_presets:
            lines.append("Intent presets (shortcut names for `intent` commands):")
            for preset in intent_presets:
                label = preset.label or preset.key
                intent = preset.intent
                lines.append(f"- intent {preset.key}: {label} ({intent})")
            lines.append("")
    except Exception:
        pass

    # Provide a few concrete stance examples that use only valid axis tokens.
    lines.append("Examples of valid stance commands:")
    lines.append("- Stance: model write as teacher to junior engineer kindly")
    lines.append("- Stance: model write as programmer to CEO directly")
    lines.append("- Stance: model write as programmer to programmer casually")
    return "\n".join(lines).rstrip()


def _build_static_prompt_docs() -> str:
    """Build a text block describing static prompts and their semantics."""
    catalog = static_prompt_catalog()
    # Prefer descriptions from the catalog (STATIC_PROMPT_CONFIG), and include
    # default axes when present; fall back to listing unprofiled prompts by name.
    lines: list[str] = [
        "Note: Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging, Slack/Jira formatting, taxonomy-style outputs) now live only as form/channel/method axis values rather than static prompts; see ADR 012/013 and the README cheat sheet for axis-based recipes.\n"
    ]
    # First, profiled prompts with rich descriptions.
    for entry in catalog["profiled"]:
        name = entry["name"]
        description = entry.get("description", "").strip()
        if not description:
            continue
        axes_bits: list[str] = []
        for label in ("completeness", "scope", "method", "form", "channel"):
            value = entry.get("axes", {}).get(label)
            if not value:
                continue
            if isinstance(value, list):
                rendered = " ".join(str(v) for v in value)
            else:
                rendered = str(value)
            if rendered:
                axes_bits.append(f"{label}={rendered}")
        if axes_bits:
            lines.append(f"- {name}: {description} (defaults: {', '.join(axes_bits)})")
        else:
            lines.append(f"- {name}: {description}")

    # Then, any remaining static prompts from the list so the model sees the
    # full token vocabulary.
    other_prompts = catalog.get("unprofiled_tokens", [])
    other_line = "- Other static prompts (tokens only; see docs for semantics): "
    if other_prompts:
        other_line += ", ".join(sorted(other_prompts))
    else:
        other_line += "(none)"
    lines.append(other_line)

    body = "\n".join(lines).strip()
    heading_lines = [
        "## Static prompt catalog snapshots",
        "",
        "## Static prompt catalog details",
        "",
    ]
    return "\n".join(heading_lines + [body])


def gpt_query():
    """Send a prompt to the GPT API and return the response"""

    if _reject_if_request_in_flight():
        return ""

    # Reset state before pasting
    GPTState.last_was_pasted = False

    response = send_request()
    return response


@mod.action_class
class UserActions:
    def gpt_start_debug():
        """Enable debug logging"""
        if _reject_if_request_in_flight():
            return
        GPTState.start_debug()

    def gpt_stop_debug():
        """Disable debug logging"""
        if _reject_if_request_in_flight():
            return
        GPTState.stop_debug()

    def gpt_copy_last_raw_exchange() -> None:
        """Copy the last raw GPT request/response JSON to the clipboard for debugging."""
        if _reject_if_request_in_flight():
            return
        try:
            data = {
                "request": getattr(GPTState, "last_raw_request", {}) or {},
                "response": getattr(GPTState, "last_raw_response", {}) or {},
            }
        except Exception:
            data = {"request": {}, "response": {}}

        if not data["request"] and not data["response"]:
            notify("GPT debug: No last raw exchange available to copy")
            return

        try:
            import json as _json

            pretty = _json.dumps(data, indent=2, sort_keys=True)
        except Exception:
            # Fallback: best-effort string representation.
            pretty = str(data)

        clip.set_text(pretty)
        notify("GPT debug: Copied last raw request/response JSON to clipboard")

    def gpt_clear_context():
        """Reset the stored context"""
        if _reject_if_request_in_flight():
            return
        GPTState.clear_context()

    def gpt_clear_stack(stack_name: str):
        """Reset the stored stack"""
        if _reject_if_request_in_flight():
            return
        GPTState.clear_stack(stack_name)

    def gpt_clear_query():
        """Reset the stored query"""
        if _reject_if_request_in_flight():
            return
        GPTState.clear_query()

    def gpt_clear_all():
        """Reset all state"""
        if _reject_if_request_in_flight():
            return
        GPTState.clear_all()

    def gpt_clear_thread():
        """Create a new thread"""
        if _reject_if_request_in_flight():
            return
        GPTState.new_thread()
        actions.user.confirmation_gui_refresh_thread()

    def gpt_enable_threading():
        """Enable threading of subsequent requests"""
        if _reject_if_request_in_flight():
            return
        GPTState.enable_thread()

    def gpt_disable_threading():
        """Enable threading of subsequent requests"""
        if _reject_if_request_in_flight():
            return
        GPTState.disable_thread()

    def gpt_push_context(context: str):
        """Add the selected text to the stored context"""
        if _reject_if_request_in_flight():
            return
        GPTState.push_context(format_message(context))

    def gpt_push_query(query: str):
        """Add the selected text to the stored context"""
        if _reject_if_request_in_flight():
            return
        GPTState.push_query(format_messages("user", [format_message(query)]))

    def gpt_push_thread(content: str):
        """Add the selected text to the active thread"""
        if _reject_if_request_in_flight():
            return
        GPTState.push_thread(format_messages("user", [format_message(content)]))

    def gpt_additional_user_context() -> list[str]:
        """This is an override function that can be used to add additional context to the prompt"""
        if _reject_if_request_in_flight():
            return []
        return []

    def gpt_tools() -> str:
        """This is an override function that will provide all of the tools available for tool calls as a JSON string"""
        if _reject_if_request_in_flight():
            return "[]"
        return "[]"

    def gpt_call_tool(tool_name: str, parameters: str) -> str:
        """This will call the tool by name and return a string of the tool call results"""
        if _reject_if_request_in_flight():
            return ""
        return ""

    def gpt_set_system_prompt(
        modelVoice: str,
        modelAudience: str,
        modelIntent: str,
        modelTone: str,
    ) -> None:
        """Set the system prompt to be used when the LLM responds to you"""
        if _reject_if_request_in_flight():
            return
        if modelVoice == "":
            modelVoice = GPTState.system_prompt.voice
        if modelAudience == "":
            modelAudience = GPTState.system_prompt.audience
        if modelTone == "":
            modelTone = GPTState.system_prompt.tone
        if modelIntent == "":
            modelIntent = GPTState.system_prompt.intent
        new_system_prompt = GPTSystemPrompt(
            voice=modelVoice,
            audience=modelAudience,
            intent=modelIntent,
            tone=modelTone,
        )
        GPTState.system_prompt = new_system_prompt

    def gpt_reset_system_prompt():
        """Reset the system prompt to default"""
        if _reject_if_request_in_flight():
            return
        GPTState.system_prompt = GPTSystemPrompt()
        # Also reset contract-style defaults so "reset writing" is a single
        # switch for persona and writing behaviour.
        _set_setting("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        _set_setting("user.model_default_scope", "")
        _set_setting("user.model_default_method", "")
        _set_setting("user.model_default_form", "")
        _set_setting("user.model_default_channel", "")
        GPTState.user_overrode_form = True
        GPTState.user_overrode_channel = True

    def persona_set_preset(preset_key: str) -> None:
        """Set Persona (Who) stance from a shared preset (ADR 042)."""
        if _reject_if_request_in_flight():
            return
        from ..lib.personaConfig import PersonaPreset  # Local import for Talon reloads

        preset_map: dict[str, PersonaPreset] = {p.key: p for p in _persona_presets()}
        preset = preset_map.get(preset_key)
        if preset is None:
            notify(f"GPT: Unknown persona preset: {preset_key}")
            return

        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        new_prompt = GPTSystemPrompt(
            voice=preset.voice or current.voice,
            audience=preset.audience or current.audience,
            intent=current.intent,
            tone=preset.tone or current.tone,
            completeness=current.completeness,
            scope=current.scope,
            method=current.method,
            form=getattr(current, "form", ""),
            channel=getattr(current, "channel", ""),
            directional=current.directional,
        )
        GPTState.system_prompt = new_prompt
        notify(
            "GPT: Persona stance set to "
            f"voice={new_prompt.voice or current.get_voice()}, "
            f"audience={new_prompt.audience or current.get_audience()}, "
            f"tone={new_prompt.tone or current.get_tone()}"
        )

    def intent_set_preset(preset_key: str) -> None:
        """Set Intent (Why) stance from a shared preset (ADR 042)."""
        if _reject_if_request_in_flight():
            return
        from ..lib.personaConfig import IntentPreset  # Local import for Talon reloads

        preset_map: dict[str, IntentPreset] = {p.key: p for p in _intent_presets()}
        preset = preset_map.get(preset_key)
        if preset is None:
            notify(f"GPT: Unknown intent preset: {preset_key}")
            return

        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        new_prompt = GPTSystemPrompt(
            voice=current.voice,
            audience=current.audience,
            intent=preset.intent or current.intent,
            tone=current.tone,
            completeness=current.completeness,
            scope=current.scope,
            method=current.method,
            form=getattr(current, "form", ""),
            channel=getattr(current, "channel", ""),
            directional=current.directional,
        )
        GPTState.system_prompt = new_prompt
        notify(
            "GPT: Intent stance set to "
            f"intent={new_prompt.intent or current.get_intent()}"
        )

    def persona_status() -> None:
        """Show the current Persona (Who) stance compared to defaults."""
        if _reject_if_request_in_flight():
            return
        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        voice = current.get_voice()
        audience = current.get_audience()
        tone = current.get_tone()

        default_voice = GPTSystemPrompt.default_voice() or ""
        default_audience = GPTSystemPrompt.default_audience() or ""
        default_tone = GPTSystemPrompt.default_tone() or ""

        non_default_axes: list[str] = []
        if voice != default_voice:
            non_default_axes.append("voice")
        if audience != default_audience:
            non_default_axes.append("audience")
        if tone != default_tone:
            non_default_axes.append("tone")

        if non_default_axes:
            suffix = f" (non-default: {', '.join(non_default_axes)})"
        else:
            suffix = " (all default)"

        notify(
            "Persona stance: "
            f"voice={voice or default_voice}, "
            f"audience={audience or default_audience}, "
            f"tone={tone or default_tone}{suffix}"
        )

    def intent_status() -> None:
        """Show the current Intent (Why) stance compared to defaults."""
        if _reject_if_request_in_flight():
            return
        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        intent = current.get_intent()
        default_intent = GPTSystemPrompt.default_intent() or ""

        if intent != default_intent:
            suffix = " (non-default)"
        else:
            suffix = " (default)"

        notify(f"Intent stance: intent={intent or default_intent}{suffix}")

    def persona_reset() -> None:
        """Reset Persona (Who) stance to defaults without touching contract axes."""
        if _reject_if_request_in_flight():
            return
        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        new_prompt = GPTSystemPrompt(
            voice="",
            audience="",
            intent=current.intent,
            tone="",
            completeness=current.completeness,
            scope=current.scope,
            method=current.method,
            form=current.form,
            channel=current.channel,
            directional=current.directional,
        )
        GPTState.system_prompt = new_prompt
        notify("GPT: Persona stance reset to defaults")

    def intent_reset() -> None:
        """Reset Intent (Why) stance to defaults without touching contract axes."""
        if _reject_if_request_in_flight():
            return
        current = getattr(GPTState, "system_prompt", GPTSystemPrompt())
        if not isinstance(current, GPTSystemPrompt):
            current = GPTSystemPrompt()

        new_prompt = GPTSystemPrompt(
            voice=current.voice,
            audience=current.audience,
            intent="",
            tone=current.tone,
            completeness=current.completeness,
            scope=current.scope,
            method=current.method,
            form=current.form,
            channel=current.channel,
            directional=current.directional,
        )
        GPTState.system_prompt = new_prompt
        notify("GPT: Intent stance reset to defaults")

    def gpt_set_async_blocking(enabled: int) -> None:
        """Toggle async blocking mode for model runs (1=blocking, 0=non-blocking)"""
        if _reject_if_request_in_flight():
            return
        _set_setting(ASYNC_BLOCKING_SETTING, bool(enabled))
        mode = "blocking" if enabled else "non-blocking"
        actions.app.notify(f"GPT: async mode set to {mode}")

    def gpt_set_default_completeness(level: str) -> None:
        """Set the default completeness level."""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_completeness", level)
        GPTState.user_overrode_completeness = True

    def gpt_reset_default_completeness() -> None:
        """Reset the default completeness level to its configured base value"""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        GPTState.user_overrode_completeness = False

    def gpt_set_default_scope(level: str) -> None:
        """Set the default scope."""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_scope", level)
        GPTState.user_overrode_scope = True

    def gpt_reset_default_scope() -> None:
        """Reset the default scope level to its configured base value"""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_scope", "")
        GPTState.user_overrode_scope = False

    def gpt_set_default_method(level: str) -> None:
        """Set the default method."""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_method", level)
        GPTState.user_overrode_method = True

    def gpt_reset_default_method() -> None:
        """Reset the default method to its configured base value (no strong default)"""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_method", "")
        GPTState.user_overrode_method = False

    def gpt_set_default_form(level: str) -> None:
        """Set the default form."""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_form", level)
        GPTState.user_overrode_form = True

    def gpt_reset_default_form() -> None:
        """Reset the default form to its configured base value (no strong default)"""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_form", "")
        GPTState.user_overrode_form = False

    def gpt_set_default_channel(level: str) -> None:
        """Set the default channel."""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_channel", level)
        GPTState.user_overrode_channel = True

    def gpt_reset_default_channel() -> None:
        """Reset the default channel to its configured base value (no strong default)"""
        if _reject_if_request_in_flight():
            return
        _set_setting("user.model_default_channel", "")
        GPTState.user_overrode_channel = False

    def gpt_select_last() -> None:
        """select all the text in the last GPT output"""
        if _reject_if_request_in_flight():
            return
        if not GPTState.last_was_pasted:
            notify("Tried to select GPT output, but it was not pasted in an editor")
            return

        lines = GPTState.last_response.split("\n")
        for _ in lines[:-1]:
            actions.edit.extend_up()
        actions.edit.extend_line_end()
        for _ in lines[0]:
            actions.edit.extend_left()

    def gpt_apply_prompt(apply_prompt_configuration: ApplyPromptConfiguration):
        """Apply an arbitrary prompt to arbitrary text"""
        # Refuse to start a new run if one is already in progress.
        if _reject_if_request_in_flight():
            return
        # Close the response viewer at the start of a new run so it disappears
        # immediately (for example, when using `model again`) and will be
        # reopened with the fresh answer once the pipeline completes.
        try:
            actions.user.model_response_canvas_close()
        except Exception:
            pass
        # If the pattern picker GUI is open, close it when any model prompt runs
        # so voice-triggered patterns and regular grammar both dismiss it.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        # Also close the prompt-specific pattern picker if it is open.
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        # Close the suggestion picker as well so executing a prompt always
        # leaves at most one model window visible.
        try:
            actions.user.model_prompt_recipe_suggestions_gui_close()
        except Exception:
            pass
        # Close the Help Hub to avoid overlapping overlays during runs.
        try:
            actions.user.help_hub_close()
        except Exception:
            pass

        prompt = apply_prompt_configuration.please_prompt
        if not str(prompt or "").strip():
            notify("GPT: Prompt is empty; nothing to run")
            return ""
        source = apply_prompt_configuration.model_source
        additional_source = apply_prompt_configuration.additional_model_source
        destination = apply_prompt_configuration.model_destination
        try:
            GPTState.last_prompt_text = prompt
        except Exception:
            pass

        # Snapshot the primary source messages so plain `model again` can reuse
        # the same content even if the live source has changed.
        try:
            GPTState.last_source_messages = source.format_messages()
        except Exception:
            GPTState.last_source_messages = []

        # Remember the canonical source key (when available) so debug source
        # snapshots can include a meaningful source type label.
        try:
            GPTState.last_source_key = getattr(source, "modelSimpleSource", "")
        except Exception:
            GPTState.last_source_key = ""

        result = None
        async_started = False
        raw_block = settings.get("user.model_async_blocking", False)
        block = False if raw_block is None else bool(raw_block)
        # Prefer async orchestrator path; optionally block for result.
        if hasattr(_recursive_orchestrator, "run_async"):
            try:
                handle = _recursive_orchestrator.run_async(
                    prompt,
                    source,
                    destination,
                    additional_source,
                )
                async_started = True
                _handle_async_result(handle, destination, block=block)
                result = getattr(handle, "result", None)
            except Exception:
                async_started = False
                result = None
        if result is None and not async_started:
            result = _recursive_orchestrator.run(
                prompt,
                source,
                destination,
                additional_source,
            )

        if result is not None:
            actions.user.gpt_insert_response(result, destination)
            return result.text
        # Non-blocking async path returns early; insertion handled in background.
        return ""

    def gpt_run_prompt(
        prompt: str,
        source: ModelSource,
        additional_source: Optional[ModelSource] = None,
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        if _reject_if_request_in_flight():
            return ""

        if not str(prompt or "").strip():
            notify("GPT: Prompt is empty; nothing to run")
            return ""

        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)

        try:
            handle = _prompt_pipeline.run_async(
                prompt,
                source,
                destination="",
                additional_source=additional_source,
            )
            async_started = True
            _handle_async_result(handle, destination="", block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _prompt_pipeline.run(
                prompt,
                source,
                destination="",
                additional_source=additional_source,
            )

        if result is not None:
            return result.text
        return ""

    def gpt_recursive_prompt(
        prompt: str,
        source: ModelSource,
        destination: ModelDestination = Default(),
        additional_source: Optional[ModelSource] = None,
    ) -> str:
        """Run a controller prompt that may recursively delegate work to sub-sessions."""

        if _reject_if_request_in_flight():
            return ""

        if not str(prompt or "").strip():
            notify("GPT: Prompt is empty; nothing to run")
            return ""

        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)
        try:
            handle = _recursive_orchestrator.run_async(
                prompt,
                source,
                destination,
                additional_source,
            )
            async_started = True
            _handle_async_result(handle, destination, block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _recursive_orchestrator.run(
                prompt,
                source,
                destination,
                additional_source,
            )

        if result is not None:
            actions.user.gpt_insert_response(result, destination)
            return (
                result.text
                if hasattr(result, "text")
                else str(getattr(result, "text", ""))
            )  # type: ignore[arg-type]
        # Non-blocking async path returns early; insertion handled in background.
        return ""

    def gpt_analyze_prompt(destination: ModelDestination = ModelDestination()):
        """Explain why we got the results we did"""
        PROMPT = "Analyze the provided prompt and response. Explain how the prompt was understood to generate the given response. Provide only the explanation."

        if _reject_if_request_in_flight():
            return

        if not GPTState.last_response:
            notify("GPT Failure: No response available to analyze")
            return

        session = PromptSession(destination)
        session.begin(reuse_existing=True)
        session.add_messages(
            [
                format_messages("assistant", [format_message(GPTState.last_response)]),
                format_messages("user", [format_message(PROMPT)]),
            ]
        )
        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)
        try:
            handle = _prompt_pipeline.complete_async(session)
            async_started = True
            _handle_async_result(handle, destination, block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _prompt_pipeline.complete(session)

        if result is not None:
            actions.user.gpt_insert_response(result, destination)

    def gpt_suggest_prompt_recipes(subject: str) -> None:
        """Suggest model prompt recipes using the default source."""
        source = create_model_source(settings.get("user.model_default_source"))
        _suggest_prompt_recipes_core_impl(source, subject)

    def gpt_suggest_prompt_recipes_with_source(
        source: ModelSource, subject: str
    ) -> None:
        """Suggest model prompt recipes for an explicit source."""
        _suggest_prompt_recipes_core_impl(source, subject)

    def gpt_rerun_last_suggest() -> None:
        """Rerun prompt recipe suggestions using the last subject and source."""
        if _reject_if_request_in_flight():
            return
        last_subject = getattr(GPTState, "last_suggest_subject", "") or ""
        last_context = getattr(GPTState, "last_suggest_context", {}) or {}
        last_recipes = getattr(GPTState, "last_suggested_recipes", []) or []
        cached_content = getattr(GPTState, "last_suggest_content", "") or ""
        if not cached_content and not last_subject and not last_context and not last_recipes:
            notify("GPT: No previous suggestions to rerun")
            return

        source_key = suggestion_source(settings.get("user.model_default_source"))

        class _CachedSuggestSource(ModelSource):
            modelSimpleSource = source_key

            def get_text(self):
                return cached_content

        source = _CachedSuggestSource()
        _suggest_prompt_recipes_core_impl(source, last_subject)

    def gpt_replay(destination: str):
        """Replay the last request"""
        if _reject_if_request_in_flight():
            return

        # Require a directional lens per ADR 048; prefer last_axes then legacy field.
        last_directional_tokens = getattr(GPTState, "last_axes", {}).get(
            "directional", []
        )
        directional = (
            last_directional_tokens[-1]
            if isinstance(last_directional_tokens, list) and last_directional_tokens
            else getattr(GPTState, "last_directional", "")
        )
        if not directional:
            notify(
                "GPT: Last request has no directional lens; replay requires fog/fig/dig/ong/rog/bog/jog."
            )
            return

        snapshot = last_recipe_snapshot()
        # Enforce axis caps for replay surfaces (scope≤2, method≤3, form=1, channel=1).
        scope_tokens = (snapshot.get("scope_tokens") or [])[-2:]
        method_tokens = (snapshot.get("method_tokens") or [])[-3:]
        form_tokens = (snapshot.get("form_tokens") or [])[-1:]
        channel_tokens = (snapshot.get("channel_tokens") or [])[-1:]

        # Rebuild recipe/state with capped axes to avoid replaying over-cap values.
        set_last_recipe_from_selection(
            snapshot.get("static_prompt", ""),
            snapshot.get("completeness", ""),
            scope_tokens,
            method_tokens,
            form_tokens,
            channel_tokens,
            directional,
        )

        session = PromptSession(destination)
        session.begin(reuse_existing=True)
        result_handle = _prompt_pipeline.complete_async(session)
        raw_block = settings.get("user.model_async_blocking", False)
        block = False if raw_block is None else bool(raw_block)
        _handle_async_result(result_handle, destination, block=block)

    def gpt_show_last_recipe() -> None:
        """Show a short summary of the last prompt recipe"""
        if _reject_if_request_in_flight():
            return
        snapshot = last_recipe_snapshot()
        static_prompt = snapshot.get("static_prompt", "")
        completeness = snapshot.get("completeness", "")
        scope_tokens = snapshot.get("scope_tokens", []) or []
        method_tokens = snapshot.get("method_tokens", []) or []
        form_tokens = snapshot.get("form_tokens", []) or []
        channel_tokens = snapshot.get("channel_tokens", []) or []
        directional = snapshot.get("directional", "") or ""

        parts: list[str] = []
        if static_prompt:
            parts.append(static_prompt)
        for value in (
            completeness,
            " ".join(scope_tokens),
            " ".join(method_tokens),
            " ".join(form_tokens),
            " ".join(channel_tokens),
        ):
            if value:
                parts.append(value)

        if parts:
            if directional:
                parts.append(directional)
            recipe = " · ".join(parts)
        else:
            recipe = snapshot.get("recipe", "") or ""
            if directional and recipe and directional not in recipe:
                recipe = f"{recipe} · {directional}"
        if not recipe:
            notify("GPT: No last recipe available")
            return
        recipe_tokens = [t for t in recipe.split(" · ") if t]
        if directional:
            seen_directional = False
            deduped: list[str] = []
            for token in recipe_tokens:
                if token == directional:
                    if seen_directional:
                        continue
                    seen_directional = True
                deduped.append(token)
            recipe = " · ".join(deduped)
        actions.app.notify(f"Last recipe: {recipe}")

    def gpt_show_last_meta() -> None:
        """Show the last meta-interpretation, if available."""
        if _reject_if_request_in_flight():
            return
        meta = last_recap_snapshot().get("meta", "")
        if not meta or not str(meta).strip():
            actions.app.notify("GPT: No last meta interpretation available")
            return
        actions.app.notify(f"Last meta interpretation:\n{meta}")

    def gpt_show_pattern_debug(pattern_name: str) -> None:
        """Show a concise debug snapshot for a named pattern."""
        if _reject_if_request_in_flight():
            return
        try:
            from ..lib.patternDebugCoordinator import pattern_debug_catalog
        except Exception:
            actions.app.notify("GPT: Pattern debug helper unavailable")
            return

        try:
            snapshots = pattern_debug_catalog()
        except Exception:
            actions.app.notify("GPT: Pattern debug helper unavailable")
            return

        snapshot = None
        for candidate in snapshots:
            name_value = str(candidate.get("name") or "")
            if name_value.lower() == pattern_name.lower():
                snapshot = candidate
                break

        if not snapshot:
            actions.app.notify(f"GPT: No pattern debug info for '{pattern_name}'")
            return

        name = str(snapshot.get("name") or pattern_name)
        static_prompt = str(snapshot.get("static_prompt") or "")
        axes = snapshot.get("axes", {}) or {}
        completeness = str(axes.get("completeness") or "")
        scope_value = axes.get("scope") or []
        method_value = axes.get("method") or []
        form_value = axes.get("form") or []
        channel_value = axes.get("channel") or []
        directional = str(axes.get("directional") or "")

        def _as_tokens(value) -> list[str]:
            if isinstance(value, list):
                return [str(v) for v in value if v]
            if isinstance(value, str) and value.strip():
                return value.strip().split()
            return []

        scope_tokens = _as_tokens(scope_value)
        method_tokens = _as_tokens(method_value)
        form_tokens = _as_tokens(form_value)
        channel_tokens = _as_tokens(channel_value)

        parts: list[str] = []
        if static_prompt:
            parts.append(static_prompt)
        for value in (
            completeness,
            " ".join(scope_tokens),
            " ".join(method_tokens),
            " ".join(form_tokens),
            " ".join(channel_tokens),
        ):
            if value:
                parts.append(value)
        if directional:
            parts.append(directional)
        recipe_line = " · ".join(parts) if parts else snapshot.get("recipe", "")

        last_axes = snapshot.get("last_axes") or {}
        actions.app.notify(
            "Pattern debug: "
            + name
            + "\nRecipe: "
            + (recipe_line or "(unknown)")
            + "\nLast axes: "
            + str(last_axes),
        )

    def gpt_clear_last_recap() -> None:
        """Clear last response/recipe/meta recap state."""
        if _reject_if_request_in_flight():
            return
        clear_recap_state()
        actions.app.notify("GPT: Cleared last recap state")

    def gpt_cancel_request() -> None:
        """Best-effort cancel for in-flight model requests (UI + state only)."""
        # Ensure the bus has a controller so the cancel event updates state/UX.
        try:
            if current_state().phase == RequestPhase.IDLE:
                set_controller(RequestUIController())
        except Exception:
            set_controller(RequestUIController())
        try:
            from ..lib.modelHelpers import cancel_active_request

            cancel_active_request()
        except Exception:
            pass
        emit_cancel()
        notify("GPT: Cancel requested")

    def gpt_preset_save(name: str) -> None:
        """Save the current prompt + stance + contract + directional + destination as a preset."""
        if not name or not name.strip():
            notify("GPT: Preset name required")
            return
        if not GPTState.last_recipe or not getattr(GPTState, "last_directional", ""):
            notify("GPT: No last recipe/directional to save as preset")
            return
        preset_name = name.strip().lower()
        axes = getattr(GPTState, "last_axes", {}) or {}
        dest_kind = (
            getattr(GPTState, "current_destination_kind", "") or settings.get("user.model_default_destination")
        )
        sys = getattr(GPTState, "system_prompt", None)
        _PRESETS[preset_name] = {
            "static_prompt": getattr(GPTState, "last_static_prompt", "") or "",
            "completeness": getattr(GPTState, "last_completeness", "") or "",
            "scope": axes.get("scope", []) or [],
            "method": axes.get("method", []) or [],
            "form": axes.get("form", []) or [],
            "channel": axes.get("channel", []) or [],
            "directional": axes.get("directional", []) or [],
            "voice": getattr(sys, "voice", "") if sys else "",
            "audience": getattr(sys, "audience", "") if sys else "",
            "tone": getattr(sys, "tone", "") if sys else "",
            "intent": getattr(sys, "intent", "") if sys else "",
            "destination_kind": dest_kind or "",
        }
        notify(f"GPT: Preset '{preset_name}' saved")

    def gpt_preset_run(name: str) -> None:
        """Run a saved preset using the stored contract and last/default sources/destination."""
        preset_name = name.strip().lower()
        preset = _PRESETS.get(preset_name)
        if not preset:
            notify(f"GPT: Unknown preset '{preset_name}'")
            return
        static_prompt = str(preset.get("static_prompt", "") or "")
        completeness = str(preset.get("completeness", "") or "")
        scope = [str(t) for t in preset.get("scope", []) if str(t)]
        method = [str(t) for t in preset.get("method", []) if str(t)]
        form_tokens = [str(t) for t in preset.get("form", []) if str(t)]
        channel_tokens = [str(t) for t in preset.get("channel", []) if str(t)]
        directional_tokens = [str(t) for t in preset.get("directional", []) if str(t)]
        directional = directional_tokens[-1] if directional_tokens else ""
        voice = str(preset.get("voice", "") or "")
        audience = str(preset.get("audience", "") or "")
        tone = str(preset.get("tone", "") or "")
        intent = str(preset.get("intent", "") or "")
        destination_kind = str(preset.get("destination_kind", "") or "")
        # Seed state so rerun uses the preset axes.
        GPTState.last_static_prompt = static_prompt
        GPTState.last_completeness = completeness
        GPTState.last_scope = " ".join(scope)
        GPTState.last_method = " ".join(method)
        GPTState.last_form = " ".join(form_tokens)
        GPTState.last_channel = " ".join(channel_tokens)
        GPTState.last_directional = directional
        # Seed stance and destination.
        try:
            GPTState.system_prompt.voice = voice
            GPTState.system_prompt.audience = audience
            GPTState.system_prompt.tone = tone
            GPTState.system_prompt.intent = intent
        except Exception:
            pass
        try:
            GPTState.current_destination_kind = destination_kind
        except Exception:
            pass
        GPTState.last_axes = {
            "completeness": [completeness] if completeness else [],
            "scope": scope,
            "method": method,
            "form": form_tokens,
            "channel": channel_tokens,
            "directional": directional_tokens,
        }
        # Compose a concise recipe for recap surfaces.
        recipe_parts = [p for p in (static_prompt, completeness, " ".join(scope), " ".join(method), " ".join(form_tokens), " ".join(channel_tokens)) if p]
        GPTState.last_recipe = " · ".join(recipe_parts)
        UserActions.gpt_rerun_last_recipe(
            static_prompt,
            completeness,
            scope,
            method,
            directional,
            " ".join(form_tokens),
            " ".join(channel_tokens),
            destination_kind,
        )

    def gpt_preset_list() -> None:
        """List saved preset names."""
        if not _PRESETS:
            notify("GPT: No presets saved")
            return
        names = sorted(_PRESETS.keys())
        notify(f"GPT presets: {', '.join(names)}")

    def gpt_beta_paste_prompt(match: str) -> None:
        """Build a prompt via modelPrompt and paste it, surfacing migration errors."""
        if _reject_if_request_in_flight():
            return
        try:
            prompt = safe_model_prompt(match)
        except Exception as exc:
            notify(f"GPT: failed to build prompt ({exc})")
            return
        if not prompt:
            return
        try:
            actions.user.paste(prompt)
        except Exception:
            try:
                actions.insert(prompt)
            except Exception:
                notify("GPT: failed to paste prompt")

    def gpt_rerun_last_recipe(
        static_prompt: str,
        completeness: str,
        scope: Union[str, List[str]],
        method: Union[str, List[str]],
        directional: str,
        form: Union[str, List[str]] = "",
        channel: Union[str, List[str]] = "",
        destination_kind: str = "",
    ) -> None:
        """Rerun the last prompt recipe with optional axis overrides, using the last or default source."""
        if _reject_if_request_in_flight():
            return
        # Close the main confirmation window so the rerun does not briefly
        # show a mismatched recipe/response pair while state updates.
        try:
            actions.user.confirmation_gui_close()
        except Exception:
            pass

        if not GPTState.last_recipe:
            notify("GPT: No last recipe available to rerun")
            return

        snapshot = last_recipe_snapshot()
        base_static = snapshot.get("static_prompt", "")
        base_completeness = snapshot.get("completeness", "")
        base_scope_tokens_raw = snapshot.get("scope_tokens", []) or []
        base_method_tokens_raw = snapshot.get("method_tokens", []) or []
        base_form_tokens_raw = snapshot.get("form_tokens", []) or []
        base_channel_tokens_raw = snapshot.get("channel_tokens", []) or []
        base_directional = snapshot.get("directional", "")

        new_static = static_prompt or base_static

        # Completeness remains scalar; overrides simply replace the base when
        # provided.
        override_completeness_tokens = _map_axis_tokens(
            "completeness", _tokens_list(completeness)
        )
        new_completeness = (
            override_completeness_tokens[0]
            if override_completeness_tokens
            else base_completeness
        )

        # Scope/method remain token-based. An explicit override replaces the
        # base axis; unspecified axes keep the previous canonical tokens.
        def _filter_known(axis: str, tokens: list[str]) -> list[str]:
            """Drop any tokens that are not in the axis config map."""
            valid = axis_key_to_value_map_for(axis)
            return [t for t in tokens if t in valid]

        # Normalise incoming overrides to lists of tokens; treat falsy values as empty.
        scope_value = scope if isinstance(scope, list) else _tokens_list(scope)
        method_value = method if isinstance(method, list) else _tokens_list(method)
        form_value = form if isinstance(form, list) else _tokens_list(form)
        channel_value = channel if isinstance(channel, list) else _tokens_list(channel)

        base_scope_tokens = _canonicalise_axis_tokens(
            "scope", _filter_known("scope", base_scope_tokens_raw)
        )
        override_scope_tokens = _filter_known(
            "scope", _map_axis_tokens("scope", scope_value)
        )
        merged_scope_tokens = (
            _canonicalise_axis_tokens("scope", override_scope_tokens)
            if scope
            else base_scope_tokens
        )
        base_scope = _axis_tokens_to_string(base_scope_tokens)
        new_scope = _axis_tokens_to_string(merged_scope_tokens)

        base_method_tokens = _canonicalise_axis_tokens(
            "method", _filter_known("method", base_method_tokens_raw)
        )
        override_method_tokens = _filter_known(
            "method", _map_axis_tokens("method", method_value)
        )
        merged_method_tokens = (
            _canonicalise_axis_tokens("method", override_method_tokens)
            if method
            else base_method_tokens
        )
        base_method = _axis_tokens_to_string(base_method_tokens)
        new_method = _axis_tokens_to_string(merged_method_tokens)

        base_form_tokens = _canonicalise_axis_tokens(
            "form", _filter_known("form", base_form_tokens_raw)
        )
        override_form_tokens = _filter_known(
            "form", _map_axis_tokens("form", form_value)
        )
        merged_form_tokens = (
            _canonicalise_axis_tokens("form", override_form_tokens[:1])
            if form_value
            else base_form_tokens
        )
        new_form = _axis_tokens_to_string(merged_form_tokens[:1])

        base_channel_tokens = _canonicalise_axis_tokens(
            "channel", _filter_known("channel", base_channel_tokens_raw)
        )
        override_channel_tokens = _filter_known(
            "channel", _map_axis_tokens("channel", channel_value)
        )
        merged_channel_tokens = (
            _canonicalise_axis_tokens("channel", override_channel_tokens[:1])
            if channel_value
            else base_channel_tokens
        )
        new_channel = _axis_tokens_to_string(merged_channel_tokens[:1])
        base_directional_tokens = _filter_known(
            "directional", _map_axis_tokens("directional", _tokens_list(base_directional))
        )
        override_directional_tokens = _filter_known(
            "directional", _map_axis_tokens("directional", _tokens_list(directional))
        )
        if override_directional_tokens:
            new_directional = override_directional_tokens[-1]
        elif base_directional_tokens:
            new_directional = base_directional_tokens[-1]
        else:
            new_directional = ""

        if not new_directional:
            notify(
                "GPT: Last recipe has no directional lens; rerun requires a directional (fog/fig/dig/ong/rog/bog/jog)."
            )
            return

        if new_completeness and new_completeness not in axis_key_to_value_map_for(
            "completeness"
        ):
            new_completeness = ""

        try:
            if any(
                (
                    static_prompt,
                    override_completeness_tokens,
                    scope,
                    method,
                    form_value,
                    channel_value,
                    directional,
                )
            ):
                print(
                    "[gpt again] overrides",
                    f"static={static_prompt!r} "
                    f"C={override_completeness_tokens or completeness!r} "
                    f"S={override_scope_tokens or scope!r} "
                    f"M={override_method_tokens or method!r} "
                    f"F={override_form_tokens or form!r} "
                    f"Ch={override_channel_tokens or channel!r} "
                    f"D={directional!r}",
                )
            # Always emit base once per rerun so we can see diffs.
            print(
                "[gpt again] base",
                f"static={base_static!r} C={base_completeness!r} "
                f"S={base_scope!r} M={base_method!r} "
                f"F={base_form_tokens_raw!r} Ch={base_channel_tokens_raw!r} "
                f"D={base_directional!r}",
            )
        except Exception:
            pass

        try:
            changed = (
                override_scope_tokens
                or override_method_tokens
                or override_form_tokens
                or override_channel_tokens
                or override_completeness_tokens
                or static_prompt
                or directional
            )
            if changed:
                print(
                    "[gpt again] override->new",
                    f"scope_override={override_scope_tokens} scope_new={merged_scope_tokens}",
                    f"method_override={override_method_tokens} method_new={merged_method_tokens}",
                    f"form_override={override_form_tokens} form_new={merged_form_tokens}",
                    f"channel_override={override_channel_tokens} channel_new={merged_channel_tokens}",
                    f"C_new={new_completeness!r} static_new={new_static!r} directional={new_directional!r}",
                )
        except Exception:
            pass

        # If normalisation dropped axis tokens (due to caps or
        # incompatibilities), surface a short, non-modal hint so users can
        # see what changed.
        def _axis_drop_summary(
            axis_name: str,
            base_tokens: list[str],
            override_tokens: list[str],
            merged_tokens: list[str],
        ) -> str:
            # When an override is provided, treat it as authoritative.
            original_tokens = (
                [t for t in override_tokens if t]
                if override_tokens
                else [t for t in base_tokens if t]
            )
            if not original_tokens:
                return ""
            original_set = set(original_tokens)
            merged_set = set(merged_tokens)
            if not original_set or original_set == merged_set:
                return ""
            original_str = " ".join(original_tokens)
            merged_str = " ".join(merged_tokens) if merged_tokens else "(none)"
            return f"{axis_name}={original_str} \u2192 {merged_str}"

        axis_drop_parts: list[str] = []
        for axis_name, base_tokens, override_tokens, merged_tokens in (
            (
                "scope",
                base_scope_tokens_raw,
                override_scope_tokens,
                merged_scope_tokens,
            ),
            (
                "method",
                base_method_tokens_raw,
                override_method_tokens,
                merged_method_tokens,
            ),
            (
                "form",
                base_form_tokens_raw,
                override_form_tokens,
                merged_form_tokens,
            ),
            (
                "channel",
                base_channel_tokens_raw,
                override_channel_tokens,
                merged_channel_tokens,
            ),
        ):
            summary = _axis_drop_summary(
                axis_name, base_tokens, override_tokens, merged_tokens
            )
            if summary:
                axis_drop_parts.append(summary)

        if axis_drop_parts:
            notify(
                "GPT: Axes normalised (caps/incompatibilities); "
                + "; ".join(axis_drop_parts)
            )

        if not new_static:
            notify("GPT: Last recipe is not available to rerun")
            return

        # Build a lightweight object with the attributes expected by modelPrompt.
        class Match:
            pass

        match = Match()
        setattr(match, "staticPrompt", new_static)
        if new_completeness:
            setattr(match, "completenessModifier", new_completeness)
        if new_scope:
            setattr(match, "scopeModifier", new_scope)
        if new_method:
            setattr(match, "methodModifier", new_method)
        if new_form:
            setattr(match, "formModifier", new_form)
        if new_channel:
            setattr(match, "channelModifier", new_channel)
        if new_directional:
            setattr(match, "directionalModifier", new_directional)

        # Keep GPTState.last_recipe and structured fields in sync with the
        # effective recipe for this rerun.
        set_last_recipe_from_selection(
            new_static,
            new_completeness,
            new_scope,
            new_method,
            new_form,
            new_channel,
            new_directional,
        )

        try:
            print(
                "[gpt again] stored",
                f"recipe={GPTState.last_recipe!r} "
                f"static={GPTState.last_static_prompt!r} "
                f"C={GPTState.last_completeness!r} "
                f"S={GPTState.last_scope!r} "
                f"M={GPTState.last_method!r} "
                f"F={GPTState.last_form!r} "
                f"Ch={GPTState.last_channel!r} "
                f"D={GPTState.last_directional!r}",
            )
        except Exception:
            pass

        please_prompt = _safe_model_prompt(match)
        if not please_prompt:
            return

        # Resolve the source for this rerun:
        # - Prefer a cached snapshot of the last primary source messages so
        #   plain `model again` reuses the same content even if the live
        #   source (clipboard/selection/etc.) has changed.
        # - Fallback to the live default source when we have no snapshot.
        cached_messages = getattr(GPTState, "last_source_messages", [])
        if cached_messages:
            from copy import deepcopy

            class CachedSource(ModelSource):
                def __init__(self, messages):
                    self._messages = list(messages)

                def get_text(self):
                    return messages_to_string(self._messages)

                def format_messages(self):
                    return deepcopy(self._messages)

            source: ModelSource = CachedSource(cached_messages)
        else:
            source_key = getattr(GPTState, "last_again_source", "") or settings.get(
                "user.model_default_source"
            )
            source = create_model_source(source_key)

        dest_kind_value = (
            destination_kind
            or getattr(GPTState, "current_destination_kind", "")
            or settings.get("user.model_default_destination")
            or ""
        )
        dest_kind_value = str(dest_kind_value or "").strip()
        if dest_kind_value:
            try:
                GPTState.current_destination_kind = dest_kind_value
            except Exception:
                pass

        config = ApplyPromptConfiguration(
            please_prompt=please_prompt,
            model_source=source,
            additional_model_source=None,
            model_destination=create_model_destination(dest_kind_value),
        )

        actions.user.gpt_apply_prompt(config)

    def gpt_rerun_last_recipe_with_source(
        source: ModelSource,
        static_prompt: str,
        completeness: str,
        scope: Union[str, List[str]],
        method: Union[str, List[str]],
        directional: str,
        form: Union[str, List[str]] = "",
        channel: Union[str, List[str]] = "",
        destination_kind: str = "",
    ) -> None:
        """Rerun the last prompt recipe for an explicit source with optional axis overrides."""
        if _reject_if_request_in_flight():
            return
        # Remember this source key for subsequent plain `model again` calls.
        source_key = getattr(source, "modelSimpleSource", None)
        if isinstance(source_key, str) and source_key:
            GPTState.last_again_source = source_key
        # Delegate to the default-source variant, which will resolve the
        # actual ModelSource from the stored key and apply the same axis logic.
        UserActions.gpt_rerun_last_recipe(
            static_prompt,
            completeness,
            scope,
            method,
            directional,
            form,
            channel,
            destination_kind,
        )

    def gpt_pass(pass_configuration: PassConfiguration) -> None:
        """Passes a response from source to destination"""
        if _reject_if_request_in_flight():
            return
        source: ModelSource = pass_configuration.model_source
        destination: ModelDestination = pass_configuration.model_destination

        # Ensure pass flows respect the target destination (for example, file)
        # instead of any stale destination kind from a prior request.
        try:
            dest_kind = (getattr(destination, "kind", "") or "").lower()
            GPTState.current_destination_kind = dest_kind
        except Exception:
            try:
                GPTState.current_destination_kind = ""
            except Exception:
                pass

        session = PromptSession(destination)
        session.begin(reuse_existing=True)

        result = PromptResult.from_messages(source.format_messages())

        actions.user.gpt_insert_response(result, destination)

    def gpt_help() -> None:
        """Open the GPT help file in the web browser"""
        if _reject_if_request_in_flight():
            return
        # Build a consolidated, scannable help page from catalog + persona SSOT
        try:
            catalog = axis_catalog()
        except Exception:
            catalog = {}

        axis_lists = catalog.get("axis_list_tokens", {}) or {}
        static_catalog = catalog.get("static_prompts") or static_prompt_catalog()
        static_desc_overrides = (
            catalog.get("static_prompt_descriptions") or static_prompt_description_overrides()
        )

        def _axis_tokens(axis: str) -> list[str]:
            tokens = list(axis_lists.get(axis) or [])
            if tokens:
                return tokens
            try:
                return list(axis_docs_map(axis).keys())
            except Exception:
                return []

        current_dir = os.path.dirname(__file__)
        lists_dir = os.path.join(current_dir, "lists")

        def _read_list_lines(name: str) -> list[str]:
            path = os.path.join(lists_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    # Skip the first two lines (talon list header convention)
                    return f.readlines()[2:]
            except FileNotFoundError:
                return []

        def render_file_list_as_tables(
            title: str,
            filename: str,
            builder: Builder,
            comment_mode: str = "section_headers",
        ) -> None:
            lines = _read_list_lines(filename)
            if not lines:
                return

            builder.h2(title)

            table_open = False
            last_comment_block: list[str] = []
            last_was_blank = True

            def ensure_table_open():
                nonlocal table_open
                if not table_open:
                    builder.start_table(["Trigger", "Description"])
                    table_open = True

            def close_table_if_open():
                nonlocal table_open
                if table_open:
                    builder.end_table()
                    table_open = False

            for raw in lines:
                line = raw.strip()
                if not line:
                    last_was_blank = True
                    continue
                if line.startswith("#"):
                    header = line.lstrip("# ")
                    if comment_mode == "preceding_description":
                        if header:
                            last_comment_block.append(header)
                    else:
                        close_table_if_open()
                        if header:
                            builder.h3(header)
                    last_was_blank = False
                    continue

                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip()
                    if comment_mode == "preceding_description":
                        desc = " ".join(last_comment_block).strip() or parts[1].strip()
                        last_comment_block = []
                    else:
                        desc = parts[1].strip()
                    ensure_table_open()
                    builder.add_row([key, desc])
                    last_was_blank = False

            close_table_if_open()

        def render_token_table(
            title: str,
            tokens: list[str],
            builder: Builder,
            description_overrides: Optional[dict[str, str]] = None,
            allowed_tokens: Optional[set[str]] = None,
        ) -> None:
            if not tokens:
                return
            rows: list[tuple[str, str]] = []
            for token in sorted(tokens):
                if allowed_tokens is not None and token not in allowed_tokens:
                    continue
                desc_map = description_overrides or {}
                rows.append((token, desc_map.get(token, "")))
            if not rows:
                return
            builder.h2(title)
            builder.start_table(["Trigger", "Description"])
            for key, desc in rows:
                builder.add_row([key, desc])
            builder.end_table()

        builder = Builder()
        builder.title("Talon GPT Reference")
        builder.h1("Talon GPT Reference")

        builder.p(
            "Use modifiers after a static prompt to control completeness, method, "
            "scope, form, and channel. You normally say at most one or two modifiers per call."
        )

        builder.h2("How to use the helpers (ADR 006)")
        builder.ul(
            "Patterns: say 'model patterns' (or 'model coding patterns' / 'model writing patterns') and click a pattern or say its name (for example, 'debug bug') to run a curated recipe.",
            "Prompt pattern menu: say 'model pattern menu <prompt>' (for example, 'model pattern menu describe') to see a few generic recipes for that static prompt; click or say 'quick gist', 'deep narrow rigor', or 'bulleted summary' while the menu is open.",
            "Recap: after running a model command, check the confirmation window's 'Recipe:' line, or say 'model last recipe' to see the last combination in a notification.",
            "Grammar help: say 'model quick help' for an overview, or 'model show grammar' to see the last recipe and an exact 'model …' line you can repeat or adapt.",
            "From the confirmation window, use 'Show grammar help' or 'Open pattern menu' buttons to quickly inspect or tweak what you just ran.",
        )

        builder.h2("Replaced prompts (ADR 007)")
        builder.ul(
            "`simple` → use `describe` with `gist` + `plain` (or the “Simplify locally” pattern).",
            "`short` → use `describe` with `gist` + `tight` (or the “Tighten summary” pattern).",
            "`how to` / `incremental` → use `todo` or `bridge` with `steps` + `checklist`/`minimal` (or the “Extract todos” pattern).",
        )

        # Order for easy scanning with Cmd-F
        # Static prompts prefer descriptions from the shared static prompt
        # configuration façade so there is a single source of truth.
        render_token_table(
            "Static Prompts",
            list(static_catalog.get("talon_list_tokens") or []),
            builder,
            description_overrides=static_desc_overrides,
        )
        render_token_table(
            "Directional Modifiers",
            _axis_tokens("directional"),
            builder,
            description_overrides=axis_docs_map("directional"),
            allowed_tokens={"fog", "fig", "dig", "ong", "rog", "bog", "jog"},
        )
        render_token_table(
            "Completeness Modifiers",
            _axis_tokens("completeness"),
            builder,
            description_overrides=axis_docs_map("completeness"),
        )
        render_token_table(
            "Scope Modifiers",
            _axis_tokens("scope"),
            builder,
            description_overrides=axis_docs_map("scope"),
        )
        render_token_table(
            "Method Modifiers",
            _axis_tokens("method"),
            builder,
            description_overrides=axis_docs_map("method"),
        )
        render_token_table(
            "Form Modifiers",
            _axis_tokens("form"),
            builder,
            description_overrides=axis_docs_map("form"),
        )
        render_token_table(
            "Channel Modifiers",
            _axis_tokens("channel"),
            builder,
            description_overrides=axis_docs_map("channel"),
        )
        # Persona/intent axes come from the persona SSOT.
        from ..lib.personaConfig import persona_docs_map

        render_token_table(
            "Voice",
            list((persona_docs_map("voice") or {}).keys()),
            builder,
            description_overrides=persona_docs_map("voice"),
        )
        render_token_table(
            "Tone",
            list((persona_docs_map("tone") or {}).keys()),
            builder,
            description_overrides=persona_docs_map("tone"),
        )
        render_token_table(
            "Audience",
            list((persona_docs_map("audience") or {}).keys()),
            builder,
            description_overrides=persona_docs_map("audience"),
        )
        render_token_table(
            "Intent",
            list((persona_docs_map("intent") or {}).keys()),
            builder,
            description_overrides=persona_docs_map("intent"),
        )
        # For Sources/Destinations, descriptions live in the preceding comment lines
        render_file_list_as_tables(
            "Sources",
            "modelSource.talon-list",
            builder,
            comment_mode="preceding_description",
        )
        render_file_list_as_tables(
            "Destinations",
            "modelDestination.talon-list",
            builder,
            comment_mode="preceding_description",
        )

        builder.h2("Default settings examples")
        builder.ul(
            "Set defaults: 'model set completeness skim', 'model set scope narrow', "
            "'model set method steps', 'model set form bullets', 'model set channel slack'.",
            "Reset defaults: 'model reset writing' (persona + all defaults), or "
            "'model reset completeness', 'model reset scope', 'model reset method', "
            "'model reset form', 'model reset channel'.",
        )

        builder.render()

    def gpt_insert_text(text: str, destination: ModelDestination = Default()) -> None:
        """Insert text using the helpers here"""
        if _reject_if_request_in_flight():
            return
        result = PromptResult.from_messages([format_message(text)])
        actions.user.gpt_insert_response(result, destination)

    def gpt_open_browser(text: str) -> None:
        """Open a browser with the response"""
        if _reject_if_request_in_flight():
            return
        result = PromptResult.from_messages([format_message(text)])
        actions.user.gpt_insert_response(result, Browser())

    def gpt_search_engine(search_engine: str, source: ModelSource) -> str:
        """Format the source for searching with a search engine and open a search"""

        if _reject_if_request_in_flight():
            return ""

        prompt = f"""
        I want to search for the following using the {search_engine} search engine.
        Format the text into a succinct search to help me find what I'm looking for. Return only the text of the search query.
        Optimize the search for returning good search results leaving off anything that would not be useful in searching.
        Rather than searching for exact strings, I want to find a search that is as close as possible.
        I will take care of putting it into a search.
        """
        return actions.user.gpt_run_prompt(prompt, source)

    def gpt_insert_response(
        gpt_result: PromptPayload,
        destination: ModelDestination = Default(),
    ) -> None:
        """Insert a GPT result in a specified way"""
        try:
            text = getattr(gpt_result, "text", "") or ""
            if isinstance(text, str) and not text.strip():
                actions.app.notify("GPT: Request cancelled")
                return
        except Exception:
            pass
        # If we're already showing the response canvas (window destination),
        # avoid inserting to a surface to prevent accidental paste.
        try:
            if getattr(GPTState, "current_destination_kind", "") == "window":
                try:
                    actions.user.model_response_canvas_open()
                except Exception:
                    pass
                return
        except Exception:
            pass
        actions.user.confirmation_gui_close()
        destination.insert(gpt_result)

    def gpt_get_source_text(spoken_text: str) -> str:
        """Get the source text that is will have the prompt applied to it"""
        if _reject_if_request_in_flight():
            return ""
        return create_model_source(spoken_text).get_text()

    def gpt_prepare_message(
        model_source: ModelSource,
        additional_model_source: Optional[ModelSource],
        prompt: str,
        destination: ModelDestination = Default(),
    ) -> PromptSession:
        """Get the source text that will have the prompt applied to it"""

        if _reject_if_request_in_flight():
            return PromptSession(destination)

        session = PromptSession(destination)
        session.prepare_prompt(prompt, model_source, additional_model_source)
        return session


def _safe_model_prompt(match) -> str:
    """Wrap modelPrompt to surface migration errors (for example, legacy style)."""
    try:
        return modelPrompt(match)
    except ValueError as exc:
        notify(f"GPT: {exc}")
        return ""


def gpt_beta_paste_prompt(match: str) -> None:
    """Module-level beta pass helper; delegates to the action for coverage."""
    return UserActions.gpt_beta_paste_prompt(match)


def _suggest_prompt_recipes_core_impl(source: ModelSource, subject: str) -> None:
    """Core suggest handler; shared by action entrypoints to avoid deprecated calls."""
    if _reject_if_request_in_flight():
        return

    subject = subject or ""
    try:
        content = source.get_text()
    except Exception:
        # Underlying helpers (for example, Context/GPTResponse) already
        # notify the user when no content is available. Keep any cached
        # suggestions intact so `model suggestions` can still reopen the
        # last successful set after a transient failure to read the source.
        return

    content_text = str(content)
    if GPTState.debug_enabled:
        preview = content_text[:200].replace("\n", "\\n")
        notify(
            "GPT debug: model suggest content length="
            f"{len(content_text)}, preview={preview!r}"
        )

    if not content_text.strip() and not subject.strip():
        # If we have neither source content nor a subject, keep any cached
        # suggestions so they remain available via `model suggestions`.
        notify("GPT: No source or subject available for suggestions")
        return

    # Remember the canonical source key used for these suggestions so the
    # suggestion GUI can both display and reuse it when running recipes.
    source_key = getattr(source, "modelSimpleSource", "")
    if isinstance(source_key, str) and source_key:
        suggest_source_key = source_key
    else:
        suggest_source_key = ""

    # For suggestions, avoid opening the response canvas as a progress
    # surface; treat this as a distinct destination kind so the default
    # RequestUI controller uses the pill instead of the response viewer.
    prev_dest_kind = getattr(GPTState, "current_destination_kind", "")
    try:
        GPTState.current_destination_kind = "suggest"
    except Exception:
        prev_dest_kind = ""

    axis_docs = _build_axis_docs()
    persona_intent_docs = _build_persona_intent_docs()
    static_prompt_docs = _build_static_prompt_docs()

    # Capture current persona/intent + axis defaults (canonical tokens only)
    # so the LLM can tailor suggestions and the UI can surface what was sent.
    sys_prompt = getattr(GPTState, "system_prompt", None)
    context_snapshot = _suggest_context_snapshot(sys_prompt)
    try:
        GPTState.last_suggest_context = dict(context_snapshot)
    except Exception:
        pass
    try:
        GPTState.last_suggest_subject = str(subject or "")
    except Exception:
        pass
    try:
        GPTState.last_suggest_content = content_text
    except Exception:
        pass

    stance_lines: list[str] = []
    persona_bits = [
        context_snapshot.get("voice", "").strip(),
        context_snapshot.get("audience", "").strip(),
        context_snapshot.get("tone", "").strip(),
    ]
    persona_bits = [b for b in persona_bits if b]
    if persona_bits:
        stance_lines.append("Persona (Who): " + " · ".join(persona_bits))
    if context_snapshot.get("intent"):
        stance_lines.append(f"Intent (Why): {context_snapshot['intent']}")
    axis_bits: list[str] = []
    for label, key in (
        ("Completeness", "completeness"),
        ("Scope", "scope"),
        ("Method", "method"),
        ("Form", "form"),
        ("Channel", "channel"),
    ):
        val = context_snapshot.get(key, "").strip()
        if val:
            axis_bits.append(f"{label}: {val}")
    if axis_bits:
        stance_lines.append("Defaults: " + " · ".join(axis_bits))
    if not stance_lines:
        stance_lines.append("Persona/Intent/Defaults: (none set)")

    prompt_subject = subject.strip() if subject else "unspecified"
    context_lines = _format_context_lines(_suggest_hydrated_context(sys_prompt))
    if not context_lines:
        context_lines = stance_lines
    user_text = _suggest_prompt_text(
        axis_docs=axis_docs,
        persona_intent_docs=persona_intent_docs,
        static_prompt_docs=static_prompt_docs,
        prompt_subject=prompt_subject,
        content_text=content_text,
        context_lines=context_lines,
    )

    try:
        sys_messages = [
            format_message(m)
            for m in getattr(GPTState.system_prompt, "format_as_array", lambda: [])()
        ]
        sys_debug = " | ".join(m.get("text", str(m)) for m in sys_messages)
    except Exception:
        sys_debug = ""
    try:
        snippet = user_text[:1200].replace("\n", "\\n")
        print(
            "GPT model suggest prompt (truncated to 1200 chars): "
            f"{snippet} | system={sys_debug}"
        )
    except Exception:
        pass

    # Run suggestions through a silent destination so we never open the
    # confirmation surface for this helper. Keep a clipboard fallback to
    # expose the raw output without popping UI if parsing/GUI fails.
    destination = Silent()
    fallback_destination = Clipboard()
    session = PromptSession(destination)
    # Always emit UI lifecycle events so the pill shows even when the
    # pipeline is swapped out or does not drive the request bus.
    manual_request_id: Optional[str] = None
    try:
        manual_request_id = emit_begin_send()
        _suppress_inflight_notify_request_id = manual_request_id
        try:
            GPTState.suppress_inflight_notify_request_id = manual_request_id
        except Exception:
            pass
    except Exception:
        manual_request_id = None
    # Suppress response canvas while suggestions are running so streaming
    # text never opens the confirmation viewer.
    prev_suppress = getattr(GPTState, "suppress_response_canvas", False)
    GPTState.suppress_response_canvas = True
    def _restore_request_state():
        try:
            GPTState.suppress_response_canvas = prev_suppress
        except Exception:
            pass
        try:
            GPTState.current_destination_kind = prev_dest_kind
        except Exception:
            pass
        try:
            # Clear the suppression flag so future requests notify as normal.
            if manual_request_id is not None and getattr(
                GPTState, "suppress_inflight_notify_request_id", None
            ) == manual_request_id:
                GPTState.suppress_inflight_notify_request_id = None
            if manual_request_id is not None and _suppress_inflight_notify_request_id == manual_request_id:
                _suppress_inflight_notify_request_id = None
        except Exception:
            pass

    def _process_suggest_result(result) -> None:
        # Attempt to parse the result text into structured suggestions so
        # future loops (for example, a suggestions GUI) can reuse them
        # without re-calling the model. Prefer the JSON shape described in
        # ADR 042; fall back to the legacy line-based format if needed.
        suggestions: list[dict[str, str]] = []
        raw_text = getattr(result, "text", "") or ""
        raw_text = str(raw_text).strip()
        debug_mode = bool(getattr(GPTState, "debug_enabled", False))
        if debug_mode:
            try:
                print(f"GPT model suggest raw text ({len(raw_text)} chars): {raw_text[:200]!r}")
            except Exception:
                pass

        def _normalise_recipe(value: str) -> str:
            """Normalise a recipe string and enforce a single static prompt token.

            This preserves the existing behaviour: we require a single
            <staticPrompt> token and a single known directional token; we drop
            any suggestion that does not meet these constraints. Axis caps are
            enforced per ADR 048 (scope≤2, method≤3, form=1, channel=1).
            """
            recipe_value = (value or "").strip()
            if not recipe_value:
                return ""
            parts = [t.strip() for t in recipe_value.split("·") if t.strip()]
            if not parts:
                return ""
            static_tokens = parts[0].split()
            if len(static_tokens) > 1:
                parts[0] = static_tokens[0]
            raw_directional = parts[-1] if len(parts) > 1 else ""
            directional = _canonical_axis_value("directional", raw_directional)
            if not directional:
                return ""
            parts[-1] = directional
            # Enforce axis caps on the remaining segments when present.
            # Expected shape: static · completeness · scope · method · form · channel · directional
            if len(parts) >= 6:
                scope_tokens = parts[2].split() if len(parts) > 2 else []
                method_tokens = parts[3].split() if len(parts) > 3 else []
                form_tokens = parts[4].split() if len(parts) > 4 else []
                channel_tokens = parts[5].split() if len(parts) > 5 else []
                if scope_tokens:
                    parts[2] = " ".join(scope_tokens[-2:])
                if method_tokens:
                    parts[3] = " ".join(method_tokens[-3:])
                if form_tokens:
                    parts[4] = form_tokens[-1]
                if channel_tokens:
                    parts[5] = channel_tokens[-1]
            return " · ".join(parts)

        if raw_text:
            parsed_from_json = False
            # First, try the structured JSON format.
            try:
                data = json.loads(raw_text)
                if isinstance(data, dict):
                    raw_suggestions = data.get("suggestions", [])
                    if isinstance(raw_suggestions, list):
                        debug_failures: list[dict[str, object]] = []
                        for item in raw_suggestions:
                            if not isinstance(item, dict):
                                continue
                            name = str(item.get("name", "")).strip()
                            recipe_value = str(item.get("recipe", "")).strip()
                            persona_voice = str(item.get("persona_voice", "")).strip()
                            persona_audience = str(
                                item.get("persona_audience", "")
                            ).strip()
                            persona_tone = str(item.get("persona_tone", "")).strip()
                            intent_purpose = str(item.get("intent_purpose", "")).strip()
                            raw_stance = str(item.get("stance_command", "")).strip()
                            why_text = str(item.get("why", "")).strip()
                            reasoning = str(item.get("reasoning", "")).strip()

                            debug_record: dict[str, object] = {
                                "name": name,
                                "raw": {
                                    "recipe": recipe_value,
                                    "persona_voice": persona_voice,
                                    "persona_audience": persona_audience,
                                    "persona_tone": persona_tone,
                                    "intent_purpose": intent_purpose,
                                    "stance_command": raw_stance,
                                    "reasoning": reasoning,
                                },
                                "failures": [],
                            }
                            failures = cast(list[str], debug_record["failures"])

                            if not name:
                                failures.append("missing_name")
                            if not recipe_value:
                                failures.append("missing_recipe")
                            if not name or not recipe_value:
                                if failures:
                                    debug_failures.append(debug_record)
                                continue

                            recipe = _normalise_recipe(recipe_value)
                            if not recipe:
                                failures.append("recipe_invalid")
                                debug_failures.append(debug_record)
                                continue

                            def _validated_persona_value(axis: str, raw_value: str) -> str:
                                token = _canonical_persona_value(axis, raw_value)
                                if token:
                                    return token
                                if str(raw_value or "").strip():
                                    failures.append(f"{axis}_invalid")
                                return ""

                            persona_voice = _validated_persona_value(
                                "voice", persona_voice
                            )
                            persona_audience = _validated_persona_value(
                                "audience", persona_audience
                            )
                            persona_tone = _validated_persona_value("tone", persona_tone)
                            intent_purpose = _validated_persona_value(
                                "intent", intent_purpose
                            )

                            entry: dict[str, str] = {"name": name, "recipe": recipe}
                            if persona_voice:
                                entry["persona_voice"] = persona_voice
                            if persona_audience:
                                entry["persona_audience"] = persona_audience
                            if persona_tone:
                                entry["persona_tone"] = persona_tone
                            if intent_purpose:
                                entry["intent_purpose"] = intent_purpose

                            if raw_stance:
                                if _valid_stance_command(raw_stance):
                                    entry["stance_command"] = raw_stance
                                else:
                                    failures.append("stance_invalid_form")

                            if why_text:
                                entry["why"] = why_text
                            if reasoning:
                                entry["reasoning"] = reasoning

                            suggestions.append(entry)
                            if failures:
                                debug_failures.append(debug_record)

                        if debug_failures and getattr(GPTState, "debug_enabled", False):
                            try:
                                lines: list[str] = []
                                for record in debug_failures[:5]:
                                    name = str(record.get("name") or "<unnamed>")
                                    raw = cast(dict[str, object], record.get("raw", {}))
                                    failures = cast(
                                        list[str], record.get("failures") or []
                                    )
                                    recipe_val = str(raw.get("recipe", ""))
                                    stance_val = str(raw.get("stance_command", ""))
                                    reasoning_val = str(raw.get("reasoning", ""))
                                    line = (
                                        f"{name}: {','.join(failures)} | "
                                        f"recipe={recipe_val!r} stance={stance_val!r}"
                                    )
                                    if reasoning_val:
                                        line += f" | reasoning={reasoning_val[:80]!r}"
                                    lines.append(line)
                                print(
                                    "GPT model suggest: validation failures:\n"
                                    + "\n".join(lines)
                                )
                            except Exception:
                                pass

                parsed_from_json = bool(suggestions)
            except Exception:
                parsed_from_json = False

            # Legacy fallback: parse pipe-separated lines if JSON was not usable.
            if not parsed_from_json:
                for raw_line in raw_text.splitlines():
                    line = raw_line.strip()
                    if not line or "|" not in line:
                        continue
                    segments = [seg.strip() for seg in line.split("|") if seg.strip()]
                    if len(segments) < 2:
                        continue
                    name_part = segments[0]
                    if "Name:" in name_part:
                        _, name_value = name_part.split("Name:", 1)
                        name = name_value.strip()
                    else:
                        name = name_part.strip().strip(":")
                    if not name:
                        continue

                    recipe_value = ""
                    for seg in segments[1:]:
                        if "Recipe:" in seg:
                            _, recipe_part = seg.split("Recipe:", 1)
                            recipe_value = recipe_part.strip()
                            break
                    if not recipe_value and len(segments) > 1:
                        candidate = segments[1].strip()
                        if "·" in candidate:
                            recipe_value = candidate
                    recipe = _normalise_recipe(recipe_value)
                    if not recipe:
                        continue

                    stance_command = ""
                    why_text = ""
                    for seg in segments[1:]:
                        if "Stance:" in seg:
                            _, stance_part = seg.split("Stance:", 1)
                            stance_command = stance_part.strip()
                        elif "Why:" in seg:
                            _, why_part = seg.split("Why:", 1)
                            why_text = why_part.strip()

                    entry: dict[str, str] = {"name": name, "recipe": recipe}
                    if stance_command:
                        if _valid_stance_command(stance_command):
                            entry["stance_command"] = stance_command
                        elif getattr(GPTState, "debug_enabled", False):
                            try:
                                print(
                                    "GPT model suggest: invalid legacy stance for "
                                    f"'{name}': {stance_command}"
                                )
                            except Exception:
                                pass
                    if why_text:
                        entry["why"] = why_text
                    suggestions.append(entry)

        if debug_mode or not suggestions:
            try:
                print(f"GPT model suggest parsed {len(suggestions)} suggestions")
            except Exception:
                pass

        if suggestions:
            record_suggestions(suggestions, suggest_source_key)
            try:
                try:
                    notify("GPT: Opening prompt recipe suggestions window")
                except Exception:
                    pass
                actions.user.model_prompt_recipe_suggestions_gui_open()
                try:
                    notify("GPT: Prompt recipe suggestions window opened")
                except Exception:
                    pass
                # When the suggestion GUI opens successfully, we do not also
                # open the confirmation GUI; the picker becomes the primary
                # surface for these recipes.
            except Exception as exc:
                try:
                    notify(
                        f"GPT: Suggestion GUI unavailable; inserting raw suggestions instead ({exc})"
                    )
                except Exception:
                    pass
                # If the GUI is not available for any reason, still insert the
                # raw suggestions so the feature remains usable.
                actions.user.gpt_insert_response(result, fallback_destination)
        else:
            # If we didn't recognise any suggestions, fall back to the normal
            # insertion flow so the user can still see the raw output.
            actions.user.gpt_insert_response(result, fallback_destination)

    # Start a fresh request for suggestions so we don't accidentally
    # reuse the previous GPTState.request (for example, from the last
    # `model` call). This avoids leaking prior prompt content into
    # the suggestion meta-prompt.
    session.begin()
    session.add_system_prompt()
    session.add_messages([format_messages("user", [format_message(user_text)])])

    raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
    block = False if raw_block is None else bool(raw_block)
    # In test environments, prefer blocking so unit tests observe parsed suggestions immediately.
    try:
        import os
        if os.environ.get("PYTEST_CURRENT_TEST"):
            block = True
    except Exception:
        pass

    def _finish_suggest(handle=None):
        result = None
        try:
            if handle is not None:
                try:
                    handle.wait(timeout=None)
                except Exception:
                    pass
                result = getattr(handle, "result", None)
                error = getattr(handle, "error", None)
                if isinstance(error, BaseException):
                    raise error
                if result is None:
                    result = _prompt_pipeline.complete(session)
            else:
                result = _prompt_pipeline.complete(session)
            if manual_request_id is not None:
                try:
                    emit_complete(request_id=manual_request_id)
                except Exception:
                    pass
        except Exception as exc:
            if manual_request_id is not None:
                try:
                    emit_fail(str(exc), request_id=manual_request_id)
                except Exception:
                    pass
            _restore_request_state()
            return

        _restore_request_state()
        if result is not None:
            _process_suggest_result(result)

    try:
        handle = _prompt_pipeline.complete_async(session)
    except Exception:
        handle = None

    if block or handle is None:
        _finish_suggest(handle)
    else:
        threading.Thread(target=_finish_suggest, args=(handle,), daemon=True).start()
