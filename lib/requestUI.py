"""Default request UI wiring for progress toasts.

This sets up a RequestUIController with lightweight, non-interactive toasts
as a fallback when richer surfaces (pill/confirmation chip) are not yet
implemented. It keeps behaviour minimal to avoid disrupting existing flows.
"""

from __future__ import annotations

from typing import Optional

from talon import actions, app

from .requestBus import set_controller
from .requestController import RequestUIController
from .requestState import RequestPhase, RequestState
from .modelState import GPTState
from .pillCanvas import show_pill, hide_pill


def _notify(message: str) -> None:
    """Best-effort notify wrapper."""
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


def _show_pill() -> None:
    if _prefer_canvas_progress():
        # When the destination is the response window, surface progress in the
        # response canvas itself instead of a floating pill to avoid canvas
        # resource issues on background threads.
        try:
            actions.user.model_response_canvas_open()
        except Exception:
            pass
        _notify("Model: sending…")
        return
    show_pill("Model: sending…", RequestPhase.SENDING)


def _hide_pill() -> None:
    hide_pill()


def _show_confirmation() -> None:
    _notify("Model: awaiting confirmation")


def _hide_confirmation() -> None:
    return


def _show_response_canvas_hint() -> None:
    _notify("Model done. Say 'last response' to view details.")


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


_controller: Optional[RequestUIController] = None


def register_default_request_ui() -> RequestUIController:
    """Register a default controller that emits simple toasts."""
    global _controller
    _controller = RequestUIController(
        show_pill=_show_pill,
        hide_pill=_hide_pill,
        show_confirmation=_show_confirmation,
        hide_confirmation=_hide_confirmation,
        show_response_canvas=_show_response_canvas_hint,
        on_state_change=_on_state_change,
    )
    set_controller(_controller)
    return _controller


# Register on import so the bus has a controller by default.
register_default_request_ui()


__all__ = ["register_default_request_ui"]
