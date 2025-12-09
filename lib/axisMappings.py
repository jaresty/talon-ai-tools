"""Shared axis mapping helpers for completeness/scope/method/style/directional."""

from __future__ import annotations

import os

_AXIS_FILES: dict[str, str] = {
    "completeness": "completenessModifier.talon-list",
    "scope": "scopeModifier.talon-list",
    "method": "methodModifier.talon-list",
    "style": "styleModifier.talon-list",
    "directional": "directionalModifier.talon-list",
}


def _lists_dir() -> str:
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))


def _read_axis_value_to_key_map(filename: str) -> dict[str, str]:
    """Build a mapping from hydrated axis values back to their short keys."""
    path = os.path.join(_lists_dir(), filename)
    mapping: dict[str, str] = {}
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
                short = key.strip()
                desc = value.strip()
                mapping[short] = short
                mapping[desc] = short
                if (desc.startswith('"') and desc.endswith('"')) or (
                    desc.startswith("'") and desc.endswith("'")
                ):
                    unquoted = desc[1:-1].strip()
                    if unquoted:
                        mapping[unquoted] = short
    except FileNotFoundError:
        return {}
    return mapping


def _read_axis_key_to_value_map(filename: str) -> dict[str, str]:
    """Build a mapping from short axis keys to their hydrated descriptions."""
    path = os.path.join(_lists_dir(), filename)
    mapping: dict[str, str] = {}
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
                short = key.strip()
                desc = value.strip()
                mapping[short] = desc
    except FileNotFoundError:
        return {}
    return mapping


AXIS_VALUE_TO_KEY_MAPS: dict[str, dict[str, str]] = {
    axis: _read_axis_value_to_key_map(filename)
    for axis, filename in _AXIS_FILES.items()
}

AXIS_KEY_TO_VALUE_MAPS: dict[str, dict[str, str]] = {
    axis: _read_axis_key_to_value_map(filename)
    for axis, filename in _AXIS_FILES.items()
}

# Store axis defaults as tokens so state remains token-based.
DEFAULT_COMPLETENESS_TOKEN = "full"


def axis_value_to_key_map_for(axis: str) -> dict[str, str]:
    return AXIS_VALUE_TO_KEY_MAPS.get(axis, {})


def axis_key_to_value_map_for(axis: str) -> dict[str, str]:
    return AXIS_KEY_TO_VALUE_MAPS.get(axis, {})


def axis_hydrate_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Return hydrated descriptions for the given axis tokens."""
    if not tokens:
        return []
    mapping = axis_key_to_value_map_for(axis)
    return [mapping.get(token, token) for token in tokens if token]
