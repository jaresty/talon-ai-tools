"""Default request UI wiring for progress toasts.

This sets up a RequestUIController with lightweight, non-interactive toasts
as a fallback when richer surfaces (pill/confirmation chip) are not yet
implemented. It keeps behaviour minimal to avoid disrupting existing flows.
"""

from __future__ import annotations

import time
from typing import Optional

from talon import actions, app

from .requestBus import set_controller
from .requestController import RequestUIController
from .requestState import RequestPhase, RequestState
from .modelState import GPTState
from .pillCanvas import show_pill, hide_pill
from .uiDispatch import run_on_ui_thread
from .responseCanvasFallback import (
    append_response_fallback,
    clear_response_fallback,
    clear_all_fallbacks,
)


def _notify(message: str) -> None:
    """Best-effort notify wrapper."""
    try:
        calls = getattr(actions.user, "calls", None)
        if isinstance(calls, list):
            calls.append(("notify", (message,), {}))
    except Exception:
        pass
    try:
        app_calls = getattr(actions.app, "calls", None)
        if isinstance(app_calls, list):
            app_calls.append(("notify", (message,), {}))
    except Exception:
        pass
    try:
        actions.user.notify(message)
        return
    except Exception:
        pass
    try:
        app.notify(message)
    except Exception:
        pass


def _prefer_canvas_progress() -> bool:
    try:
        kind = getattr(GPTState, "current_destination_kind", "") or ""
    except Exception:
        kind = ""
    return kind in ("window", "default")


def _should_show_response_canvas() -> bool:
    """Mirror the modelHelpers gating for response canvas refreshes."""
    try:
        if getattr(GPTState, "suppress_response_canvas", False):
            return False
    except Exception:
        pass
    return _prefer_canvas_progress()


def _show_pill() -> None:
    if _prefer_canvas_progress():
        # When the destination is the response window, surface progress in the
        # response canvas itself instead of a floating pill to avoid canvas
        # resource issues on background threads.
        run_on_ui_thread(lambda: actions.user.model_response_canvas_open())
        _notify("Model: sending…")
        return
    run_on_ui_thread(lambda: show_pill("Model: sending…", RequestPhase.SENDING))
    _notify("Model: sending…")


def _hide_pill() -> None:
    run_on_ui_thread(hide_pill)


def _show_confirmation() -> None:
    _notify("Model: awaiting confirmation")


def _hide_confirmation() -> None:
    return


def _show_response_canvas_hint() -> None:
    _notify("Model done. Say 'model last response' to view details.")


def _hide_help_hub() -> None:
    run_on_ui_thread(lambda: actions.user.help_hub_close())


def _on_history_save(request_id: Optional[str], path: Optional[str]) -> None:
    """Refresh the request history drawer when a save completes."""
    try:
        run_on_ui_thread(lambda: actions.user.request_history_drawer_refresh())
    except Exception:
        pass


def _on_append(request_id: Optional[str], chunk: str) -> None:
    """Refresh the response canvas incrementally when streaming chunks arrive."""
    global _LAST_APPEND_REFRESH_MS, _LAST_APPEND_REQUEST_ID
    if not chunk:
        return
    if not _should_show_response_canvas():
        return
    if request_id and request_id != _LAST_APPEND_REQUEST_ID:
        _LAST_APPEND_REFRESH_MS = None
        _LAST_APPEND_REQUEST_ID = request_id
    now_ms = time.time() * 1000.0
    if (
        _LAST_APPEND_REFRESH_MS is not None
        and (now_ms - _LAST_APPEND_REFRESH_MS) < _APPEND_REFRESH_THROTTLE_MS
    ):
        return
    _LAST_APPEND_REFRESH_MS = now_ms
    try:
        # Cache chunk text so consumers can render something even if the
        # response canvas isn’t yet backed by GPTState snapshots.
        append_response_fallback(request_id, chunk)
        run_on_ui_thread(lambda: actions.user.model_response_canvas_refresh())
    except Exception:
        pass


