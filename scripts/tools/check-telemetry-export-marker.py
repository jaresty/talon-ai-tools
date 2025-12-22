#!/usr/bin/env python3
"""Guardrail helper ensuring Talon telemetry export ran recently."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def main() -> int:
    args = parse_args()
    allow_env = args.allow_env
    if allow_env and os.environ.get(allow_env):
        return 0

    marker = args.marker
    if not marker.exists():
        print(
            "Telemetry export marker missing at"
            f" {marker}. Run `history export telemetry` inside Talon first.",
            file=sys.stderr,
        )
        return 2

    timestamp = load_timestamp(marker)
    if timestamp is None:
        print(
            "Unable to parse telemetry export marker; run `history export telemetry`"
            " inside Talon to refresh the artefacts.",
            file=sys.stderr,
        )
        return 2

    age_minutes = (datetime.now(timezone.utc) - timestamp).total_seconds() / 60
    if age_minutes > args.max_age_minutes:
        print(
            "Telemetry export marker is stale (last export"
            f" {age_minutes:.1f} minutes ago). Run `history export telemetry`"
            " inside Talon before invoking guardrails.",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
