#!/usr/bin/env python3
"""Guardrail helper ensuring Talon telemetry export ran recently."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from bootstrap import bootstrap  # type: ignore
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

DEFAULT_MARKER = Path("artifacts/telemetry/talon-export-marker.json")
DEFAULT_MAX_AGE_MINUTES = 60
ALLOW_ENV = "ALLOW_STALE_TELEMETRY"
DEFAULT_STREAK_LOG = Path("artifacts/telemetry/cli-warning-streak.json")
DEFAULT_STREAK_THRESHOLD = 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--marker",
        type=Path,
        default=DEFAULT_MARKER,
        help="Path to the Talon export marker JSON file.",
    )
    parser.add_argument(
        "--max-age-minutes",
        type=int,
        default=DEFAULT_MAX_AGE_MINUTES,
        help="Fail when the marker is older than this many minutes.",
    )
    parser.add_argument(
        "--allow-env",
        default=ALLOW_ENV,
        help="Environment variable that, when set, bypasses the freshness check.",
    )
    parser.add_argument(
        "--no-auto-export",
        dest="auto_export",
        action="store_false",
        help="Disable automatic telemetry export attempts when the marker is missing or stale.",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Wait up to --wait-seconds for the marker to refresh instead of failing immediately.",
    )
    parser.add_argument(
        "--wait-seconds",
        type=int,
        default=60,
        help="Maximum seconds to wait for telemetry export when --wait is set (default: 60).",
    )
    parser.add_argument(
        "--streak-log",
        type=Path,
        default=DEFAULT_STREAK_LOG,
        help="Path to JSON file storing consecutive warning streak metadata.",
    )
    parser.add_argument(
        "--streak-threshold",
        type=int,
        default=DEFAULT_STREAK_THRESHOLD,
        help="Number of consecutive warnings before emitting an escalation prompt.",
    )
    parser.set_defaults(auto_export=True)
    return parser.parse_args()


def _load_streak_state(path: Path) -> Dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    if isinstance(raw, dict):
        return raw
    return {}


def _write_streak_state(path: Path, state: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def _record_warning(path: Path, reason: str) -> Dict[str, Any]:
    state = _load_streak_state(path)
    previous_reason = state.get("last_reason") if isinstance(state, dict) else None
    previous_streak = state.get("streak") if isinstance(state, dict) else 0
    if not isinstance(previous_streak, int):
        previous_streak = 0
    streak = previous_streak + 1 if previous_reason == reason else 1
    command = " ".join([sys.executable, *sys.argv])
    timestamp = datetime.now(timezone.utc).isoformat()
    new_state: Dict[str, Any] = {
        "streak": streak,
        "last_reason": reason,
        "last_command": command,
        "updated_at": timestamp,
    }
    _write_streak_state(path, new_state)
    return new_state


def _reset_streak(path: Path) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    command = " ".join([sys.executable, *sys.argv])
    state: Dict[str, Any] = {
        "streak": 0,
        "last_reason": None,
        "last_command": command,
        "updated_at": timestamp,
    }
    _write_streak_state(path, state)


def _emit_streak_notice(state: Dict[str, Any], threshold: int, reason: str) -> None:
    streak_value = state.get("streak", 0)
    try:
        streak = int(streak_value)
    except (TypeError, ValueError):
        return
    if streak < threshold:
        return
    command = state.get("last_command")
    reason_value = state.get("last_reason") or reason
    print(
        f"Telemetry export warning streak: {streak} (reason: {reason_value}, threshold {threshold}).",
        file=sys.stderr,
    )
    if command:
        print(f"Last command: {command}", file=sys.stderr)


def load_timestamp(path: Path) -> datetime | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    exported_at = data.get("exported_at")
    if not isinstance(exported_at, str):
        return None
    try:
        timestamp = datetime.fromisoformat(exported_at)
    except ValueError:
        return None
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc)


def attempt_auto_export(marker: Path) -> bool:
    """Attempt to refresh the telemetry export marker via Talon helpers."""

    try:
        from talon_user.lib import telemetryExport as telemetry_module  # type: ignore
        from talon_user.lib import telemetryExportCommand as command  # type: ignore
    except Exception:
        return False

    marker_dir = marker.parent
    marker_dir.mkdir(parents=True, exist_ok=True)

    original_output_dir = getattr(telemetry_module, "DEFAULT_OUTPUT_DIR", marker_dir)
    original_command_dir = getattr(command, "DEFAULT_OUTPUT_DIR", marker_dir)
    try:
        telemetry_module.DEFAULT_OUTPUT_DIR = marker_dir  # type: ignore[assignment]
        command.DEFAULT_OUTPUT_DIR = marker_dir  # type: ignore[assignment]
        command.export_model_telemetry(reset_gating=False, notify_user=False)
    except Exception:
        return False
    finally:
        telemetry_module.DEFAULT_OUTPUT_DIR = original_output_dir  # type: ignore[assignment]
        command.DEFAULT_OUTPUT_DIR = original_command_dir  # type: ignore[assignment]

    return marker.exists()


def print_refresh_tip(marker: Path) -> None:
    print(
        "TIP: open Talon and run the `model export telemetry` command (voice or GUI).\n"
        f"After it finishes, rerun this helper so guardrails use the fresh snapshot (marker: {marker}).",
        file=sys.stderr,
    )


def _marker_status(
    marker: Path, max_age_minutes: int
) -> tuple[bool, Optional[datetime], Optional[float], bool]:
    exists = marker.exists()
    timestamp = load_timestamp(marker) if exists else None
    if timestamp is None:
        return exists, None, None, False
    age_minutes = (datetime.now(timezone.utc) - timestamp).total_seconds() / 60
    return exists, timestamp, age_minutes, age_minutes <= max_age_minutes


def _wait_for_marker(
    marker: Path, args: argparse.Namespace, reason: str
) -> tuple[bool, Optional[datetime], Optional[float], bool]:
    deadline = time.time() + max(0, args.wait_seconds)
    emitted = False
    while time.time() <= deadline:
        exists, timestamp, age_minutes, is_fresh = _marker_status(
            marker, args.max_age_minutes
        )
        if timestamp is not None and is_fresh:
            if emitted:
                print(
                    "Telemetry export marker is fresh after waiting.",
                    file=sys.stderr,
                )
            return exists, timestamp, age_minutes, True
        if not emitted:
            print(
                f"Waiting for telemetry export marker ({reason}); will retry for up to {args.wait_seconds} seconds...",
                file=sys.stderr,
            )
            emitted = True
        if args.auto_export:
            attempt_auto_export(marker)
        time.sleep(1 if deadline - time.time() > 1 else max(0, deadline - time.time()))
    return _marker_status(marker, args.max_age_minutes)


def main() -> int:
    args = parse_args()
    args.streak_threshold = max(1, args.streak_threshold)
    streak_log: Path = args.streak_log

    def record_and_notify(reason: str) -> None:
        state = _record_warning(streak_log, reason)
        _emit_streak_notice(state, args.streak_threshold, reason)

    allow_env = args.allow_env
    if allow_env and os.environ.get(allow_env):
        return 0

    marker = args.marker
    exists, timestamp, age_minutes, is_fresh = _marker_status(
        marker, args.max_age_minutes
    )

    if timestamp is None and args.auto_export:
        if attempt_auto_export(marker):
            exists, timestamp, age_minutes, is_fresh = _marker_status(
                marker, args.max_age_minutes
            )

    if timestamp is None:
        reason = "missing" if not exists else "invalid"
        if args.wait:
            exists, timestamp, age_minutes, is_fresh = _wait_for_marker(
                marker, args, reason
            )
        if timestamp is None:
            if not exists:
                print(
                    "Telemetry export marker missing at"
                    f" {marker}. Run `model export telemetry` inside Talon first.",
                    file=sys.stderr,
                )
            else:
                print(
                    "Unable to parse telemetry export marker; run `model export telemetry`"
                    " inside Talon to refresh the artefacts.",
                    file=sys.stderr,
                )
            print_refresh_tip(marker)
            record_and_notify(reason)
            return 2

    if not is_fresh:
        if args.auto_export and attempt_auto_export(marker):
            exists, timestamp, age_minutes, is_fresh = _marker_status(
                marker, args.max_age_minutes
            )
        if not is_fresh and args.wait:
            exists, timestamp, age_minutes, is_fresh = _wait_for_marker(
                marker, args, "stale"
            )
        if not is_fresh:
            stale_minutes = age_minutes if age_minutes is not None else float("inf")
            print(
                "Telemetry export marker is stale (last export"
                f" {stale_minutes:.1f} minutes ago). Run `model export telemetry`"
                " inside Talon before invoking guardrails.",
                file=sys.stderr,
            )
            print_refresh_tip(marker)
            record_and_notify("stale")
            return 2

    _reset_streak(streak_log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
