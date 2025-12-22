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
from typing import Optional

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
    parser.set_defaults(auto_export=True)
    return parser.parse_args()


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
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
