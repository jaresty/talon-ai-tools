"""Automatically export telemetry on a fixed interval inside Talon."""

from __future__ import annotations

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


def _export_telemetry() -> None:
    try:
        actions.user.model_export_telemetry(False)
    except Exception:
        # Talon surfaces exceptions in the log; skip bubbling failures so the
        # scheduler keeps running even if individual exports fail.
        pass


def _maybe_schedule() -> bool:
    global _handle
    minutes = settings.get("user.guardrail_telemetry_export_interval_minutes", 30)
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = 0

    if minutes <= 0:
        if _handle is not None:
            cron.cancel(_handle)
            _handle = None
        return False

    interval_spec = f"{minutes}m"
    if _handle is not None:
        cron.cancel(_handle)
    _handle = cron.interval(interval_spec, _export_telemetry)
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
