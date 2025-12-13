"""Shared axis mapping helpers for completeness/scope/method/form/channel/directional."""

from __future__ import annotations

from .axisConfig import AXIS_KEY_TO_VALUE, axis_key_to_value_map


def _ensure_not_style_axis(axis: str) -> None:
    """Guardrail: the legacy style axis is removed post form/channel split."""
    if axis.strip().lower() == "style":
        raise ValueError("style axis is removed; use form/channel instead.")

# Back-compat aliases for callers expecting module-level maps.
AXIS_KEY_TO_VALUE_MAPS = AXIS_KEY_TO_VALUE
AXIS_VALUE_TO_KEY_MAPS = {
    axis: {token: token for token in mapping} for axis, mapping in AXIS_KEY_TO_VALUE.items()
}

# Store axis defaults as tokens so state remains token-based.
DEFAULT_COMPLETENESS_TOKEN = "full"


def axis_value_to_key_map_for(axis: str) -> dict[str, str]:
    # In token-only mode, the map is identity on known tokens; expose a mutable
    # copy so tests can inject additional tokens without mutating the SSOT.
    _ensure_not_style_axis(axis)
    mapping = AXIS_VALUE_TO_KEY_MAPS.get(axis, {})
    return dict(mapping)


def axis_key_to_value_map_for(axis: str) -> dict[str, str]:
    _ensure_not_style_axis(axis)
    return axis_key_to_value_map(axis)


def axis_hydrate_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Return hydrated descriptions for the given axis tokens."""
    _ensure_not_style_axis(axis)
    if not tokens:
        return []
    mapping = axis_key_to_value_map(axis)
    return [mapping.get(token, token) for token in tokens if token]


def axis_hydrate_token(axis: str, token: str) -> str:
    """Hydrate a single axis token to its description (or pass through)."""
    _ensure_not_style_axis(axis)
    if not token:
        return ""
    return axis_key_to_value_map(axis).get(token, token)


def axis_docs_map(axis: str) -> dict[str, str]:
    """Return the key->description map for an axis for UI/docs consumption."""
    _ensure_not_style_axis(axis)
    return axis_key_to_value_map(axis)


def axis_registry() -> dict[str, list[str]]:
    """Return a snapshot of axis tokens keyed by axis name."""
    return {axis: list(mapping.keys()) for axis, mapping in AXIS_KEY_TO_VALUE.items()}


def axis_registry_tokens(axis: str) -> set[str]:
    """Return the set of known tokens for a given axis."""
    _ensure_not_style_axis(axis)
    mapping = AXIS_KEY_TO_VALUE.get(axis, {})
    return set(mapping.keys())
