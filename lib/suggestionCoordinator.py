"""Coordinator for suggestion/rerun state (last suggested recipes, source keys)."""

from __future__ import annotations

from typing import Iterable, List, Dict, Optional, Any

from .modelState import GPTState
from .axisMappings import axis_registry_tokens
from .modelHelpers import notify
from .personaConfig import persona_intent_maps


def _recipe_has_directional(recipe: str) -> bool:
    """Return True when the recipe string includes a known directional token."""
    tokens = [tok.strip() for tok in recipe.replace("·", " ").split() if tok.strip()]
    directionals = axis_registry_tokens("directional")
    return any(tok in directionals for tok in tokens)


def record_suggestions(
    suggestions: Iterable[dict[str, str]], source_key: str | None
) -> None:
    """Persist the latest suggestions and source key in GPTState."""
    debug_mode = bool(getattr(GPTState, "debug_enabled", False))
    try:
        maps = persona_intent_maps()
    except Exception:
        maps = None

    suggestions_list: list[dict[str, str]] = []
    skip_counts: dict[str, int] = {}

    persona_axis_catalog = {
        axis: {token.lower(): token for token in axis_registry_tokens(axis)}
        for axis in ("voice", "audience", "tone")
    }
    persona_axis_aliases: dict[str, dict[str, str]] = {}
    if maps is not None:
        raw_aliases = getattr(maps, "persona_axis_tokens", {}) or {}
        persona_axis_aliases = {
            axis: {str(key).lower(): str(value) for key, value in aliases.items()}
            for axis, aliases in raw_aliases.items()
        }

    def _canonical_persona_axis(axis: str, raw: str) -> tuple[str, bool]:
        token = str(raw or "").strip()
        if not token:
            return "", True
        lower = token.lower()
        alias_map = persona_axis_aliases.get(axis, {})
        canonical = alias_map.get(lower)
        if canonical:
            return canonical, True
        catalog_map = persona_axis_catalog.get(axis, {})
        canonical = catalog_map.get(lower)
        if canonical:
            return canonical, True
        return token, False

    for item in suggestions:
        recipe = str(item.get("recipe", "") or "").strip()
        if recipe and not _recipe_has_directional(recipe):
            if debug_mode:
                print(
                    f"record_suggestions skipped entry without directional: {recipe!r}"
                )
            notify(
                "GPT: Suggestion skipped because it has no directional lens; expected fog/fig/dig/ong/rog/bog/jog."
            )
            skip_counts["missing_directional"] = (
                skip_counts.get("missing_directional", 0) + 1
            )
            continue
        data = dict(item)
        if maps is not None:
            persona_key = str(data.get("persona_preset_key") or "").strip()
            persona_label = str(data.get("persona_preset_label") or "").strip()
            persona_spoken = str(data.get("persona_preset_spoken") or "").strip()

            persona_voice_raw = str(data.get("persona_voice") or "").strip()
            persona_voice, voice_valid = _canonical_persona_axis(
                "voice", persona_voice_raw
            )
            persona_audience_raw = str(data.get("persona_audience") or "").strip()
            persona_audience, audience_valid = _canonical_persona_axis(
                "audience", persona_audience_raw
            )
            persona_tone_raw = str(data.get("persona_tone") or "").strip()
            persona_tone, tone_valid = _canonical_persona_axis("tone", persona_tone_raw)

            preset = None
            if persona_key:
                preset = maps.persona_presets.get(persona_key)
            else:
                for alias in (persona_spoken, persona_label):
                    alias_l = alias.lower()
                    if alias_l:
                        canonical = maps.persona_preset_aliases.get(alias_l)
                        if canonical:
                            preset = maps.persona_presets.get(canonical)
                            if preset is not None:
                                persona_key = canonical
                                break
            if preset is None and (persona_voice or persona_audience or persona_tone):
                voice_l = persona_voice.lower()
                audience_l = persona_audience.lower()
                tone_l = persona_tone.lower()
                for candidate in maps.persona_presets.values():
                    c_voice = (candidate.voice or "").lower()
                    c_audience = (candidate.audience or "").lower()
                    c_tone = (candidate.tone or "").lower()
                    if c_voice and c_voice != voice_l:
                        continue
                    if c_audience and c_audience != audience_l:
                        continue
                    if c_tone and c_tone != tone_l:
                        continue
                    if not (c_voice or c_audience or c_tone):
                        continue
                    preset = candidate
                    persona_key = candidate.key
                    break

            persona_hints_present = any(
                (
                    persona_key,
                    persona_label,
                    persona_spoken,
                    persona_voice,
                    persona_audience,
                    persona_tone,
                )
            )
            preset_alias_hints_present = any(
                (persona_key, persona_label, persona_spoken)
            )
            axis_hints_valid = voice_valid and audience_valid and tone_valid
            if preset is None and persona_hints_present:
                if preset_alias_hints_present or not axis_hints_valid:
                    notify(
                        "GPT: Suggestion skipped because its persona preset is unknown; regenerate persona lists and try again."
                    )
                    skip_counts["unknown_persona"] = (
                        skip_counts.get("unknown_persona", 0) + 1
                    )
                    continue

            if preset is not None:
                if not persona_key:
                    persona_key = preset.key
                if not persona_label:
                    persona_label = preset.label or preset.key
                if not persona_spoken:
                    persona_spoken = preset.spoken or persona_label or preset.key
                if not persona_voice:
                    persona_voice = preset.voice or ""
                if not persona_audience:
                    persona_audience = preset.audience or ""
                if not persona_tone:
                    persona_tone = preset.tone or ""
                data["persona_preset_key"] = persona_key
                data["persona_preset_label"] = persona_label
                data["persona_preset_spoken"] = persona_spoken

            if persona_voice:
                data["persona_voice"] = persona_voice
            if persona_audience:
                data["persona_audience"] = persona_audience
            if persona_tone:
                data["persona_tone"] = persona_tone

            intent_key = str(data.get("intent_preset_key") or "").strip()
            intent_label = str(data.get("intent_preset_label") or "").strip()
            intent_display = str(data.get("intent_display") or "").strip()
            intent_purpose = str(data.get("intent_purpose") or "").strip()

            canonical_intent = ""
            if intent_key:
                canonical_intent = intent_key
            else:
                for alias in (intent_display, intent_label, intent_purpose):
                    alias_l = alias.lower()
                    if alias_l:
                        canonical_intent = (
                            maps.intent_preset_aliases.get(alias_l)
                            or maps.intent_synonyms.get(alias_l)
                            or ""
                        )
                        if canonical_intent:
                            break
            if not canonical_intent and intent_purpose:
                canonical_intent = (
                    maps.intent_synonyms.get(intent_purpose.lower()) or intent_purpose
                )

            intent_preset = (
                maps.intent_presets.get(canonical_intent) if canonical_intent else None
            )
            intent_hints_present = any(
                (intent_key, intent_label, intent_display, intent_purpose)
            )
            if intent_preset is None and intent_hints_present:
                notify(
                    "GPT: Suggestion skipped because its intent preset is unknown; regenerate intent lists and try again."
                )
                skip_counts["unknown_intent"] = skip_counts.get("unknown_intent", 0) + 1
                continue
            if intent_preset is not None:
                if not intent_key:
                    intent_key = intent_preset.key
                    data["intent_preset_key"] = intent_key
                if not intent_label:
                    intent_label = intent_preset.label or intent_preset.key
                    data["intent_preset_label"] = intent_label
                if not intent_purpose:
                    intent_purpose = intent_preset.intent
                    data["intent_purpose"] = intent_purpose
                display_value = maps.intent_display_map.get(
                    intent_preset.key
                ) or maps.intent_display_map.get(intent_preset.intent)
                if display_value and not intent_display:
                    intent_display = display_value
                    data["intent_display"] = intent_display

        suggestions_list.append(data)
    GPTState.last_suggested_recipes = suggestions_list
    GPTState.last_suggest_source = source_key or ""
    GPTState.last_suggest_skip_counts = dict(skip_counts)

    if skip_counts:
        total_skipped = sum(skip_counts.values())
        breakdown = ", ".join(
            f"{key}={value}" for key, value in sorted(skip_counts.items()) if value > 0
        )
        message = "GPT: Skipped"
        if total_skipped == 1:
            message += " 1 suggestion"
        else:
            message += f" {total_skipped} suggestions"
        if breakdown:
            message += f"; breakdown: {breakdown}"
        notify(message)

    if debug_mode:
        try:
            print(f"record_suggestions stored {len(suggestions_list)} suggestions")
        except Exception:
            pass


