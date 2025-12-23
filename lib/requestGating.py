from __future__ import annotations

from typing import Optional, Tuple

from .requestBus import (
    current_state,
    is_in_flight as bus_is_in_flight,
    try_start_request as bus_try_start_request,
)
from .requestLog import record_gating_drop, drop_reason_message, set_drop_reason
from .requestState import (
    RequestDropReason,
    RequestPhase,
    RequestState,
    is_in_flight as state_is_in_flight,
    try_start_request as state_try_start_request,
)


def _safe_state(state: Optional[RequestState] = None) -> Optional[RequestState]:
    """Return a usable request state for gating checks."""

    if state is not None:
        return state
    try:
        return current_state()
    except Exception:
        return None


def _record_streaming_gating_event(
    state: Optional[RequestState],
    reason: RequestDropReason,
    source: str = "",
    message: str = "",
) -> None:
    """Record a gating drop event on the active streaming session, if any."""

    if not reason:
        return
    try:
        from .modelState import GPTState
    except Exception:
        return

    session = getattr(GPTState, "last_streaming_session", None)
    if session is None or not hasattr(session, "record_gating_drop"):
        return

    try:
        session_request_id = getattr(session, "request_id", None)
    except Exception:
        session_request_id = None

    request_id = None
    phase_value = ""
    if state is not None:
        try:
            request_id = getattr(state, "request_id", None)
        except Exception:
            request_id = None
        try:
            phase_obj = getattr(state, "phase", "")
        except Exception:
            phase_obj = ""
        if isinstance(phase_obj, RequestPhase):
            phase_value = getattr(phase_obj, "value", "")
        else:
            phase_value = ""
            for choice in RequestPhase:
                if phase_obj is choice:
                    phase_value = getattr(choice, "value", "")
                    break
            if not phase_value:
                phase_value = str(phase_obj or "")

    if session_request_id and request_id and session_request_id != request_id:
        return

    message_value = str(message or "")
    if not message_value:
        try:
            message_value = drop_reason_message(reason)  # type: ignore[arg-type]
        except Exception:
            message_value = ""

    try:
        session.record_gating_drop(
            reason=reason,
            phase=phase_value,
            source=str(source or ""),
            message=message_value,
        )
    except Exception:
        pass


def request_is_in_flight(state: Optional[RequestState] = None) -> bool:
    """Return True when a request is currently running."""

    if state is None:
        try:
            return bus_is_in_flight()
        except Exception:
            candidate = _safe_state()
    else:
        candidate = _safe_state(state)

    if candidate is None:
        return False
    try:
        return state_is_in_flight(candidate)
    except Exception:
        return False


def try_begin_request(
    state: Optional[RequestState] = None,
    *,
    source: str = "",
) -> Tuple[bool, RequestDropReason]:
    """Return whether a new request may start plus the drop reason."""

    try:
        from .modelState import GPTState

        if getattr(GPTState, "suppress_overlay_inflight_guard", False):
            return True, ""
    except Exception:
        pass

    candidate: Optional[RequestState]
    if state is None:
        try:
            allowed, reason = bus_try_start_request()
        except Exception:
            candidate = _safe_state()
            if candidate is None:
                return True, ""
            try:
                allowed, reason = state_try_start_request(candidate)
            except Exception:
                return True, ""
        else:
            candidate = _safe_state()
    else:
        candidate = _safe_state(state)
        if candidate is None:
            return True, ""
        try:
            allowed, reason = state_try_start_request(candidate)
        except Exception:
            return True, ""

    if not allowed and reason:
        message_value = ""
        try:
            message_value = drop_reason_message(reason)  # type: ignore[arg-type]
        except Exception:
            message_value = ""
        try:
            record_gating_drop(reason, source=source)
        except Exception:
            pass
        try:
            if message_value:
                set_drop_reason(reason, message_value)
            else:
                set_drop_reason(reason)
        except Exception:
            pass
        _record_streaming_gating_event(
            candidate, reason, source=source, message=message_value
        )
    return allowed, reason


__all__ = ["request_is_in_flight", "try_begin_request"]
