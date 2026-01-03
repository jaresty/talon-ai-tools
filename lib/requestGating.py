from __future__ import annotations

from typing import Optional, Tuple, cast

from .requestBus import (
    current_state,
    is_in_flight as bus_is_in_flight,
    try_start_request as bus_try_start_request,
)
from .historyLifecycle import (
    RequestDropReason,
    RequestPhase,
    RequestState,
    drop_reason_message,
    record_gating_drop,
    set_drop_reason,
    state_is_in_flight,
    state_try_start_request,
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


def _check_cli_delegation_gate(
    state: Optional[RequestState],
    source: str,
) -> Tuple[bool, RequestDropReason]:
    try:
        from . import cliDelegation as _cliDelegation
    except Exception:
        return True, cast(RequestDropReason, "")

    try:
        enabled = _cliDelegation.delegation_enabled()
    except Exception:
        enabled = True

    if enabled:
        return True, cast(RequestDropReason, "")

    failure_count = 0
    try:
        failure_count = int(_cliDelegation.failure_count())
    except Exception:
        failure_count = 0

    failure_threshold = 0
    try:
        failure_threshold = int(_cliDelegation.failure_threshold())
    except Exception:
        failure_threshold = 0

    last_reason = ""
    try:
        last_reason = _cliDelegation.last_disable_reason() or ""
    except Exception:
        last_reason = ""

    last_reason_lower = last_reason.lower()
    signature_mismatch = "signature telemetry mismatch" in last_reason_lower

    reason_code = cast(
        RequestDropReason,
        "cli_signature_mismatch" if signature_mismatch else "cli_unhealthy",
    )

    message = drop_reason_message(reason_code)
    details = []
    if not signature_mismatch and failure_count:
        if failure_threshold:
            details.append(f"failed probes={failure_count}/{failure_threshold}")
        else:
            details.append(f"failed probes={failure_count}")
    if last_reason:
        details.append(last_reason)
    if details:
        message = f"{message} ({'; '.join(details)})"

    try:
        record_gating_drop(reason_code, source=source)
    except Exception:
        pass
    try:
        set_drop_reason(reason_code, message)
    except Exception:
        pass

    _record_streaming_gating_event(state, reason_code, source=source, message=message)

    try:
        from . import cliHealth as _cliHealth
    except Exception:
        pass
    else:
        try:
            _cliHealth.probe_cli_health(source="request_gate")
        except Exception:
            pass

    return False, reason_code


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

    candidate: Optional[RequestState] = None
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

    cli_allowed, cli_reason = _check_cli_delegation_gate(candidate, source)
    if not cli_allowed:
        return False, cli_reason

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
