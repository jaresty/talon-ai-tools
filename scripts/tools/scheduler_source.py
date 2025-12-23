#!/usr/bin/env python3
"""Scheduler source helper for guardrail telemetry.

Determines which artifact (telemetry export, validation summary, or Talon marker)
provides the most recent scheduler statistics and returns the normalised payload
plus a source label. Falls back to default values when all sources are empty.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

DEFAULT_SCHEDULER: Dict[str, Any] = {
    "reschedule_count": 0,
    "last_interval_minutes": None,
    "last_reason": "",
    "last_timestamp": "",
}


def _load_json(path: Optional[Path]) -> Mapping[str, Any]:
    if path is None:
        return {}
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError:
        return {}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if isinstance(data, Mapping):
        return data
    return {}


def _coerce_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        try:
            return int(stripped)
        except ValueError:
            return None
    return None


def _coerce_str(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    return ""


def _normalise_scheduler(payload: Any) -> Dict[str, Any]:
    scheduler: Dict[str, Any] = DEFAULT_SCHEDULER.copy()
    if not isinstance(payload, Mapping):
        return scheduler

    reschedule_count = _coerce_int(payload.get("reschedule_count"))
    if reschedule_count is not None:
        scheduler["reschedule_count"] = reschedule_count

    last_interval = payload.get("last_interval_minutes")
    coerced_interval = _coerce_int(last_interval)
    scheduler["last_interval_minutes"] = coerced_interval

    scheduler["last_reason"] = _coerce_str(payload.get("last_reason"))
    scheduler["last_timestamp"] = _coerce_str(payload.get("last_timestamp"))

    return scheduler


def _candidate_payload(data: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
    if not isinstance(data, Mapping):
        return None

    scheduler = data.get("scheduler")
    if isinstance(scheduler, Mapping):
        return scheduler

    telemetry = data.get("telemetry")
    if isinstance(telemetry, Mapping):
        scheduler = telemetry.get("scheduler")
        if isinstance(scheduler, Mapping):
            return scheduler

    keys = {
        "reschedule_count",
        "last_interval_minutes",
        "last_reason",
        "last_timestamp",
    }
    if keys & set(data.keys()):
        return data

    return None


def determine_scheduler_source(
    summary_path: Optional[Path],
    telemetry_path: Optional[Path],
    marker_path: Optional[Path],
) -> Tuple[Dict[str, Any], str]:
    summary_data = _load_json(summary_path)
    telemetry_data = _load_json(telemetry_path)
    marker_data = _load_json(marker_path)

    candidates = [
        ("telemetry", _candidate_payload(telemetry_data)),
        ("summary", _candidate_payload(summary_data)),
        ("marker", _candidate_payload(marker_data)),
    ]

    for label, payload in candidates:
        if payload is None:
            continue
        normalised = _normalise_scheduler(payload)
        if normalised != DEFAULT_SCHEDULER:
            return normalised, label

    return DEFAULT_SCHEDULER.copy(), "defaults"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve scheduler telemetry source")
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Path to history-validation-summary.json",
    )
    parser.add_argument(
        "--telemetry",
        type=Path,
        default=None,
        help="Path to history-validation-summary.telemetry.json",
    )
    parser.add_argument(
        "--marker",
        type=Path,
        default=None,
        help="Path to talon-export-marker.json",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    stats, source = determine_scheduler_source(
        summary_path=args.summary,
        telemetry_path=args.telemetry,
        marker_path=args.marker,
    )
    output = {"stats": stats, "source": source}
    print(json.dumps(output, separators=(", ", ": ")))


if __name__ == "__main__":
    main()
