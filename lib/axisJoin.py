"""Shared helpers for joining axis tokens from snapshots or GPT state."""

from __future__ import annotations

from typing import Mapping, Sequence


def axis_join(
    axes_tokens: Mapping[str, object] | None, axis: str, fallback: str = ""
) -> str:
    """Return a space-joined token string for an axis, with sensible fallbacks.

    - If the axis is present as a list/tuple, join non-empty tokens with spaces.
    - If the axis is present as a string-like value, return it as-is.
    - Otherwise, return the provided fallback.
    """
    tokens = (axes_tokens or {}).get(axis)
    if isinstance(tokens, Sequence) and not isinstance(tokens, (str, bytes)):
        joined = " ".join(str(t) for t in tokens if str(t))
        return joined or fallback
    if tokens:
        return str(tokens)
    return fallback
