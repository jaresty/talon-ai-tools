"""Coordinator for suggestion/rerun state (last suggested recipes, source keys)."""

from __future__ import annotations

from typing import Iterable, List, Dict, Optional

from .modelState import GPTState


def record_suggestions(
    suggestions: Iterable[dict[str, str]], source_key: str | None
) -> None:
    """Persist the latest suggestions and source key in GPTState."""
    suggestions_list = list(suggestions)
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


def last_recipe_snapshot() -> dict[str, object]:
    """Return the last recipe/static/axis tokens in a normalised form."""
    axes_state = getattr(GPTState, "last_axes", {}) or {}

    def _axis(axis: str, fallback: str = "") -> list[str]:
        tokens = axes_state.get(axis)
        if isinstance(tokens, list) and tokens:
            return [str(t) for t in tokens if str(t)]
        return _tokens(fallback)

    recipe_str = getattr(GPTState, "last_recipe", "") or ""
    return {
        "recipe": recipe_str,
        "static_prompt": getattr(GPTState, "last_static_prompt", "") or "",
        "completeness": (
            _axis("completeness", getattr(GPTState, "last_completeness", "")) or [""]
        )[0],
        "scope_tokens": _axis("scope", getattr(GPTState, "last_scope", "")),
        "method_tokens": _axis("method", getattr(GPTState, "last_method", "")),
        "style_tokens": _axis("style", getattr(GPTState, "last_style", "")),
        "directional": getattr(GPTState, "last_directional", "") or "",
    }


def last_recap_snapshot() -> dict[str, str]:
    """Return last response/recipe/meta for recap surfaces."""
    return {
        "recipe": getattr(GPTState, "last_recipe", "") or "",
        "response": getattr(GPTState, "last_response", "") or "",
        "meta": getattr(GPTState, "last_meta", "") or "",
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
    GPTState.last_style = ""
    GPTState.last_axes = {
        "completeness": [],
        "scope": [],
        "method": [],
        "style": [],
    }


def set_last_recipe_from_selection(
    static_prompt: str,
    completeness: str,
    scope: str | list[str],
    method: str | list[str],
    style: str | list[str],
    directional: str,
) -> None:
    """Update GPTState last_* fields after running a suggestion."""
    static_token = static_prompt or ""
    completeness_token = completeness or ""
    scope_tokens = _tokens(scope)
    method_tokens = _tokens(method)
    style_tokens = _tokens(style)
    recipe_parts = [static_token] if static_token else []
    for token in (
        completeness_token,
        " ".join(scope_tokens),
        " ".join(method_tokens),
        " ".join(style_tokens),
    ):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_token
    GPTState.last_completeness = completeness_token
    GPTState.last_scope = " ".join(scope_tokens)
    GPTState.last_method = " ".join(method_tokens)
    GPTState.last_style = " ".join(style_tokens)
    GPTState.last_directional = directional or ""
    GPTState.last_axes = {
        "completeness": [completeness_token] if completeness_token else [],
        "scope": scope_tokens,
        "method": method_tokens,
        "style": style_tokens,
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