def last_suggestions() -> tuple[list[dict[str, str]], str]:
    """Return the last suggestions and source key (empty if none)."""
    recipes = getattr(GPTState, "last_suggested_recipes", []) or []
    source = getattr(GPTState, "last_suggest_source", "") or ""
    return list(recipes), source


def suggestion_entries() -> list[Dict[str, str]]:
    """Return validated suggestion entries (name+recipe only)."""
    recipes = getattr(GPTState, "last_suggested_recipes", []) or []
    entries: list[Dict[str, str]] = []
    for item in recipes:
        name = item.get("name")
        recipe = item.get("recipe")
        if name and recipe:
            entries.append({"name": str(name), "recipe": str(recipe)})
    return entries


def suggestion_skip_counts() -> dict[str, int]:
    """Return counts of skipped suggestions keyed by reason code."""

    stats = getattr(GPTState, "last_suggest_skip_counts", {}) or {}
    result: dict[str, int] = {}
    for key, value in stats.items():
        try:
            count = int(value)
        except Exception:
            continue
        if count > 0:
            result[str(key)] = count
    return result


def suggestion_source(default_source: Optional[str] = None) -> str:
    """Return the stored suggestion source key or the provided default."""
    source = getattr(GPTState, "last_suggest_source", "") or ""
    if source:
        return source
    return default_source or ""


