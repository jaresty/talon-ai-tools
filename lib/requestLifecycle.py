from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


RequestStatus = Literal[
    "pending",
    "running",
    "streaming",
    "completed",
    "errored",
    "cancelled",
]


@dataclass(frozen=True)
class RequestLifecycleState:
    """Logical request lifecycle state for RequestLifecycle façade.

    This is intentionally transport-agnostic and UI-agnostic so higher-level
    orchestrators can reason about request progress (pending -> running ->
    streaming/completed/errored/cancelled) without depending on specific
    Talon events or canvas wiring.
    """

    status: RequestStatus = "pending"


def is_terminal(state: RequestLifecycleState) -> bool:
    """Return True if the lifecycle state is terminal.

    Under ADR-0037, ``errored`` and ``cancelled`` are treated as terminal
    states for lifecycle purposes: once reached, subsequent lifecycle events
    do not move the request back into a non-terminal state.
    """

    return state.status in ("errored", "cancelled")


def reduce_request_state(
    state: RequestLifecycleState, event: str
) -> RequestLifecycleState:
    """Pure reducer for request lifecycle events.

    Events are a small, high-level set:
    - "start": request has been dispatched.
    - "stream_start": first stream chunk has been observed.
    - "stream_end": stream finished normally.
    - "complete": non-streaming request completed.
    - "error": a terminal error occurred.
    - "cancel": the request was cancelled.
    - "retry": a retry was initiated after an error.

    This helper does not perform side effects; it is a building block for a
    future RequestLifecycle façade that will sit over modelHelpers and
    request* modules.
    """

    s = state.status
    # Allow "retry" to leave terminal states; otherwise treat errored/cancelled as terminal.
    if event == "retry":
        return RequestLifecycleState(status="running")
    if s in ("errored", "cancelled"):
        if event in {
            "start",
            "stream_start",
            "stream_end",
            "complete",
            "error",
            "cancel",
        }:
            return state

    if event == "start":
        if s in ("pending", "completed"):
            return RequestLifecycleState(status="running")
        return state
    if event == "stream_start":
        if s in ("running", "streaming"):
            return RequestLifecycleState(status="streaming")
        return state
    if event == "stream_end":
        if s in ("running", "streaming"):
            return RequestLifecycleState(status="completed")
        return state
    if event == "complete":
        if s in ("pending", "running", "streaming"):
            return RequestLifecycleState(status="completed")
        return state
    if event == "error":
        if s not in ("completed", "cancelled"):
            return RequestLifecycleState(status="errored")
        return state
    if event == "cancel":
        if s not in ("completed", "errored"):
            return RequestLifecycleState(status="cancelled")
        return state
    # Unknown events are ignored to keep the reducer total.
    return state
