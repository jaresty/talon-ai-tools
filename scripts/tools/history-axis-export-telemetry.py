#!/usr/bin/env python3
"""Export history axis validation telemetry for Concordance dashboards.

This helper consumes the JSON summary produced by ``history-axis-validate``
and emits a small, machine-friendly payload that can be uploaded to
telemetry and dashboard pipelines. The payload focuses on the aggregate
entry counts and the top gating-drop reasons so operators can trend
Concordance guardrails without parsing richer guardrail artefacts.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

DEFAULT_TOP_N = 5


def _coerce_int(value: Any) -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def _load_summary(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - defensive guard
        raise SystemExit(f"summary file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"summary file is not valid JSON: {path}") from exc


def _scheduler_defaults() -> Dict[str, Any]:
    return {
        "reschedule_count": 0,
        "last_interval_minutes": None,
        "last_reason": "",
        "last_timestamp": "",
    }


def _normalize_scheduler(payload: object) -> Dict[str, Any]:
    defaults = _scheduler_defaults()
    if not isinstance(payload, Mapping):
        return defaults

    scheduler: Dict[str, Any] = _scheduler_defaults()

    reschedule_count = payload.get("reschedule_count")
    if isinstance(reschedule_count, (int, float)) and not isinstance(
        reschedule_count, bool
    ):
        scheduler["reschedule_count"] = int(reschedule_count)
    elif isinstance(reschedule_count, str) and reschedule_count.strip():
        try:
            scheduler["reschedule_count"] = int(reschedule_count.strip())
        except ValueError:
            pass

    last_interval = payload.get("last_interval_minutes")
    if last_interval is None:
        scheduler["last_interval_minutes"] = None
    elif isinstance(last_interval, (int, float)) and not isinstance(
        last_interval, bool
    ):
        scheduler["last_interval_minutes"] = int(last_interval)
    elif isinstance(last_interval, str) and last_interval.strip():
        try:
            scheduler["last_interval_minutes"] = int(last_interval.strip())
        except ValueError:
            scheduler["last_interval_minutes"] = None

    last_reason = payload.get("last_reason")
    if isinstance(last_reason, str):
        scheduler["last_reason"] = last_reason.strip()

    last_timestamp = payload.get("last_timestamp")
    if isinstance(last_timestamp, str):
        scheduler["last_timestamp"] = last_timestamp.strip()

    return scheduler


def _load_scheduler_stats(
    summary_path: Path, summary_data: Dict[str, Any]
) -> Dict[str, Any]:
    defaults = _scheduler_defaults()
    scheduler = _normalize_scheduler(summary_data.get("scheduler"))
    if scheduler != defaults:
        return scheduler

    marker_path = summary_path.with_name("talon-export-marker.json")
    try:
        marker_data = json.loads(marker_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        marker_data = {}
    if isinstance(marker_data, Mapping):
        scheduler_candidate = _normalize_scheduler(marker_data.get("scheduler"))
        if scheduler_candidate != defaults:
            return scheduler_candidate

    return scheduler


def _sorted_counts(summary: Dict[str, Any]) -> List[Tuple[str, int]]:
    streaming = summary.get("streaming_gating_summary")
    if not isinstance(streaming, dict):
        return []

    counts_sorted = streaming.get("counts_sorted")
    ordered: List[Tuple[str, int]] = []
    if isinstance(counts_sorted, list):
        for item in counts_sorted:
            if not isinstance(item, dict):
                continue
            reason = item.get("reason")
            count_value = _coerce_int(item.get("count"))
            if not isinstance(reason, str) or not reason:
                continue
            ordered.append((reason, count_value))
    if ordered:
        return ordered

    counts = streaming.get("counts")
    if not isinstance(counts, dict):
        return []

    for reason, value in counts.items():
        if not isinstance(reason, str) or not reason:
            continue
        count_value = _coerce_int(value)
        ordered.append((reason, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))
    return ordered


def _sorted_sources(summary: Dict[str, Any]) -> List[Tuple[str, int]]:
    streaming = summary.get("streaming_gating_summary")
    if not isinstance(streaming, dict):
        return []

    sources_sorted = streaming.get("sources_sorted")
    ordered: List[Tuple[str, int]] = []
    if isinstance(sources_sorted, list):
        for item in sources_sorted:
            if not isinstance(item, dict):
                continue
            source = item.get("source")
            count_value = _coerce_int(item.get("count"))
            if not isinstance(source, str) or not source:
                continue
            ordered.append((source, count_value))
    if ordered:
        return ordered

    sources = streaming.get("sources")
    if not isinstance(sources, dict):
        return []

    for source, value in sources.items():
        if not isinstance(source, str) or not source:
            continue
        count_value = _coerce_int(value)
        ordered.append((source, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))
    return ordered


def _top_reasons(
    counts: Iterable[Tuple[str, int]],
    *,
    limit: int,
) -> Tuple[List[Dict[str, Any]], int]:
    reasons: List[Dict[str, Any]] = []
    remaining = 0

    for index, (reason, count) in enumerate(counts):
        if count <= 0:
            continue
        if index < limit:
            reasons.append({"reason": reason, "count": count})
        else:
            remaining += count
    return reasons, remaining


def _top_sources(
    counts: Iterable[Tuple[str, int]],
    *,
    limit: int,
) -> Tuple[List[Dict[str, Any]], int]:
    sources: List[Dict[str, Any]] = []
    remaining = 0

    for index, (source, count) in enumerate(counts):
        if count <= 0:
            continue
        if index < limit:
            sources.append({"source": source, "count": count})
        else:
            remaining += count
    return sources, remaining


def _load_skip_summary(path: Path | None) -> tuple[int, List[Dict[str, Any]]]:
    if path is None:
        return 0, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return 0, []
    except json.JSONDecodeError:
        return 0, []

    total = _coerce_int(data.get("total_skipped")) or 0
    reasons_raw = data.get("reason_counts", [])
    reasons: List[Dict[str, Any]] = []
    if isinstance(reasons_raw, list):
        for item in reasons_raw:
            if not isinstance(item, dict):
                continue
            reason = item.get("reason")
            count_value = _coerce_int(item.get("count"))
            if not isinstance(reason, str) or not reason or count_value <= 0:
                continue
            reasons.append({"reason": reason, "count": count_value})
    return total, reasons


def build_payload(
    data: Dict[str, Any],
    *,
    top_n: int,
    artifact_url: str | None,
    summary_path: Path,
    skip_summary_path: Path | None,
) -> Dict[str, Any]:
    streaming = data.get("streaming_gating_summary")
    if not isinstance(streaming, dict):
        streaming = {}

    raw_last_message = data.get("gating_drop_last_message")
    last_message = ""
    if isinstance(raw_last_message, str):
        last_message = raw_last_message.strip()
    streaming_last_message_raw = (
        streaming.get("last_message") if isinstance(streaming, dict) else ""
    )
    streaming_last_message_text = ""
    if isinstance(streaming_last_message_raw, str):
        streaming_last_message_text = streaming_last_message_raw.replace(
            "\n", " "
        ).strip()
    if not last_message and streaming_last_message_text:
        last_message = streaming_last_message_text
    last_message = last_message.replace("\n", " ").strip()
    if not last_message:
        last_message = "none"

    raw_last_code = data.get("gating_drop_last_code")
    last_code = ""
    if isinstance(raw_last_code, str):
        last_code = raw_last_code.strip()
    streaming_last_code_raw = (
        streaming.get("last_code") if isinstance(streaming, dict) else ""
    )
    streaming_last_code_text = ""
    if isinstance(streaming_last_code_raw, str):
        streaming_last_code_text = streaming_last_code_raw.strip()
    if not last_code and streaming_last_code_text:
        last_code = streaming_last_code_text

    ordered_counts = _sorted_counts(data)
    sum_counts = sum(count for _, count in ordered_counts)
    top_reasons, other_total = _top_reasons(ordered_counts, limit=top_n)

    ordered_sources = _sorted_sources(data)
    top_sources, other_sources_total = _top_sources(ordered_sources, limit=top_n)

    status_raw = streaming.get("status") if isinstance(streaming, dict) else None
    status_text = ""
    if isinstance(status_raw, str):
        status_text = status_raw.strip()
    if not status_text:
        status_text = "unknown"

    streaming_total = _coerce_int(streaming.get("total"))
    legacy_total = _coerce_int(data.get("gating_drop_total"))
    if streaming_total == 0:
        if legacy_total:
            streaming_total = legacy_total
        elif sum_counts:
            streaming_total = sum_counts

    total_entries = _coerce_int(data.get("total_entries"))

    payload: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_entries": total_entries,
        "gating_drop_total": streaming_total,
        "top_gating_reasons": top_reasons,
        "top_gating_sources": top_sources,
        "streaming_status": status_text,
        "summary_path": str(summary_path),
        "last_drop_message": last_message,
    }

    payload["streaming_last_drop_message"] = (
        streaming_last_message_text if streaming_last_message_text else "none"
    )

    if streaming_last_code_text:
        payload["streaming_last_drop_code"] = streaming_last_code_text
    if last_code:
        payload["last_drop_code"] = last_code
    if artifact_url:
        payload["artifact_url"] = artifact_url
    if other_total:
        payload["other_gating_drops"] = other_total
    if other_sources_total:
        payload["other_gating_source_drops"] = other_sources_total
    if total_entries > 0:
        payload["gating_drop_rate"] = round(streaming_total / total_entries, 4)

    skip_total, skip_reasons = _load_skip_summary(skip_summary_path)
    payload["suggestion_skip"] = {
        "total": skip_total,
        "reasons": skip_reasons,
    }

    payload["scheduler"] = _load_scheduler_stats(summary_path, data)

    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "summary_path",
        type=Path,
        help="Path to history-validation-summary.json produced by history-axis-validate",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional output file. Defaults to stdout when omitted.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Number of gating reasons to include (default: {DEFAULT_TOP_N})",
    )
    parser.add_argument(
        "--artifact-url",
        type=str,
        default=None,
        help="Optional artifact URL to embed in the telemetry payload.",
    )
    parser.add_argument(
        "--skip-summary",
        type=Path,
        help="Optional path to suggestion skip summary JSON for inclusion in the payload.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output with indentation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top < 1:
        raise SystemExit("--top must be >= 1")

    summary_data = _load_summary(args.summary_path)
    skip_summary_path = args.skip_summary.resolve() if args.skip_summary else None

    payload = build_payload(
        summary_data,
        top_n=args.top,
        artifact_url=args.artifact_url,
        summary_path=args.summary_path,
        skip_summary_path=skip_summary_path,
    )

    if args.output is None:
        text = json.dumps(payload, indent=2 if args.pretty else None)
        print(text)
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2 if args.pretty else None)
        if args.pretty:
            handle.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
