from __future__ import annotations

from typing import Optional

from .modelPatternGUI import PATTERNS, PatternDomain, pattern_debug_snapshot


def pattern_debug_catalog(
    domain: Optional[PatternDomain] = None,
) -> list[dict[str, object]]:
    """Return debug snapshots for all patterns, optionally filtered by domain.

    This helper is a small coordinator-style façade for the Pattern Debug & GPT
    Action domain. Callers (GUIs, GPT actions, tests) can obtain a stable list
    of pattern debug snapshots without reimplementing iteration or filtering
    logic around ``PATTERNS``.
    """

    snapshots: list[dict[str, object]] = []
    for pattern in PATTERNS:
        if domain is not None and pattern.domain != domain:
            continue
        snapshot = pattern_debug_snapshot(pattern.name)
        if snapshot:
            snapshots.append(snapshot)
    return snapshots


def pattern_debug_view(pattern_name: str) -> dict[str, object]:
    """Return a minimal, GUI-friendly view of a pattern debug snapshot.

    This helper is a thin adapter over :func:`pattern_debug_snapshot` that
    exposes just enough structure for GUI flows to render a concise, token-based
    recipe line alongside the underlying axes state. It intentionally preserves
    the snapshot's axes shape so existing tests can continue to characterise
    that behaviour.
    """

    snapshot = pattern_debug_snapshot(pattern_name)
    if not snapshot:
        return {}

    name = str(snapshot.get("name") or pattern_name)
    static_prompt = str(snapshot.get("static_prompt") or "")
    axes = snapshot.get("axes", {}) or {}
    completeness = str(axes.get("completeness") or "")
    scope_value = axes.get("scope") or []
    method_value = axes.get("method") or []
    style_value = axes.get("style") or []
    directional = str(axes.get("directional") or "")

    def _as_tokens(value) -> list[str]:
        if isinstance(value, list):
            return [str(v) for v in value if v]
        if isinstance(value, str) and value.strip():
            return value.strip().split()
        return []

    scope_tokens = _as_tokens(scope_value)
    method_tokens = _as_tokens(method_value)
    style_tokens = _as_tokens(style_value)

    parts: list[str] = []
    if static_prompt:
        parts.append(static_prompt)
    for value in (
        completeness,
        " ".join(scope_tokens),
        " ".join(method_tokens),
        " ".join(style_tokens),
    ):
        if value:
            parts.append(value)
    if directional:
        parts.append(directional)
    recipe_line = " · ".join(parts) or str(snapshot.get("recipe") or "")

    return {
        "name": name,
        "recipe_line": recipe_line,
        "axes": axes,
        "last_axes": snapshot.get("last_axes") or {},
    }
