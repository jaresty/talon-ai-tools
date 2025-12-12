"""Pattern debug coordinator facade (ADR-0046).

Provides a structured, testable snapshot of pattern metadata (name, domain,
description, recipe, axes) so GUIs and guardrails can consume a shared shape
instead of bespoke `_debug` paths.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from .axisCatalog import axis_catalog


def _default_patterns():
    """Lazy accessor to avoid hard import cycles with modelPatternGUI."""
    try:
        from .modelPatternGUI import PATTERNS  # type: ignore

        return PATTERNS
    except Exception:
        return []


def _axes_from_pattern(pattern) -> tuple[str, Dict[str, Any]]:
    """Parse a pattern's recipe/axes into a unified axes dict."""

    catalog = axis_catalog()
    axis_tokens = {
        axis: set((tokens or {}).keys())
        for axis, tokens in (catalog.get("axes") or {}).items()
    }

    recipe = getattr(pattern, "recipe", "") or ""
    tokens = [t.strip() for t in recipe.split("·") if t.strip()]
    static_prompt = tokens[0] if tokens else ""
    directional = tokens[-1] if len(tokens) > 1 else ""

    completeness = ""
    scope_tokens: List[str] = []
    method_tokens: List[str] = []
    style_tokens: List[str] = []

    for segment in tokens[1:-1]:
        for token in segment.split():
            if token in axis_tokens.get("completeness", set()):
                completeness = token
            elif token in axis_tokens.get("scope", set()):
                if token not in scope_tokens:
                    scope_tokens.append(token)
            elif token in axis_tokens.get("method", set()):
                if token not in method_tokens:
                    method_tokens.append(token)
            elif token in axis_tokens.get("style", set()):
                if token not in style_tokens:
                    style_tokens.append(token)

    axes_attr = getattr(pattern, "axes", {}) or {}

    def _list(value: Any) -> List[str]:
        if isinstance(value, list):
            return value
        if value is None:
            return []
        return [str(value)]

    axes: Dict[str, Any] = {
        "completeness": axes_attr.get("completeness") or completeness,
        "scope": _list(axes_attr.get("scope")) or scope_tokens,
        "method": _list(axes_attr.get("method")) or method_tokens,
        "style": _list(axes_attr.get("style")) or style_tokens,
        "directional": axes_attr.get("directional") or directional,
    }
    return static_prompt, axes


def pattern_debug_view(
    pattern_name: str, patterns=None
) -> Dict[str, Any]:
    """Return a single pattern debug view including axes/recipe."""

    patterns = patterns if patterns is not None else _default_patterns()
    for pat in patterns:
        if str(getattr(pat, "name", "")).lower() != str(pattern_name).lower():
            continue

        static_prompt, axes = _axes_from_pattern(pat)
        view: Dict[str, Any] = {
            "name": getattr(pat, "name", pattern_name),
            "description": getattr(pat, "description", ""),
            "domain": getattr(pat, "domain", None),
            "recipe_line": getattr(pat, "recipe", ""),
            "axes": axes,
            "static_prompt": static_prompt,
        }
        try:
            from .modelState import GPTState  # type: ignore

            last_axes = getattr(GPTState, "last_axes", None)
            if isinstance(last_axes, dict):
                view["last_axes"] = last_axes
        except Exception:
            pass
        return view
    return {}


def pattern_debug_snapshot(
    pattern_name: str, patterns=None
) -> Dict[str, Any]:
    """Return a structured snapshot for a named pattern."""

    return pattern_debug_view(pattern_name, patterns=patterns)


def pattern_debug_catalog(
    patterns=None, domain: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Return debug views for all patterns, optionally filtered by domain."""

    patterns = patterns if patterns is not None else _default_patterns()
    views: List[Dict[str, Any]] = []
    for pat in patterns:
        view = pattern_debug_view(getattr(pat, "name", ""), patterns=patterns)
        if not view:
            continue
        if domain is not None and view.get("domain") != domain:
            continue
        views.append(view)
    return views
