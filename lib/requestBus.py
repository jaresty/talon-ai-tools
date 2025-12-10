"""Request event bus to drive the request UI controller."""

from __future__ import annotations

from typing import Optional

from .requestController import RequestUIController
from .requestState import (
    RequestEvent,
    RequestEventKind,
    RequestState,
    lifecycle_status_for,
)


_controller: Optional[RequestUIController] = None
_counter: int = 0


def set_controller(controller: Optional[RequestUIController]) -> None:
    """Register the controller that should receive request events."""
    global _controller
    _controller = controller


def next_request_id() -> str:
    global _counter
    _counter += 1
    return f"req-{_counter}"


def _handle(event: RequestEvent) -> RequestState:
    if _controller is None:
        return RequestState()
    try:
        return _controller.handle(event)
    except Exception:
        return _controller.state


def emit_reset() -> RequestState:
    return _handle(RequestEvent(RequestEventKind.RESET))


def emit_begin_send(request_id: Optional[str] = None) -> str:
    rid = request_id or next_request_id()
    _handle(RequestEvent(RequestEventKind.BEGIN_SEND, request_id=rid))
    return rid


def emit_begin_stream(request_id: Optional[str] = None) -> str:
    rid = request_id or next_request_id()
    _handle(RequestEvent(RequestEventKind.BEGIN_STREAM, request_id=rid))
    return rid


def emit_complete(request_id: Optional[str] = None) -> RequestState:
    return _handle(RequestEvent(RequestEventKind.COMPLETE, request_id=request_id))


def emit_fail(error: str = "", request_id: Optional[str] = None) -> RequestState:
    return _handle(
        RequestEvent(RequestEventKind.FAIL, request_id=request_id, error=error)
    )


def emit_cancel(request_id: Optional[str] = None) -> RequestState:
    return _handle(RequestEvent(RequestEventKind.CANCEL, request_id=request_id))


def current_state() -> RequestState:
    if _controller is None:
        return RequestState()
    return _controller.state


def current_lifecycle_state():
    """Return the logical RequestLifecycle state for the current request.

    This is a thin adapter from the UI-focused ``RequestState`` exposed by the
    request bus to the transport-agnostic ``RequestLifecycleState`` façade
    defined in ``requestLifecycle`` for ADR-0037.
    """

    return lifecycle_status_for(current_state())


__all__ = [
    "set_controller",
    "emit_reset",
    "emit_begin_send",
    "emit_begin_stream",
    "emit_complete",
    "emit_fail",
    "emit_cancel",
    "current_state",
    "current_lifecycle_state",
    "next_request_id",
]
