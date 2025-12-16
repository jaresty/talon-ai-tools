"""Shared overlay helpers for canvases (blocking, scroll, clamp, fractions).

This module centralises overlay behaviour so canvases can depend on a single
surface instead of duplicating helpers. It delegates to helpUI for now to
avoid behaviour drift while we migrate canvases incrementally.
"""

from __future__ import annotations

from .helpUI import clamp_scroll, apply_scroll_delta, scroll_fraction  # re-export


def set_canvas_block_mouse(canvas_obj) -> None:
    """Best-effort mouse capture across Talon runtime variants."""
    if canvas_obj is None:
        return
    for attr in ("blocks_mouse", "block_mouse"):
        if hasattr(canvas_obj, attr):
            try:
                setattr(canvas_obj, attr, True)
            except Exception:
                continue


def set_canvas_block_keyboard(canvas_obj) -> None:
    """Best-effort keyboard capture across Talon runtime variants."""
    if canvas_obj is None:
        return
    for attr in ("blocks_keyboard", "block_keyboard"):
        if hasattr(canvas_obj, attr):
            try:
                setattr(canvas_obj, attr, True)
            except Exception:
                continue


def apply_canvas_blocking(canvas_obj) -> None:
    """Apply mouse + keyboard blocking in one call."""
    if canvas_obj is None:
        return
    set_canvas_block_mouse(canvas_obj)
    set_canvas_block_keyboard(canvas_obj)


__all__ = [
    "apply_canvas_blocking",
    "set_canvas_block_mouse",
    "set_canvas_block_keyboard",
    "clamp_scroll",
    "apply_scroll_delta",
    "scroll_fraction",
]
