"""Manage CLI delegation state for Talon adapters."""

from datetime import datetime, timezone
from typing import Dict, List

from talon import Module, actions

mod = Module()

_DELEGATION_ENABLED: bool = True
_DISABLE_EVENTS: List[Dict[str, str]] = []


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _record_disable_event(reason: str, source: str) -> None:
    _DISABLE_EVENTS.append(
        {
            "reason": reason,
            "source": source,
            "timestamp": _timestamp(),
        }
    )


def disable_delegation(
    reason: str, *, source: str = "bootstrap", notify: bool = True
) -> None:
    """Disable CLI delegation and record the triggering reason."""

    global _DELEGATION_ENABLED
    _DELEGATION_ENABLED = False
    _record_disable_event(reason, source)
    if notify:
        try:
            actions.user.notify(f"CLI delegation disabled: {reason}")
        except Exception:
            pass
        try:
            handler = getattr(actions.user, "cli_delegation_disabled", None)
            if handler is not None:
                handler(reason, source)
        except Exception:
            pass


def mark_cli_ready(*, source: str = "bootstrap") -> None:
    """Mark CLI delegation as healthy and ready after bootstrap succeeds."""

    global _DELEGATION_ENABLED
    _DELEGATION_ENABLED = True
    try:
        handler = getattr(actions.user, "cli_delegation_ready", None)
        if handler is not None:
            handler(source)
    except Exception:
        pass


def delegation_enabled() -> bool:
    """Return True when CLI delegation is currently enabled."""

    return _DELEGATION_ENABLED


def disable_events() -> List[Dict[str, str]]:
    """Return recorded CLI delegation disable events."""

    return list(_DISABLE_EVENTS)


def reset_state() -> None:
    """Reset delegation state and forget recorded disable events."""

    global _DELEGATION_ENABLED
    _DELEGATION_ENABLED = True
    _DISABLE_EVENTS.clear()


@mod.action_class
class CliDelegationActions:
    def cli_delegation_disable(reason: str, source: str = "runtime") -> None:
        """Disable CLI delegation for the provided reason."""

        disable_delegation(reason, source=source)

    def cli_delegation_enable() -> None:
        """Re-enable CLI delegation."""

        mark_cli_ready(source="action")

    def cli_delegation_enabled() -> bool:
        """Return True when CLI delegation is enabled."""

        return delegation_enabled()

    def cli_delegation_disable_reasons() -> List[str]:
        """Return the recorded CLI delegation disable reasons."""

        return [event["reason"] for event in _DISABLE_EVENTS]


__all__ = [
    "disable_delegation",
    "mark_cli_ready",
    "delegation_enabled",
    "disable_events",
    "reset_state",
]
