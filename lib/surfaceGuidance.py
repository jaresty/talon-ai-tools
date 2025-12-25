from __future__ import annotations

from typing import Callable, Optional, cast

from .dropReasonUtils import render_drop_reason
from .modelHelpers import notify
from .modelState import GPTState
from .requestGating import try_begin_request
from .historyLifecycle import last_drop_reason, set_drop_reason
from .requestState import RequestDropReason, RequestState

GuardBlockHandler = Callable[[str, str], None]
BeginRequestFn = Callable[..., tuple[bool, RequestDropReason]]
StateGetter = Callable[[], RequestState]
Notifier = Callable[[str], None]


def _resolve_state(
    state: Optional[RequestState],
    state_getter: Optional[StateGetter],
) -> Optional[RequestState]:
    if state_getter is not None:
        try:
            candidate = state_getter()
        except Exception:
            candidate = None
    else:
        candidate = state
    if candidate is not None and not isinstance(candidate, RequestState):
        return None
    return candidate


def guard_surface_request(
    *,
    surface: str,
    source: str,
    suppress_attr: Optional[str] = None,
    state: Optional[RequestState] = None,
    state_getter: Optional[StateGetter] = None,
    allow_inflight: bool = False,
    on_block: Optional[GuardBlockHandler] = None,
    begin_request_fn: Optional[BeginRequestFn] = None,
    notify_fn: Optional[Notifier] = None,
) -> bool:
    """Return True when the caller should abort due to an in-flight request."""

    if suppress_attr and getattr(GPTState, suppress_attr, False):
        return False

    gate_fn = begin_request_fn or try_begin_request
    notifier = notify_fn or notify

    resolved_state = _resolve_state(state, state_getter)
    if resolved_state is not None:
        allowed, reason = gate_fn(resolved_state, source=source)
    else:
        allowed, reason = gate_fn(source=source)

    if allowed:
        try:
            pending = last_drop_reason()
        except Exception:
            pending = ""
        if not pending:
            try:
                set_drop_reason("")
            except Exception:
                pass
        return False

    if not reason:
        return False

    if allow_inflight and reason == "in_flight":
        return False

    reason_value = cast(RequestDropReason, reason)

    try:
        message = render_drop_reason(reason_value)
    except Exception:
        message = ""

    try:
        if message:
            set_drop_reason(reason_value, message)
        else:
            set_drop_reason(reason_value)
    except Exception:
        pass

    if on_block is not None:
        try:
            on_block(reason_value, message)
        except Exception:
            pass

    if message:
        try:
            notifier(message)
        except Exception:
            pass

    return True


__all__ = ["guard_surface_request"]
