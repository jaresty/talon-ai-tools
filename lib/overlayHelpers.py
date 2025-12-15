"""Shared helpers for Talon canvas overlays."""

from __future__ import annotations


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
