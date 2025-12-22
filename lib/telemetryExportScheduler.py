"""Automatically export telemetry on a fixed interval inside Talon."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from talon import Module, actions, app, cron, settings

mod = Module()
mod.setting(
    "guardrail_telemetry_export_interval_minutes",
    type=int,
    default=30,
    desc=(
        "Minutes between automatic telemetry exports. Set to 0 to disable the "
        "scheduled export."
    ),
)

_handle: Optional[object] = None
_initialized = False
_current_interval_minutes: Optional[int] = None
_scheduler_stats = {
    "reschedule_count": 0,
    "last_interval_minutes": None,
    "last_reason": "",
    "last_timestamp": "",
}


def _record_scheduler_event(interval_minutes: Optional[int], reason: str) -> None:
    _scheduler_stats["reschedule_count"] += 1
    _scheduler_stats["last_interval_minutes"] = interval_minutes
    _scheduler_stats["last_reason"] = reason
    _scheduler_stats["last_timestamp"] = datetime.now(timezone.utc).isoformat()


def _export_telemetry() -> None:
    try:
        actions.user.model_export_telemetry(False)
    except Exception:
        # Talon surfaces exceptions in the log; skip bubbling failures so the
        # scheduler keeps running even if individual exports fail.
        pass


def _maybe_schedule() -> bool:
    global _handle, _current_interval_minutes
    minutes = settings.get("user.guardrail_telemetry_export_interval_minutes", 30)
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = 0

    previous_interval = _current_interval_minutes

    if minutes <= 0:
        if _handle is not None:
            cron.cancel(_handle)
            _handle = None
        if previous_interval is not None:
            _record_scheduler_event(None, "disabled")
        _current_interval_minutes = None
        return False

    interval_spec = f"{minutes}m"
    reason = "enabled" if _handle is None else "updated"
    if _handle is not None:
        cron.cancel(_handle)
    _handle = cron.interval(interval_spec, _export_telemetry)
    _current_interval_minutes = minutes
    if previous_interval != minutes:
        _record_scheduler_event(minutes, reason)
    return True


def _on_app_ready() -> None:
    global _initialized
    if _initialized:
        return
    _initialized = True
    if _maybe_schedule():
        _export_telemetry()


def _on_interval_setting_change(_value: object) -> None:
    if _initialized:
        _maybe_schedule()


def get_scheduler_stats() -> dict[str, object]:
    return {
        "reschedule_count": _scheduler_stats["reschedule_count"],
        "last_interval_minutes": _scheduler_stats["last_interval_minutes"],
        "last_reason": _scheduler_stats["last_reason"],
        "last_timestamp": _scheduler_stats["last_timestamp"],
    }


def _reset_for_tests() -> None:  # pragma: no cover - used only in tests
    global _handle, _initialized, _current_interval_minutes
    if _handle is not None:
        try:
            cron.cancel(_handle)
        except Exception:
            pass
    _handle = None
    _initialized = False
    _current_interval_minutes = None
    _scheduler_stats.update(
        {
            "reschedule_count": 0,
            "last_interval_minutes": None,
            "last_reason": "",
            "last_timestamp": "",
        }
    )


if hasattr(app, "register"):
    app.register("ready", _on_app_ready)

if hasattr(settings, "register"):
    try:
        settings.register(
            "user.guardrail_telemetry_export_interval_minutes",
            _on_interval_setting_change,
        )
    except Exception:
        pass