def suggestion_grammar_phrase(
    recipe: str,
    source_key: str | None = None,
    spoken_map: Optional[dict[str, str]] = None,
) -> str:
    """Build a speakable grammar phrase for a suggestion recipe."""
    spoken_source = ""
    if spoken_map and source_key:
        spoken_source = spoken_map.get(source_key, "")
    base_recipe = recipe.replace(" · ", " ").strip()
    if spoken_source:
        return f"model run {spoken_source} {base_recipe}".strip()
    return f"model run {base_recipe}".strip()


def _tokens(value) -> list[str]:
    if isinstance(value, list):
        return [str(v) for v in value if str(v)]
    if isinstance(value, str):
        return [tok for tok in value.split() if tok]
    return []


def _directional_token(value: str | list[str]) -> str:
    """Return a single directional token (last-wins when multiple are provided)."""
    tokens = _tokens(value)
    if not tokens:
        return ""
    # Enforce single directional per ADR 048; prefer the last spoken token.
    return tokens[-1]


def last_recipe_snapshot() -> dict[str, object]:
    """Return the last recipe/static/axis tokens in a normalised form."""
    axes_state = getattr(GPTState, "last_axes", {}) or {}

    def _axis(axis: str, fallback: str = "") -> list[str]:
        tokens = axes_state.get(axis)
        if isinstance(tokens, list) and tokens:
            return [str(t) for t in tokens if str(t)]
        return _tokens(fallback)

    recipe_str = getattr(GPTState, "last_recipe", "") or ""
    directional_tokens = axes_state.get("directional")
    if isinstance(directional_tokens, list) and directional_tokens:
        directional = _directional_token(directional_tokens)
    else:
        directional = _directional_token(getattr(GPTState, "last_directional", ""))

    snapshot: dict[str, object] = {
        "recipe": recipe_str,
        "static_prompt": getattr(GPTState, "last_static_prompt", "") or "",
        "completeness": (
            _axis("completeness", getattr(GPTState, "last_completeness", "")) or [""]
        )[0],
        "scope_tokens": _axis("scope", getattr(GPTState, "last_scope", "")),
        "method_tokens": _axis("method", getattr(GPTState, "last_method", "")),
        "form_tokens": _axis("form", getattr(GPTState, "last_form", "")),
        "channel_tokens": _axis("channel", getattr(GPTState, "last_channel", "")),
        "directional": directional,
    }

    context_hydrated = _hydrate_context_aliases(
        getattr(GPTState, "last_suggest_context", {}) or {}
    )
    for key in (
        "persona_preset_key",
        "persona_preset_label",
        "persona_preset_spoken",
        "persona_voice",
        "persona_audience",
        "persona_tone",
        "intent_preset_key",
        "intent_preset_label",
        "intent_display",
        "intent_purpose",
    ):
        if key in context_hydrated:
            snapshot[key] = context_hydrated[key]

    return snapshot


