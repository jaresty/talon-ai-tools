from __future__ import annotations

from typing import Optional, Tuple

from .requestBus import current_state
from .requestLog import record_gating_drop
from .requestState import (
    RequestDropReason,
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


def request_is_in_flight(state: Optional[RequestState] = None) -> bool:
    """Return True when a request is currently running."""

    candidate = _safe_state(state)
    if candidate is None:
        return False
    try:
        return state_is_in_flight(candidate)
    except Exception:
        return False


def try_begin_request(
    state: Optional[RequestState] = None,
) -> Tuple[bool, RequestDropReason]:
    """Return whether a new request may start plus the drop reason."""

    candidate = _safe_state(state)
    if candidate is None:
        return True, ""
    try:
        allowed, reason = state_try_start_request(candidate)
    except Exception:
        return True, ""
    if not allowed and reason:
        try:
            record_gating_drop(reason)
        except Exception:
            pass
    return allowed, reason


__all__ = ["request_is_in_flight", "try_begin_request"]
