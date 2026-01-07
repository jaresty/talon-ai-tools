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
    actions_obj,
    exclude: Iterable[str] | None = None,
    extra: Iterable[str] | None = None,
    *,
    passive: bool = False,
) -> None:
    """Close a standard set of overlays if present on actions_obj, plus any extras."""
    if actions_obj is None:
        return

    if not passive:
        try:
            from .requestGating import request_is_in_flight

            if request_is_in_flight():
                passive = True
        except Exception:
            pass

    suppress_token = None
    if passive:
        try:
            from .modelState import GPTState  # local import to avoid cycles

            suppress_token = getattr(GPTState, "suppress_overlay_inflight_guard", False)
            setattr(GPTState, "suppress_overlay_inflight_guard", True)
        except Exception:
            suppress_token = None
        try:
            from .surfaceGuidance import try_begin_request as _try_begin_request

            _try_begin_request(source="overlayLifecycle.close_common_overlays")
        except Exception:
            pass

    try:
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
    finally:
        if passive:
            try:
                from .modelState import GPTState  # type: ignore

                if suppress_token is None:
                    delattr(GPTState, "suppress_overlay_inflight_guard")
                else:
                    setattr(GPTState, "suppress_overlay_inflight_guard", suppress_token)
            except Exception:
                pass
