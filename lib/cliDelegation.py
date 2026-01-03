"""Manage CLI delegation state for Talon adapters."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from talon import Module, actions

mod = Module()

_DELEGATION_ENABLED: bool = True
_DISABLE_EVENTS: List[Dict[str, str]] = []
_TELEMETRY_DIR = Path("var/cli-telemetry")
_STATE_PATH = _TELEMETRY_DIR / "delegation-state.json"
_FAILURE_THRESHOLD = 3
_FAILURE_COUNT = 0
_LAST_REASON: str | None = None


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> None:
    global _DELEGATION_ENABLED, _DISABLE_EVENTS, _FAILURE_COUNT, _LAST_REASON
    if not _STATE_PATH.exists():
        return
    try:
        payload = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    _DELEGATION_ENABLED = bool(payload.get("enabled", True))
    _DISABLE_EVENTS = list(payload.get("events", []))
    _FAILURE_COUNT = int(payload.get("failure_count", 0))
    _LAST_REASON = payload.get("reason")


_load_state()


def _persist_state(
    *,
    enabled: bool,
    reason: str | None,
    source: str | None,
    extra: Dict[str, Any] | None = None,
) -> None:
    try:
        _TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        existing: Dict[str, Any] = {}
        try:
            current = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            current = {}
        if isinstance(current, dict):
            existing = dict(current)
        payload: Dict[str, Any] = dict(existing)
        payload.update(
            {
                "enabled": enabled,
                "updated_at": _timestamp(),
                "reason": reason,
                "source": source,
                "events": list(_DISABLE_EVENTS),
                "failure_count": _FAILURE_COUNT,
                "failure_threshold": _FAILURE_THRESHOLD,
            }
        )
        if extra:
            for key, value in extra.items():
                if key in {
                    "enabled",
                    "updated_at",
                    "reason",
                    "source",
                    "events",
                    "failure_count",
                    "failure_threshold",
                }:
                    continue
                payload[key] = value
        _STATE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except Exception:
        # Persisting state is best-effort; telemetry continues in memory when this fails.
        pass


def apply_release_snapshot(snapshot: Dict[str, Any]) -> None:
    """Hydrate delegation state from a packaged release snapshot."""

    global \
        _DELEGATION_ENABLED, \
        _DISABLE_EVENTS, \
        _FAILURE_COUNT, \
        _FAILURE_THRESHOLD, \
        _LAST_REASON

    enabled = bool(snapshot.get("enabled", True))
    failure_count_raw = snapshot.get("failure_count", 0)
    try:
        failure_count = int(failure_count_raw)
    except Exception:
        failure_count = 0
    failure_count = max(0, failure_count)

    failure_threshold_raw = snapshot.get("failure_threshold", _FAILURE_THRESHOLD)
    try:
        failure_threshold = int(failure_threshold_raw)
    except Exception:
        failure_threshold = _FAILURE_THRESHOLD
    if failure_threshold <= 0:
        failure_threshold = _FAILURE_THRESHOLD

    events_raw = snapshot.get("events", [])
    events: List[Dict[str, str]] = []
    if isinstance(events_raw, list):
        for entry in events_raw:
            if isinstance(entry, dict):
                events.append(
                    {
                        "reason": str(entry.get("reason", "")),
                        "source": str(entry.get("source", "")),
                        "timestamp": str(entry.get("timestamp", "")),
                    }
                )

    reason = snapshot.get("reason")
    source = snapshot.get("source") or "snapshot"

    _DELEGATION_ENABLED = enabled
    _FAILURE_COUNT = failure_count
    _FAILURE_THRESHOLD = failure_threshold
    _DISABLE_EVENTS = events
    _LAST_REASON = reason if isinstance(reason, str) else None

    extra_fields: Dict[str, Any] = dict(snapshot)
    for key in (
        "enabled",
        "updated_at",
        "reason",
        "source",
        "events",
        "failure_count",
        "failure_threshold",
    ):
        extra_fields.pop(key, None)

    _persist_state(
        enabled=enabled,
        reason=_LAST_REASON,
        source=str(source),
        extra=extra_fields,
    )


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

    global _DELEGATION_ENABLED, _LAST_REASON
    _DELEGATION_ENABLED = False
    _LAST_REASON = reason
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
    _persist_state(enabled=False, reason=reason, source=source)


def mark_cli_ready(*, source: str = "bootstrap") -> None:
    """Mark CLI delegation as healthy and ready after bootstrap succeeds."""

    global _DELEGATION_ENABLED, _FAILURE_COUNT, _LAST_REASON
    _DELEGATION_ENABLED = True
    _FAILURE_COUNT = 0
    _LAST_REASON = None
    try:
        handler = getattr(actions.user, "cli_delegation_ready", None)
        if handler is not None:
            handler(source)
    except Exception:
        pass
    _persist_state(enabled=True, reason=None, source=source)


def delegation_enabled() -> bool:
    """Return True when CLI delegation is currently enabled."""

    return _DELEGATION_ENABLED


def disable_events() -> List[Dict[str, str]]:
    """Return recorded CLI delegation disable events."""

    return list(_DISABLE_EVENTS)


def failure_count() -> int:
    """Return the current consecutive failure count."""

    return _FAILURE_COUNT


def failure_threshold() -> int:
    """Return the failure threshold that disables delegation."""

    return _FAILURE_THRESHOLD


def last_disable_reason() -> str | None:
    """Return the last recorded disablement reason, if any."""

    return _LAST_REASON


def reset_state() -> None:
    """Reset delegation state and forget recorded disable events."""

    global _DELEGATION_ENABLED, _FAILURE_COUNT, _LAST_REASON
    _DELEGATION_ENABLED = True
    _FAILURE_COUNT = 0
    _LAST_REASON = None
    _DISABLE_EVENTS.clear()
    _persist_state(enabled=True, reason=None, source="reset")


def record_health_failure(reason: str, *, source: str = "health_probe") -> None:
    """Record a failed health probe and disable delegation after threshold."""

    global _FAILURE_COUNT, _LAST_REASON
    _FAILURE_COUNT += 1
    _LAST_REASON = reason
    if _FAILURE_COUNT >= _FAILURE_THRESHOLD:
        disable_delegation(
            f"{reason}; reached failure threshold {_FAILURE_THRESHOLD}",
            source=source,
            notify=True,
        )
    else:
        _persist_state(enabled=_DELEGATION_ENABLED, reason=reason, source=source)


def record_health_success(*, source: str = "health_probe") -> None:
    """Record a successful health probe and reset failure counters."""

    global _FAILURE_COUNT, _LAST_REASON
    _FAILURE_COUNT = 0
    _LAST_REASON = None
    mark_cli_ready(source=source)


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
    "failure_count",
    "failure_threshold",
    "last_disable_reason",
    "reset_state",
    "record_health_failure",
    "record_health_success",
    "apply_release_snapshot",
]
