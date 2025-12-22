from __future__ import annotations

from pathlib import Path
from typing import Dict

from talon import Module, app

from .telemetryExport import DEFAULT_OUTPUT_DIR, DEFAULT_TOP_N, snapshot_telemetry

mod = Module()


def _notify(message: str) -> None:
    try:
        app.notify(message)
    except Exception:
        pass


def export_history_telemetry(
    *, reset_gating: bool, notify_user: bool = False
) -> Dict[str, Path]:
    """Snapshot request history telemetry into ``artifacts/telemetry``.

    Parameters
    ----------
    reset_gating:
        When ``True`` the underlying snapshot will consume gating drop counters
        after writing the artefacts.
    notify_user:
        When ``True`` a best-effort notification is displayed summarising the
        outcome. Notifications swallow failures so automated callers do not
        crash when UI surfaces are unavailable (for example, unit tests).
    """

    try:
        result = snapshot_telemetry(
            output_dir=DEFAULT_OUTPUT_DIR,
            reset_gating=reset_gating,
            top_n=DEFAULT_TOP_N,
        )
    except Exception as exc:
        if notify_user:
            _notify(f"History telemetry export failed: {exc}")
        raise

    if notify_user:
        message = "History telemetry exported."
        if reset_gating:
            message = "History telemetry exported and gating counters reset."
        _notify(message)

    return result


@mod.action_class
class UserActions:
    def history_export_telemetry(reset_gating: bool = False):
        """Export request history telemetry artifacts for guardrail tooling."""

        export_history_telemetry(reset_gating=reset_gating, notify_user=True)
