"""Coordinator for suggestion/rerun state (last suggested recipes, source keys)."""

from __future__ import annotations

from typing import Iterable, List, Dict, Optional

from .modelState import GPTState
from .axisMappings import axis_registry_tokens
from .modelHelpers import notify


def _recipe_has_directional(recipe: str) -> bool:
    """Return True when the recipe string includes a known directional token."""
    tokens = [tok.strip() for tok in recipe.replace("·", " ").split() if tok.strip()]
    directionals = axis_registry_tokens("directional")
    return any(tok in directionals for tok in tokens)


def record_suggestions(
    suggestions: Iterable[dict[str, str]], source_key: str | None
) -> None:
    """Persist the latest suggestions and source key in GPTState."""
    suggestions_list: list[dict[str, str]] = []
    for item in suggestions:
        recipe = str(item.get("recipe", "") or "").strip()
        if recipe and not _recipe_has_directional(recipe):
            notify(
                "GPT: Suggestion skipped because it has no directional lens; expected fog/fig/dig/ong/rog/bog/jog."
            )
            continue
        suggestions_list.append(dict(item))
    GPTState.last_suggested_recipes = suggestions_list
    GPTState.last_suggest_source = source_key or ""


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
    return {
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


def recipe_header_lines_from_snapshot(snapshot: dict[str, object]) -> list[str]:
    """Build axis/recipe header lines from a last_recipe_snapshot dict.

    This keeps the formatting of recipe/axis headers consistent across
    snapshot surfaces (for example, source snapshots and response
    destinations) while allowing each caller to prepend its own
    saved_at/model/source_type fields.
    """

    header_lines: list[str] = []

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
