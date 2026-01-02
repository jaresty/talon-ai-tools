"""Telemetry snapshot helpers for Talon-side guardrails.

These helpers are designed to run inside the Talon runtime so they can access
in-memory request history, gating counters, and suggestion skip statistics.
They persist the current telemetry snapshot to JSON artefacts that downstream
CLI guardrails can consume without needing access to Talon's live state.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Tuple

from . import historyLifecycle, requestLog

try:
    from .modelState import GPTState
except Exception:  # pragma: no cover - Talon runtime unavailable

    class _FallbackGPTState:
        last_suggest_skip_counts: Dict[str, int] = {}

    GPTState = _FallbackGPTState  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "artifacts" / "telemetry"
DEFAULT_TOP_N = 5


def _coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return 0
        try:
            return int(stripped)
        except ValueError:
            return 0
    return 0


def _sorted_counts(counts: Mapping[str, int]) -> List[Tuple[str, int]]:
    return sorted(
        ((key, int(value)) for key, value in counts.items()),
        key=lambda item: (-item[1], item[0]),
    )


def _normalize_streaming_summary(summary: object) -> Dict[str, Any]:
    if not isinstance(summary, Mapping):
        return {
            "counts": {},
            "counts_sorted": [],
            "sources": {},
            "sources_sorted": [],
            "last": {},
            "last_source": {},
            "total": 0,
            "status": "unknown",
            "last_message": "",
            "last_code": "",
        }

    counts: Dict[str, int] = {}
    raw_counts = summary.get("counts")
    if isinstance(raw_counts, Mapping):
        for reason, value in raw_counts.items():
            count_value = _coerce_int(value)
            if count_value > 0:
                counts[str(reason)] = count_value

    sources: Dict[str, int] = {}
    raw_sources = summary.get("sources")
    if isinstance(raw_sources, Mapping):
        for source, value in raw_sources.items():
            count_value = _coerce_int(value)
            if count_value > 0:
                sources[str(source)] = count_value

    total = _coerce_int(summary.get("total"))
    counts_total = sum(counts.values())
    if counts_total and total < counts_total:
        total = counts_total

    counts_sorted = [
        {"reason": reason, "count": count} for reason, count in _sorted_counts(counts)
    ]
    sources_sorted = [
        {"source": source, "count": count} for source, count in _sorted_counts(sources)
    ]

    status_raw = summary.get("status")
    status_value = ""
    if isinstance(status_raw, str):
        status_value = status_raw.strip()
    if not status_value:
        status_value = "unknown"

    last_payload: Dict[str, Any] = {}
    raw_last = summary.get("last")
    if isinstance(raw_last, Mapping):
        reason = raw_last.get("reason")
        if isinstance(reason, str) and reason:
            last_payload["reason"] = reason
        reason_count = _coerce_int(raw_last.get("reason_count"))
        if not reason_count and isinstance(reason, str) and reason:
            reason_count = counts.get(reason, 0)
        if reason_count:
            last_payload["reason_count"] = reason_count
        if not last_payload:
            last_payload = {}

    last_source_payload: Dict[str, Any] = {}
    raw_last_source = summary.get("last_source")
    if isinstance(raw_last_source, Mapping):
        source_name = raw_last_source.get("source")
        if isinstance(source_name, str) and source_name:
            last_source_payload["source"] = source_name
        source_count = _coerce_int(raw_last_source.get("count"))
        if not source_count and isinstance(source_name, str) and source_name:
            source_count = sources.get(source_name, 0)
        if source_count:
            last_source_payload["count"] = source_count
        if not last_source_payload:
            last_source_payload = {}

    last_message_raw = summary.get("last_message")
    last_code_raw = summary.get("last_code")
    last_message = last_message_raw.strip() if isinstance(last_message_raw, str) else ""
    last_code = last_code_raw.strip() if isinstance(last_code_raw, str) else ""

    return {
        "counts": counts,
        "counts_sorted": counts_sorted,
        "sources": sources,
        "sources_sorted": sources_sorted,
        "last": last_payload,
        "last_source": last_source_payload,
        "total": total,
        "status": status_value,
        "last_message": last_message,
        "last_code": last_code,
    }


def _top_reasons(
    counts: Iterable[Tuple[str, int]], *, limit: int
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
    counts: Iterable[Tuple[str, int]], *, limit: int
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


def _build_telemetry_payload(
    stats: MutableMapping[str, Any],
    streaming_summary: Mapping[str, Any],
    *,
    history_path: Path,
    skip_total: int,
    skip_reasons: List[Dict[str, Any]],
    top_n: int,
    truncation_events: Iterable[Mapping[str, Any]],
) -> Dict[str, Any]:
    ordered_counts = _sorted_counts(streaming_summary.get("counts", {}))
    top_reasons, other_total = _top_reasons(ordered_counts, limit=top_n)

    ordered_sources = _sorted_counts(streaming_summary.get("sources", {}))
    top_sources, other_sources_total = _top_sources(ordered_sources, limit=top_n)

    total_entries = _coerce_int(stats.get("total_entries"))
    streaming_total = _coerce_int(streaming_summary.get("total"))
    legacy_total = _coerce_int(stats.get("gating_drop_total"))
    if streaming_total == 0:
        if legacy_total:
            streaming_total = legacy_total
        elif ordered_counts:
            streaming_total = sum(count for _, count in ordered_counts)

    status_text = streaming_summary.get("status", "unknown")
    if not isinstance(status_text, str) or not status_text.strip():
        status_text = "unknown"

    last_message = streaming_summary.get("last_message")
    last_message_text = last_message.strip() if isinstance(last_message, str) else ""
    if not last_message_text:
        last_message_text = stats.get("gating_drop_last_message", "")
        if isinstance(last_message_text, str):
            last_message_text = last_message_text.strip()
        else:
            last_message_text = ""
    if not last_message_text:
        last_message_text = "none"

    last_code = streaming_summary.get("last_code")
    last_code_text = last_code.strip() if isinstance(last_code, str) else ""
    if not last_code_text:
        legacy_code = stats.get("gating_drop_last_code", "")
        last_code_text = legacy_code.strip() if isinstance(legacy_code, str) else ""

    payload: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary_path": str(history_path),
        "total_entries": total_entries,
        "gating_drop_total": streaming_total,
        "top_gating_reasons": top_reasons,
        "top_gating_sources": top_sources,
        "streaming_status": status_text,
        "streaming_last_drop_message": last_message_text,
    }
    if last_code_text:
        payload["streaming_last_drop_code"] = last_code_text
    if other_total:
        payload["other_gating_drops"] = other_total
    if other_sources_total:
        payload["other_gating_source_drops"] = other_sources_total
    if total_entries > 0:
        payload["gating_drop_rate"] = round(streaming_total / total_entries, 4)

    payload["last_drop_message"] = (
        stats.get("gating_drop_last_message", "none") or "none"
    )
    last_drop_code = stats.get("gating_drop_last_code", "")
    if isinstance(last_drop_code, str) and last_drop_code.strip():
        payload["last_drop_code"] = last_drop_code.strip()

    payload["suggestion_skip"] = {
        "total": skip_total,
        "reasons": skip_reasons,
    }

    events_payload: List[Dict[str, Any]] = []
    for event in truncation_events:
        if isinstance(event, Mapping):
            try:
                events_payload.append({str(key): value for key, value in event.items()})
            except Exception:
                continue
    if events_payload:
        payload["truncation_events"] = events_payload

    return payload


def snapshot_telemetry(
    *,
    output_dir: Path | str | None = None,
    reset_gating: bool = False,
    top_n: int = DEFAULT_TOP_N,
) -> Dict[str, Path]:
    """Persist the current telemetry snapshot to JSON files.

    Parameters
    ----------
    output_dir:
        Directory where telemetry artefacts should be written. Defaults to
        ``artifacts/telemetry``.
    reset_gating:
        When True, request gating statistics are cleared after the snapshot.
    top_n:
        Number of gating reasons/sources to include in the telemetry payload.
    """

    if top_n < 1:
        raise ValueError("top_n must be >= 1")

    base_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    base_dir.mkdir(parents=True, exist_ok=True)

    history_stats: Dict[str, Any] = historyLifecycle.history_validation_stats()
    streaming_summary = _normalize_streaming_summary(
        history_stats.get("streaming_gating_summary")
    )
    history_stats["streaming_gating_summary"] = streaming_summary

    history_path = base_dir / "history-validation-summary.json"
    history_path.write_text(json.dumps(history_stats, sort_keys=True, indent=2))

    streaming_path = base_dir / "history-validation-summary.streaming.json"
    streaming_path.write_text(json.dumps(streaming_summary, sort_keys=True, indent=2))

    raw_skip_counts = getattr(GPTState, "last_suggest_skip_counts", {})
    skip_counts: Dict[str, int] = {}
    if isinstance(raw_skip_counts, Mapping):
        for reason, value in raw_skip_counts.items():
            count_value = _coerce_int(value)
            if count_value > 0:
                skip_counts[str(reason)] = count_value

    skip_total = sum(skip_counts.values())
    skip_reasons = [
        {"reason": reason, "count": count}
        for reason, count in _sorted_counts(skip_counts)
    ]

    skip_summary = {
        "total_skipped": skip_total,
        "counts": skip_counts,
        "reason_counts": skip_reasons,
    }
    skip_path = base_dir / "suggestion-skip-summary.json"
    skip_path.write_text(json.dumps(skip_summary, sort_keys=True, indent=2))

    truncation_events = requestLog.consume_truncation_events()

    telemetry_payload = _build_telemetry_payload(
        history_stats,
        streaming_summary,
        history_path=history_path,
        skip_total=skip_total,
        skip_reasons=skip_reasons,
        top_n=top_n,
        truncation_events=truncation_events,
    )

    scheduler_stats: Dict[str, Any] = {
        "reschedule_count": 0,
        "last_interval_minutes": None,
        "last_reason": "",
        "last_timestamp": "",
    }
    try:
        from . import telemetryExportScheduler as scheduler_module  # type: ignore
    except Exception:
        pass
    else:
        get_stats = getattr(scheduler_module, "get_scheduler_stats", None)
        if callable(get_stats):
            try:
                fetched = get_stats()
            except Exception:
                fetched = None
            if isinstance(fetched, dict):
                scheduler_stats.update(fetched)
    telemetry_payload["scheduler"] = scheduler_stats

    telemetry_path = base_dir / "history-validation-summary.telemetry.json"
    telemetry_path.write_text(json.dumps(telemetry_payload, sort_keys=True, indent=2))

    if reset_gating:
        historyLifecycle.consume_gating_drop_stats()

    return {
        "history": history_path,
        "streaming": streaming_path,
        "telemetry": telemetry_path,
        "suggestion_skip": skip_path,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where telemetry artefacts should be written (default: artifacts/telemetry)",
    )
    parser.add_argument(
        "--reset-gating",
        action="store_true",
        help="Clear gating drop counters after writing the snapshot.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Number of gating reasons/sources to include in telemetry (default: {DEFAULT_TOP_N})",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    snapshot_telemetry(
        output_dir=args.output_dir,
        reset_gating=args.reset_gating,
        top_n=args.top,
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
