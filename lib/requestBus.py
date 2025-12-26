"""Request event bus to drive the request UI controller."""

from __future__ import annotations

from typing import Optional

from .requestController import RequestUIController
from .historyLifecycle import (
    RequestDropReason,
    RequestEvent,
    RequestEventKind,
    RequestState,
    lifecycle_status_for,
    transition,
    state_is_in_flight,
    state_try_start_request,
)

try:
    from .modelState import GPTState  # type: ignore
except Exception:  # pragma: no cover - import may fail in tests without Talon
    GPTState = None  # type: ignore[assignment]


_controller: Optional[RequestUIController] = None
_counter: int = 0
_last_state: RequestState = RequestState()


def set_controller(controller: Optional[RequestUIController]) -> None:
    """Register the controller that should receive request events."""
    global _controller
    _controller = controller
    if controller is None:
        # Reset retained state when detaching a controller to avoid leaking ids/state.
        global _last_state
        _last_state = RequestState()


def _set_last_request_id(request_id: str) -> None:
    """Best-effort: record the last request id for downstream consumers."""
    if not request_id or GPTState is None:
        return
    try:
        GPTState.last_request_id = request_id
    except Exception:
        pass


def _clear_last_request_id() -> None:
    """Best-effort: clear the last request id."""
    if GPTState is None:
        return
    try:
        GPTState.last_request_id = ""
    except Exception:
        pass


def next_request_id() -> str:
    global _counter
    _counter += 1
    return f"req-{_counter}"


def _handle(event: RequestEvent) -> RequestState:
    global _last_state
    if _controller is None:
        _last_state = transition(_last_state, event)
        return _last_state
    try:
        return _controller.handle(event)
    except Exception:
        return _controller.state


def emit_reset() -> RequestState:
    _clear_last_request_id()
    return _handle(RequestEvent(RequestEventKind.RESET))


def emit_begin_send(request_id: Optional[str] = None) -> str:
    rid = request_id or next_request_id()
    _set_last_request_id(rid)
    _handle(RequestEvent(RequestEventKind.BEGIN_SEND, request_id=rid))
    return rid


def emit_begin_stream(request_id: Optional[str] = None) -> str:
    rid = request_id or next_request_id()
    _set_last_request_id(rid)
    _handle(RequestEvent(RequestEventKind.BEGIN_STREAM, request_id=rid))
    return rid


def emit_retry(request_id: Optional[str] = None) -> RequestState:
    rid = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(rid or "")
    return _handle(RequestEvent(RequestEventKind.RETRY, request_id=rid))


def emit_append(chunk: str, request_id: Optional[str] = None) -> RequestState:
    rid = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(rid or "")
    return _handle(
        RequestEvent(
            RequestEventKind.APPEND,
            request_id=rid,
            payload=chunk,
        )
    )


def emit_complete(request_id: Optional[str] = None) -> RequestState:
    rid = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(rid or "")
    return _handle(RequestEvent(RequestEventKind.COMPLETE, request_id=rid))


def emit_fail(error: str = "", request_id: Optional[str] = None) -> RequestState:
    rid = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(rid or "")
    return _handle(RequestEvent(RequestEventKind.FAIL, request_id=rid, error=error))


def emit_cancel(request_id: Optional[str] = None) -> RequestState:
    rid = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(rid or "")
    return _handle(RequestEvent(RequestEventKind.CANCEL, request_id=rid))


def emit_history_saved(path: str, request_id: Optional[str] = None) -> RequestState:
    req_id = request_id or current_state().request_id or next_request_id()
    _set_last_request_id(req_id or "")
    return _handle(
        RequestEvent(
            RequestEventKind.HISTORY_SAVED,
            request_id=req_id,
            payload=path,
        )
    )


def current_state() -> RequestState:
    if _controller is None:
        return _last_state
    return _controller.state


def try_start_request() -> tuple[bool, RequestDropReason]:
    """Return whether a new request may start plus the drop reason."""

    if _controller is not None:
        try:
            return _controller.try_start_request()
        except Exception:
            pass
    state = current_state()
    try:
        return state_try_start_request(state)
    except Exception:
        return True, ""


def is_in_flight() -> bool:
    """Return True when the current request is currently in flight."""

    if _controller is not None:
        try:
            return _controller.is_in_flight()
        except Exception:
            pass
    state = current_state()
    try:
        return state_is_in_flight(state)
    except Exception:
        return False


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
    "emit_retry",
    "emit_complete",
    "emit_fail",
    "emit_cancel",
    "emit_append",
    "emit_history_saved",
    "current_state",
    "try_start_request",
    "is_in_flight",
    "current_lifecycle_state",
    "next_request_id",
]
