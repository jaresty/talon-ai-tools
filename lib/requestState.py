"""Request and UI state machine scaffolding for model requests.

This module is intentionally pure/side-effect-free so it can be tested
without Talon UI primitives. Controllers can map phases to concrete
surfaces (pill, confirmation chip, response canvas) elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Literal

from .requestLifecycle import RequestLifecycleState, RequestStatus


class RequestPhase(Enum):
    IDLE = "idle"
    LISTENING = "listening"
    TRANSCRIBING = "transcribing"
    CONFIRMING = "confirming"
    SENDING = "sending"
    STREAMING = "streaming"
    DONE = "done"
    ERROR = "error"
    CANCELLED = "cancelled"


class Surface(Enum):
    NONE = "none"
    CONFIRMATION_CHIP = "confirmation_chip"
    RESPONSE_CANVAS = "response_canvas"
    PILL = "pill"


class RequestEventKind(Enum):
    RESET = "reset"
    START_LISTEN = "start_listen"
    GOT_TRANSCRIPT = "got_transcript"
    CONFIRM_SEND = "confirm_send"
    BEGIN_SEND = "begin_send"
    RETRY = "retry"
    BEGIN_STREAM = "begin_stream"
    APPEND = "append"
    COMPLETE = "complete"
    FAIL = "fail"
    CANCEL = "cancel"
    HISTORY_SAVED = "history_saved"


@dataclass(frozen=True)
class RequestEvent:
    """Event driving the state machine."""

    kind: RequestEventKind
    request_id: Optional[str] = None
    error: str = ""
    payload: Optional[Any] = None


@dataclass(frozen=True)
class RequestState:
    """Snapshot of request phase, UI hints, and cancellation intent."""

    phase: RequestPhase = RequestPhase.IDLE
    active_surface: Surface = Surface.NONE
    request_id: Optional[str] = None
    cancel_requested: bool = False
    last_error: str = ""

    @property
    def is_terminal(self) -> bool:
        return self.phase in (
            RequestPhase.DONE,
            RequestPhase.ERROR,
            RequestPhase.CANCELLED,
        )


def transition(state: RequestState, event: RequestEvent) -> RequestState:
    """Apply an event and return the next state (pure / no side effects)."""
    kind = event.kind

    if kind is RequestEventKind.RESET:
        return RequestState()

    if kind is RequestEventKind.START_LISTEN:
        return RequestState(phase=RequestPhase.LISTENING)

    if kind is RequestEventKind.GOT_TRANSCRIPT:
        return RequestState(
            phase=RequestPhase.CONFIRMING,
            active_surface=Surface.CONFIRMATION_CHIP,
        )

    if kind in (RequestEventKind.CONFIRM_SEND, RequestEventKind.BEGIN_SEND):
        return RequestState(
            phase=RequestPhase.SENDING,
            active_surface=Surface.PILL,
            request_id=event.request_id or state.request_id,
        )

    if kind in (RequestEventKind.RETRY, RequestEventKind.BEGIN_STREAM):
        return RequestState(
            phase=RequestPhase.STREAMING,
            active_surface=Surface.PILL,
            request_id=event.request_id or state.request_id,
        )

    if kind is RequestEventKind.APPEND:
        # Keep state/phase while allowing controllers to react to streaming chunks.
        return RequestState(
            phase=state.phase,
            active_surface=state.active_surface,
            request_id=state.request_id or event.request_id,
            cancel_requested=state.cancel_requested,
            last_error=state.last_error,
        )

    if kind is RequestEventKind.CANCEL:
        # Preserve the request id so controllers can correlate clean-up.
        return RequestState(
            phase=RequestPhase.CANCELLED,
            active_surface=Surface.NONE,
            request_id=state.request_id,
            cancel_requested=True,
        )

    if kind is RequestEventKind.COMPLETE:
        return RequestState(
            phase=RequestPhase.DONE,
            active_surface=Surface.RESPONSE_CANVAS,
            request_id=state.request_id,
        )

    if kind is RequestEventKind.FAIL:
        return RequestState(
            phase=RequestPhase.ERROR,
            active_surface=Surface.RESPONSE_CANVAS,
            request_id=state.request_id,
            last_error=event.error or state.last_error,
        )

    if kind is RequestEventKind.HISTORY_SAVED:
        # Do not alter phase/surfaces; controller-level hooks may react.
        return RequestState(
            phase=state.phase,
            active_surface=state.active_surface,
            request_id=state.request_id or event.request_id,
            cancel_requested=state.cancel_requested,
            last_error=state.last_error,
        )

    # Unknown events leave state unchanged.
    return state


def lifecycle_status_for(state: RequestState) -> RequestLifecycleState:
    """Map ``RequestState`` phases onto the RequestLifecycle façade.

    This provides a thin, testable bridge from the UI-focused request state
    machine to the transport/UI-agnostic ``RequestLifecycleState`` used by
    ADR-0037. No callers are wired to this yet; it is an adapter for future
    RequestLifecycle slices.
    """

    phase = state.phase
    if phase in (
        RequestPhase.IDLE,
        RequestPhase.LISTENING,
        RequestPhase.TRANSCRIBING,
        RequestPhase.CONFIRMING,
    ):
        status: RequestStatus = "pending"
    elif phase is RequestPhase.SENDING:
        status = "running"
    elif phase is RequestPhase.STREAMING:
        status = "streaming"
    elif phase is RequestPhase.DONE:
        status = "completed"
    elif phase is RequestPhase.ERROR:
        status = "errored"
    elif phase is RequestPhase.CANCELLED:
        status = "cancelled"
    else:
        status = "pending"
    return RequestLifecycleState(status=status)


def is_in_flight(state: RequestState) -> bool:
    """Return True when the request is currently in flight.

    For gating decisions, treat idle/done/error/cancelled as non in-flight so
    follow-up commands are allowed once a request reaches a terminal phase.
    """

    phase = state.phase
    return phase not in (
        RequestPhase.IDLE,
        RequestPhase.DONE,
        RequestPhase.ERROR,
        RequestPhase.CANCELLED,
    )


RequestDropReason = Literal[
    "",
    "in_flight",
    "missing_request_id",
    "missing_directional",
    "history_save_failed",
    "history_save_no_entry",
    "history_save_empty_prompt",
    "history_save_copy_failed",
    "history_save_open_action_unavailable",
    "history_save_open_exception",
    "history_save_path_unset",
    "history_save_path_not_found",
    "history_save_dir_create_failed",
    "history_save_write_failed",
    "history_save_missing_directional",
    "cli_unhealthy",
]


def try_start_request(state: RequestState) -> tuple[bool, RequestDropReason]:
    """Return whether a new request may start.

    This is a thin, testable façade over ``is_in_flight`` that callers can use
    to centralise drop reasons (for example, "in_flight") instead of duplicating
    phase checks.
    """

    if is_in_flight(state):
        return False, "in_flight"
    return True, ""


__all__ = [
    "RequestPhase",
    "Surface",
    "RequestEventKind",
    "RequestEvent",
    "RequestState",
    "transition",
    "is_in_flight",
    "try_start_request",
    "RequestDropReason",
    "lifecycle_status_for",
]