def recipe_header_lines_from_snapshot(snapshot: dict[str, object]) -> list[str]:
    """Build axis/recipe header lines from a last_recipe_snapshot dict.

    This keeps the formatting of recipe/axis headers consistent across
    snapshot surfaces (for example, source snapshots and response
    destinations) while allowing each caller to prepend its own
    saved_at/model/source_type fields.
    """

    header_lines: list[str] = []

    def _text(value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if value is None:
            return ""
        return str(value).strip()

    recipe = snapshot.get("recipe", "") or ""
    if recipe:
        header_lines.append(f"recipe: {recipe}")

    completeness = snapshot.get("completeness", "") or ""
    if completeness:
        header_lines.append(f"completeness: {completeness}")

    for axis in ("scope", "method", "form", "channel"):
        tokens = snapshot.get(f"{axis}_tokens", []) or []
        if isinstance(tokens, list) and tokens:
            joined = " ".join(str(t) for t in tokens if str(t).strip())
            if joined:
                header_lines.append(f"{axis}_tokens: {joined}")

    directional = snapshot.get("directional", "") or ""
    if directional:
        header_lines.append(f"directional: {directional}")

    persona_key = _text(snapshot.get("persona_preset_key"))
    persona_label = _text(snapshot.get("persona_preset_label"))
    persona_spoken = _text(snapshot.get("persona_preset_spoken"))
    persona_voice = _text(snapshot.get("persona_voice"))
    persona_audience = _text(snapshot.get("persona_audience"))
    persona_tone = _text(snapshot.get("persona_tone"))

    if any(
        (
            persona_key,
            persona_label,
            persona_spoken,
            persona_voice,
            persona_audience,
            persona_tone,
        )
    ):
        descriptor = persona_key or persona_label or persona_spoken or "persona"
        say_hint = persona_spoken or persona_label or persona_key or descriptor
        details: list[str] = []
        if persona_label and persona_label != descriptor:
            details.append(f"label={persona_label}")
        if say_hint:
            details.append(f"say: persona {say_hint}")
        axis_bits: list[str] = []
        if persona_voice:
            axis_bits.append(f"voice={persona_voice}")
        if persona_audience:
            axis_bits.append(f"audience={persona_audience}")
        if persona_tone:
            axis_bits.append(f"tone={persona_tone}")
        if axis_bits:
            details.append("axes " + ", ".join(axis_bits))
        else:
            details.append("axes none")
        header_lines.append(f"persona_preset: {descriptor} ({'; '.join(details)})")

    intent_key = _text(snapshot.get("intent_preset_key"))
    intent_label = _text(snapshot.get("intent_preset_label"))
    intent_display = _text(snapshot.get("intent_display"))
    intent_purpose = _text(snapshot.get("intent_purpose"))

    if any((intent_key, intent_label, intent_display, intent_purpose)):
        descriptor = (
            intent_key or intent_display or intent_label or intent_purpose or "intent"
        )
        say_hint = intent_display or intent_label or intent_key or descriptor
        details = []
        if intent_label and intent_label != descriptor:
            details.append(f"label={intent_label}")
        if intent_display and intent_display != descriptor:
            details.append(f"display={intent_display}")
        if say_hint:
            details.append(f"say: intent {say_hint}")
        if intent_purpose:
            details.append(f"purpose={intent_purpose}")
        header_lines.append(f"intent_preset: {descriptor} ({'; '.join(details)})")

    return header_lines


def last_recap_snapshot() -> dict[str, str]:
    """Return last response/recipe/meta for recap surfaces."""
    return {
        "recipe": getattr(GPTState, "last_recipe", "") or "",
        "response": getattr(GPTState, "last_response", "") or "",
        "meta": getattr(GPTState, "last_meta", "") or "",
        "directional": getattr(GPTState, "last_directional", "") or "",
    }


def clear_recap_state() -> None:
    """Reset recap-related last_* fields."""
    GPTState.last_response = ""
    GPTState.last_meta = ""
    GPTState.last_recipe = ""
    GPTState.last_directional = ""
    GPTState.last_static_prompt = ""
    GPTState.last_completeness = ""
    GPTState.last_scope = ""
    GPTState.last_method = ""
    GPTState.last_form = ""
    GPTState.last_channel = ""
    GPTState.last_directional = ""
    GPTState.last_axes = {
        "completeness": [],
        "scope": [],
        "method": [],
        "form": [],
        "channel": [],
        "directional": [],
    }


def set_last_recipe_from_selection(
    static_prompt: str,
    completeness: str,
    scope: str | list[str],
    method: str | list[str],
    form: str | list[str] = "",
    channel: str | list[str] = "",
    directional: str = "",
) -> None:
    """Update GPTState last_* fields after running a suggestion."""
    static_token = static_prompt or ""
    completeness_token = completeness or ""
    scope_tokens = _tokens(scope)
    method_tokens = _tokens(method)
    form_tokens = _tokens(form)
    channel_tokens = _tokens(channel)
    recipe_parts = [static_token] if static_token else []
    directional_token = _directional_token(directional)

    for token in (
        completeness_token,
        " ".join(scope_tokens),
        " ".join(method_tokens),
        " ".join(form_tokens),
        " ".join(channel_tokens),
        directional_token,
    ):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_token
    GPTState.last_completeness = completeness_token
    GPTState.last_scope = " ".join(scope_tokens)
    GPTState.last_method = " ".join(method_tokens)
    GPTState.last_form = " ".join(form_tokens)
    GPTState.last_channel = " ".join(channel_tokens)
    GPTState.last_directional = directional_token
    GPTState.last_axes = {
        "completeness": [completeness_token] if completeness_token else [],
        "scope": scope_tokens,
        "method": method_tokens,
        "form": form_tokens,
        "channel": channel_tokens,
        "directional": [directional_token] if directional_token else [],
    }


def suggestion_entries_with_metadata() -> list[dict[str, str]]:
    """Return raw suggestion dicts (including optional stance metadata)."""
    recipes = getattr(GPTState, "last_suggested_recipes", []) or []
    entries: list[dict[str, str]] = []
    for item in recipes:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        recipe = item.get("recipe")
        if not name or not recipe:
            continue
        entries.append(dict(item))
    return entries


def _hydrate_context_aliases(context: dict[str, Any]) -> dict[str, Any]:
    if not context:
        return context
    try:
        maps = persona_intent_maps()
    except Exception:
        return context

    hydrated = dict(context)

    persona_key = str(hydrated.get("persona_preset_key") or "").strip()
    persona_label = str(hydrated.get("persona_preset_label") or "").strip()
    persona_spoken = str(hydrated.get("persona_preset_spoken") or "").strip()
    persona_voice = str(hydrated.get("persona_voice") or "").strip()
    persona_audience = str(hydrated.get("persona_audience") or "").strip()
    persona_tone = str(hydrated.get("persona_tone") or "").strip()

    preset = None
    if persona_key:
        preset = maps.persona_presets.get(persona_key)
    else:
        for alias in (persona_spoken, persona_label):
            alias_l = alias.lower()
            if alias_l:
                canonical = maps.persona_preset_aliases.get(alias_l)
                if canonical:
                    preset = maps.persona_presets.get(canonical)
                    if preset is not None:
                        persona_key = canonical
                        break
    if preset is None and (persona_voice or persona_audience or persona_tone):
        voice_l = persona_voice.lower()
        audience_l = persona_audience.lower()
        tone_l = persona_tone.lower()
        for candidate in maps.persona_presets.values():
            c_voice = (candidate.voice or "").lower()
            c_audience = (candidate.audience or "").lower()
            c_tone = (candidate.tone or "").lower()
            if c_voice and c_voice != voice_l:
                continue
            if c_audience and c_audience != audience_l:
                continue
            if c_tone and c_tone != tone_l:
                continue
            if not (c_voice or c_audience or c_tone):
                continue
            preset = candidate
            persona_key = candidate.key
            break

    if preset is not None:
        if not persona_key:
            persona_key = preset.key
        hydrated.setdefault("persona_preset_key", persona_key)
        hydrated.setdefault("persona_preset_label", preset.label or preset.key)
        hydrated.setdefault(
            "persona_preset_spoken", preset.spoken or preset.label or preset.key
        )

        if not persona_voice:
            hydrated["persona_voice"] = preset.voice or ""
        if not persona_audience:
            hydrated["persona_audience"] = preset.audience or ""
        if not persona_tone:
            hydrated["persona_tone"] = preset.tone or ""

    intent_key = str(hydrated.get("intent_preset_key") or "").strip()
    intent_label = str(hydrated.get("intent_preset_label") or "").strip()
    intent_display = str(hydrated.get("intent_display") or "").strip()
    intent_purpose = str(hydrated.get("intent_purpose") or "").strip()

    canonical_intent = ""
    if intent_key:
        canonical_intent = intent_key
    else:
        for alias in (intent_display, intent_label, intent_purpose):
            alias_l = alias.lower()
            if alias_l:
                canonical_intent = (
                    maps.intent_preset_aliases.get(alias_l)
                    or maps.intent_synonyms.get(alias_l)
                    or ""
                )
                if canonical_intent:
                    break
    if not canonical_intent and intent_purpose:
        canonical_intent = (
            maps.intent_synonyms.get(intent_purpose.lower()) or intent_purpose
        )

    intent_preset = (
        maps.intent_presets.get(canonical_intent) if canonical_intent else None
    )
    if intent_preset is not None:
        hydrated.setdefault("intent_preset_key", intent_preset.key)
        hydrated.setdefault(
            "intent_preset_label", intent_preset.label or intent_preset.key
        )
        hydrated.setdefault("intent_purpose", intent_preset.intent)
        display_value = maps.intent_display_map.get(
            intent_preset.key
        ) or maps.intent_display_map.get(intent_preset.intent)
        if display_value:
            hydrated.setdefault("intent_display", display_value)

    return hydrated


def suggestion_context(default: Optional[dict[str, str]] = None) -> dict[str, str]:
    """Return the context snapshot sent with the last suggest request."""
    ctx = getattr(GPTState, "last_suggest_context", {}) or {}
    if ctx:
        return _hydrate_context_aliases(dict(ctx))
    if default:
        return _hydrate_context_aliases(dict(default))
    return {}
