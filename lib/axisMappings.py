"""Shared axis mapping helpers for completeness/scope/method/style/directional."""

from __future__ import annotations

from .axisConfig import (
    AXIS_KEY_TO_VALUE,
    axis_key_to_value_map,
)

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
    mapping = AXIS_VALUE_TO_KEY_MAPS.get(axis, {})
    return dict(mapping)


def axis_key_to_value_map_for(axis: str) -> dict[str, str]:
    return axis_key_to_value_map(axis)


def axis_hydrate_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Return hydrated descriptions for the given axis tokens."""
    if not tokens:
        return []
    mapping = axis_key_to_value_map(axis)
    return [mapping.get(token, token) for token in tokens if token]


def axis_hydrate_token(axis: str, token: str) -> str:
    """Hydrate a single axis token to its description (or pass through)."""
    if not token:
        return ""
    return axis_key_to_value_map(axis).get(token, token)


def axis_docs_map(axis: str) -> dict[str, str]:
    """Return the key->description map for an axis for UI/docs consumption."""
    return axis_key_to_value_map(axis)
