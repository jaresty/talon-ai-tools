"""UI controller for request state transitions.

This maps pure request state transitions onto UI actions (for example,
show/hide pill overlays, confirmation chips, or response canvases). It stays
side-effect-free except for the provided callbacks, so it can be tested
without Talon imports.
"""

from __future__ import annotations

from typing import Callable, Optional

from .requestState import (
    RequestEvent,
    RequestState,
    Surface,
    transition,
)


class RequestUIController:
    """Stateful controller that applies transitions and invokes UI callbacks."""

    def __init__(
        self,
        show_pill: Optional[Callable[[], None]] = None,
        hide_pill: Optional[Callable[[], None]] = None,
        show_confirmation: Optional[Callable[[], None]] = None,
        hide_confirmation: Optional[Callable[[], None]] = None,
        show_response_canvas: Optional[Callable[[], None]] = None,
        hide_response_canvas: Optional[Callable[[], None]] = None,
        on_state_change: Optional[Callable[[RequestState], None]] = None,
    ):
        self._state = RequestState()
        self._callbacks = {
            "show_pill": show_pill,
            "hide_pill": hide_pill,
            "show_confirmation": show_confirmation,
            "hide_confirmation": hide_confirmation,
            "show_response_canvas": show_response_canvas,
            "hide_response_canvas": hide_response_canvas,
        }
        self._on_state_change = on_state_change

    @property
    def state(self) -> RequestState:
        return self._state

    def handle(self, event: RequestEvent) -> RequestState:
        """Apply an event, update state, and reconcile UI surfaces."""
        next_state = transition(self._state, event)
        if next_state is self._state:
            return self._state

        self._reconcile_surfaces(prev=self._state, nxt=next_state)
        self._state = next_state
        if self._on_state_change:
            try:
                self._on_state_change(self._state)
            except Exception:
                pass
        return self._state

    def _reconcile_surfaces(self, prev: RequestState, nxt: RequestState) -> None:
        """Close no-longer-active surfaces and open the new one."""
        if prev.active_surface != nxt.active_surface:
            self._close_surface(prev.active_surface)
            self._open_surface(nxt.active_surface)
        # When entering terminal phases, ensure transient surfaces are closed.
        if nxt.is_terminal:
            self._close_surface(Surface.PILL)
            self._close_surface(Surface.CONFIRMATION_CHIP)

    def _open_surface(self, surface: Surface) -> None:
        cb = None
        if surface is Surface.PILL:
            cb = self._callbacks.get("show_pill")
        elif surface is Surface.CONFIRMATION_CHIP:
            cb = self._callbacks.get("show_confirmation")
        elif surface is Surface.RESPONSE_CANVAS:
            cb = self._callbacks.get("show_response_canvas")
        if cb:
            try:
                cb()
            except Exception:
                pass

    def _close_surface(self, surface: Surface) -> None:
        cb = None
        if surface is Surface.PILL:
            cb = self._callbacks.get("hide_pill")
        elif surface is Surface.CONFIRMATION_CHIP:
            cb = self._callbacks.get("hide_confirmation")
        elif surface is Surface.RESPONSE_CANVAS:
            cb = self._callbacks.get("hide_response_canvas")
        if cb:
            try:
                cb()
            except Exception:
                pass


__all__ = ["RequestUIController"]
