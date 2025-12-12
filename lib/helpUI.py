"""Shared navigation/scroll helpers for help-oriented canvases."""

from __future__ import annotations


def clamp_scroll(value: float, max_scroll: float) -> float:
    """Clamp scroll offset to [0, max_scroll]."""
    max_scroll = max(0.0, float(max_scroll))
    value = float(value)
    if value < 0.0:
        return 0.0
    if value > max_scroll:
        return max_scroll
    return value


def apply_scroll_delta(value: float, delta: float, max_scroll: float) -> float:
    """Apply a delta to scroll offset and clamp within bounds."""
    return clamp_scroll(value + float(delta), max_scroll)


def scroll_fraction(value: float, max_scroll: float) -> float:
    """Return scroll fraction in [0,1] guarding divide-by-zero."""
    max_scroll = max(0.0, float(max_scroll))
    if max_scroll == 0.0:
        return 0.0
    clamped = clamp_scroll(value, max_scroll)
    return clamped / max_scroll
