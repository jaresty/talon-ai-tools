"""Telemetry helpers for bootstrap warnings.

This module records bootstrap warnings with basic metadata so Talon adapters
and parity harnesses can consume them as structured telemetry rather than
parsing stderr output.
"""

from datetime import datetime, timezone
from typing import Dict, List

from .cliDelegation import disable_delegation

_TELEMETRY_EVENTS: List[Dict[str, str]] = []


def _append_event(message: str, *, source: str = "bootstrap") -> None:
    """Record a telemetry event for a bootstrap warning."""

    event = {
        "message": message,
        "source": source,
        "severity": "warning",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _TELEMETRY_EVENTS.append(event)


def record_bootstrap_warning(message: str, *, source: str = "bootstrap") -> None:
    """Record a bootstrap warning with optional source metadata."""

    _append_event(message, source=source)
    try:
        disable_delegation(message, source=source)
    except Exception:
        pass


def get_bootstrap_warning_events(*, clear: bool = False) -> List[Dict[str, str]]:
    """Return telemetry events for bootstrap warnings."""

    events = list(_TELEMETRY_EVENTS)
    if clear:
        _TELEMETRY_EVENTS.clear()
    return events


def get_bootstrap_warning_messages(*, clear: bool = False) -> List[str]:
    """Return the warning messages captured via telemetry."""

    return [event["message"] for event in get_bootstrap_warning_events(clear=clear)]


def has_bootstrap_warning_events() -> bool:
    """Return True when structured telemetry has captured any warnings."""

    return bool(_TELEMETRY_EVENTS)


def clear_bootstrap_warning_events() -> None:
    """Clear recorded telemetry events."""

    _TELEMETRY_EVENTS.clear()


from talon import Module


mod = Module()


@mod.action_class
class BootstrapTelemetryActions:
    def cli_bootstrap_warning_messages() -> List[str]:
        """Return bootstrap warning messages without clearing telemetry."""

        return get_bootstrap_warning_messages(clear=False)

    def cli_bootstrap_warning_messages_clear() -> List[str]:
        """Return bootstrap warning messages and clear telemetry."""

        return get_bootstrap_warning_messages(clear=True)


try:  # Allow tests to access telemetry via stubbed actions.user
    from talon import actions as _bootstrap_actions
except Exception:  # pragma: no cover - Talon runtime without actions module
    _bootstrap_actions = None
else:

    def _record_actions_call(name: str) -> None:
        if _bootstrap_actions is None:
            return
        try:
            actions_user_local = getattr(_bootstrap_actions, "user", None)
            calls = getattr(actions_user_local, "calls", None)
            if isinstance(calls, list):
                calls.append((name, tuple(), {}))
        except Exception:
            pass

    def _actions_cli_bootstrap_warning_messages() -> List[str]:
        _record_actions_call("cli_bootstrap_warning_messages")
        return get_bootstrap_warning_messages(clear=False)

    def _actions_cli_bootstrap_warning_messages_clear() -> List[str]:
        _record_actions_call("cli_bootstrap_warning_messages_clear")
        return get_bootstrap_warning_messages(clear=True)

    actions_user = getattr(_bootstrap_actions, "user", None)
    if actions_user is not None:
        try:
            setattr(
                actions_user,
                "cli_bootstrap_warning_messages",
                _actions_cli_bootstrap_warning_messages,
            )
            setattr(
                actions_user,
                "cli_bootstrap_warning_messages_clear",
                _actions_cli_bootstrap_warning_messages_clear,
            )
        except Exception:
            pass


__all__ = [
    "record_bootstrap_warning",
    "get_bootstrap_warning_events",
    "get_bootstrap_warning_messages",
    "has_bootstrap_warning_events",
    "clear_bootstrap_warning_events",
]