def _on_retry(request_id: Optional[str]) -> None:
    """Surface retry intent and keep progress visible."""
    global _LAST_APPEND_REFRESH_MS, _LAST_APPEND_REQUEST_ID
    try:
        _hide_pill()
    except Exception:
        pass
    # Clear stale streaming cache before a retry to avoid showing old chunks.
    try:
        # Clear all cached chunks so the new attempt starts clean.
        clear_all_fallbacks()
    except Exception:
        pass
    _LAST_APPEND_REFRESH_MS = None
    _LAST_APPEND_REQUEST_ID = None
    _notify("Model: retrying…")
    try:
        if _should_show_response_canvas():
            run_on_ui_thread(lambda: actions.user.model_response_canvas_open())
    except Exception:
        pass


def _on_state_change(state: RequestState) -> None:
    """Notify on terminal states so failures/cancels are visible."""
    try:
        if state.phase is RequestPhase.ERROR:
            detail = state.last_error or "unknown error"
            _notify(f"Model failed: {detail}")
        elif state.phase is RequestPhase.CANCELLED:
            _notify("Model cancel requested")
    except Exception:
        pass
    # Always clear the pill/progress toast when moving out of the happy path.
    if state.is_terminal or state.phase in (RequestPhase.IDLE, RequestPhase.ERROR, RequestPhase.CANCELLED):
        try:
            _hide_pill()
        except Exception:
            pass
    # Reset append throttle when a new send starts or after any transition that
    # ends a request (idle/terminal) so the next request isn't throttled.
    global _LAST_APPEND_REFRESH_MS, _LAST_APPEND_REQUEST_ID
    if state.phase in (
        RequestPhase.SENDING,
        RequestPhase.IDLE,
        RequestPhase.ERROR,
        RequestPhase.CANCELLED,
        RequestPhase.DONE,
        RequestPhase.STREAMING,
        RequestPhase.LISTENING,
        RequestPhase.TRANSCRIBING,
        RequestPhase.CONFIRMING,
    ):
        _LAST_APPEND_REFRESH_MS = None
        _LAST_APPEND_REQUEST_ID = None
        try:
            # Do not carry suppression flags across requests; fall back to defaults.
            GPTState.suppress_response_canvas = False
        except Exception:
            pass
    # Clear cached fallback text when a request reaches a terminal phase.
    try:
        if state.phase is RequestPhase.SENDING:
            clear_all_fallbacks()
        if state.phase in (RequestPhase.CANCELLED, RequestPhase.ERROR):
            clear_all_fallbacks()
            run_on_ui_thread(lambda: actions.user.model_response_canvas_close())
        if state.is_terminal:
            clear_response_fallback(getattr(state, "request_id", None))
        elif state.phase is RequestPhase.IDLE:
            clear_all_fallbacks()
            # Ensure any open response canvas is closed on reset/idle.
            run_on_ui_thread(lambda: actions.user.model_response_canvas_close())
    except Exception:
        pass


_controller: Optional[RequestUIController] = None
_LAST_APPEND_REFRESH_MS: Optional[float] = None
_LAST_APPEND_REQUEST_ID: Optional[str] = None
_APPEND_REFRESH_THROTTLE_MS = 150.0


def register_default_request_ui() -> RequestUIController:
    """Register a default controller that emits simple toasts."""
    global _controller
    global _LAST_APPEND_REFRESH_MS, _LAST_APPEND_REQUEST_ID
    _LAST_APPEND_REFRESH_MS = None
    _LAST_APPEND_REQUEST_ID = None
    try:
        GPTState.suppress_response_canvas = False  # reset per registration
    except Exception:
        pass
    _controller = RequestUIController(
        show_pill=_show_pill,
        hide_pill=_hide_pill,
        show_confirmation=_show_confirmation,
        hide_confirmation=_hide_confirmation,
        show_response_canvas=_show_response_canvas_hint,
        hide_help_hub=_hide_help_hub,
        on_history_save=_on_history_save,
        on_retry=_on_retry,
        on_append=_on_append,
        on_state_change=_on_state_change,
    )
    set_controller(_controller)
    return _controller


# Register on import so the bus has a controller by default.
register_default_request_ui()


__all__ = ["register_default_request_ui"]
