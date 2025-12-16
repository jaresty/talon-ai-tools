"""Shared overlay lifecycle helpers."""

from __future__ import annotations

from typing import Callable, Iterable, Optional, Set, Sequence
import traceback

COMMON_OVERLAY_CLOSERS: Sequence[str] = (
    "model_pattern_gui_close",
    "prompt_pattern_gui_close",
    "model_prompt_recipe_suggestions_gui_close",
    "model_help_canvas_close",
    "model_response_canvas_close",
    "confirmation_gui_close",
)


def close_overlays(closers: Iterable[Optional[Callable[[], None]]]) -> None:
    """Invoke a list of overlay close callables, ignoring exceptions."""
    for closer in closers:
        if closer is None:
            continue
        try:
            name = getattr(closer, "__name__", str(closer))
        except Exception:
            name = str(closer)
        if "model_response_canvas_close" in name:
            try:
                stack = "".join(traceback.format_stack(limit=6))
                print(f"[overlayLifecycle] closing response canvas via {name}\n{stack}")
            except Exception:
                pass
        try:
            closer()
        except Exception:
            continue


def close_common_overlays(
    actions_obj, exclude: Iterable[str] | None = None, extra: Iterable[str] | None = None
) -> None:
    """Close a standard set of overlays if present on actions_obj, plus any extras."""
    if actions_obj is None:
        return
    exclude_set: Set[str] = set(exclude or ())
    closers = []
    seen: Set[str] = set()
    for name in COMMON_OVERLAY_CLOSERS:
        if name in exclude_set or name in seen:
            continue
        seen.add(name)
        closers.append(getattr(actions_obj, name, None))
    if extra:
        for name in extra:
            if name in exclude_set or name in seen:
                continue
            seen.add(name)
            closers.append(getattr(actions_obj, name, None))
    close_overlays(closers)
