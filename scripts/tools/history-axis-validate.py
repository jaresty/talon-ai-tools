#!/usr/bin/env python3
"""Validate request history entries for directional lenses and supported axis keys."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional, cast

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from bootstrap import bootstrap  # type: ignore
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from talon_user.lib import requestLog  # type: ignore  # noqa: E402


def _coerce_int(value: object) -> Optional[int]:
    if isinstance(value, bool):
        return int(value)
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
        except Exception:
            return None
    return None


def _normalize_streaming_summary(summary: object) -> dict[str, object]:
    if not isinstance(summary, dict):
        return {
            "counts": {},
            "counts_sorted": [],
            "sources": {},
            "sources_sorted": [],
            "last": {},
            "last_source": {},
            "total": 0,
            "status": "unknown",
        }

    summary_dict: dict[str, Any] = summary

    counts: dict[str, int] = {}
    raw_counts = summary_dict.get("counts")
    if isinstance(raw_counts, dict):
        raw_counts_dict = cast(dict[str, Any], raw_counts)
        for reason, raw_value in raw_counts_dict.items():
            count_value = _coerce_int(raw_value)
            if count_value is None or count_value < 0:
                continue
            counts[str(reason)] = count_value

    sources: dict[str, int] = {}
    raw_sources = summary_dict.get("sources")
    if isinstance(raw_sources, dict):
        raw_sources_dict = cast(dict[str, Any], raw_sources)
        for source, raw_value in raw_sources_dict.items():
            count_value = _coerce_int(raw_value)
            if count_value is None or count_value < 0:
                continue
            sources[str(source)] = count_value

    total = _coerce_int(summary_dict.get("total")) or 0
    counts_total = sum(counts.values())
    if counts_total and total < counts_total:
        total = counts_total

    sorted_items = _sorted_counts(counts)
    counts_sorted = [
        {"reason": reason, "count": count} for reason, count in sorted_items
    ]
    sorted_sources = _sorted_counts(sources)
    sources_sorted = [
        {"source": source, "count": count} for source, count in _sorted_counts(sources)
    ]

    status_raw = summary_dict.get("status")
    status_value = ""
    if isinstance(status_raw, str):
        status_value = status_raw.strip()
    if not status_value:
        status_value = "unknown"

    last_payload: dict[str, object] = {}

    raw_last = summary_dict.get("last")
    if isinstance(raw_last, dict):
        raw_last_dict = cast(dict[str, Any], raw_last)
        reason = raw_last_dict.get("reason")
        if isinstance(reason, str) and reason:
            last_payload["reason"] = reason
        reason_count = _coerce_int(raw_last_dict.get("reason_count"))
        if reason_count is None and isinstance(reason, str) and reason:
            reason_count = counts.get(reason, 0)
        if reason_count is not None:
            last_payload["reason_count"] = reason_count
        if not last_payload.get("reason") and "reason_count" not in last_payload:
            last_payload = {}

    last_source_payload: dict[str, object] = {}
    raw_last_source = summary_dict.get("last_source")
    if isinstance(raw_last_source, dict):
        raw_last_source_dict = cast(dict[str, Any], raw_last_source)
        source_name = raw_last_source_dict.get("source")
        if isinstance(source_name, str) and source_name:
            last_source_payload["source"] = source_name
        source_count = _coerce_int(raw_last_source_dict.get("count"))
        if source_count is None and isinstance(source_name, str) and source_name:
            source_count = sources.get(source_name, 0)
        if source_count is not None:
            last_source_payload["count"] = source_count
        if not last_source_payload.get("source") and "count" not in last_source_payload:
            last_source_payload = {}

    last_message_value = ""
    raw_last_message = summary_dict.get("last_message")
    if isinstance(raw_last_message, str):
        last_message_value = raw_last_message.strip()

    last_code_value = ""
    raw_last_code = summary_dict.get("last_code")
    if isinstance(raw_last_code, str):
        last_code_value = raw_last_code.strip()

    return {
        "counts": counts,
        "counts_sorted": counts_sorted,
        "sources": sources,
        "sources_sorted": sources_sorted,
        "last": last_payload,
        "last_source": last_source_payload,
        "total": total,
        "status": status_value,
        "last_message": last_message_value,
        "last_code": last_code_value,
    }


def _sorted_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def _format_streaming_summary_line(normalized: dict[str, object]) -> str:
    counts_dict = cast(dict[str, int], normalized.get("counts") or {})
    counts_text = (
        ", ".join(f"{reason}={count}" for reason, count in _sorted_counts(counts_dict))
        if counts_dict
        else "none"
    )
    sources_dict = cast(dict[str, int], normalized.get("sources") or {})
    sources_text = (
        ", ".join(f"{source}={count}" for source, count in _sorted_counts(sources_dict))
        if sources_dict
        else "none"
    )
    last_dict = cast(dict[str, Any], normalized.get("last") or {})
    if last_dict:
        last_reason = str(last_dict.get("reason") or "n/a")
        last_count = cast(int, last_dict.get("reason_count", 0))
        last_text = f"{last_reason} (count={last_count})"
    else:
        last_text = "n/a"
    last_source_dict = cast(dict[str, Any], normalized.get("last_source") or {})
    if last_source_dict:
        last_source = str(last_source_dict.get("source") or "n/a")
        last_source_count = cast(int, last_source_dict.get("count", 0))
        last_source_text = f"{last_source} (count={last_source_count})"
    else:
        last_source_text = "n/a"
    total_value = cast(int, normalized.get("total", 0))
    status_value = str(normalized.get("status") or "").strip() or "unknown"
    last_message_raw = str(normalized.get("last_message") or "").strip()
    last_message_text = last_message_raw if last_message_raw else "none"
    last_code_raw = str(normalized.get("last_code") or "").strip()
    if last_code_raw:
        last_message_text = f"{last_message_text} (code={last_code_raw})"
    return (
        "Streaming gating summary: "
        f"status={status_value}; total={total_value}; counts={counts_text}; "
        f"sources={sources_text}; last={last_text}; last_source={last_source_text}; "
        f"last_message={last_message_text}"
    )


def _format_history_summary_from_data(
    summary_path: Path, data: dict[str, Any], *, artifact_url: str = ""
) -> str:
    summary = _normalize_streaming_summary(data.get("streaming_gating_summary"))
    streaming_line = _format_streaming_summary_line(summary)
    lines = [
        "### History Guardrail Summary",
        "",
        f"- Saved `{summary_path}`",
        f"- Entries validated: {data.get('total_entries', 'unknown')}",
        f"- Gating drops recorded: {data.get('gating_drop_total', 'unknown')}",
    ]

    last_message_raw = str(data.get("gating_drop_last_message") or "").strip()
    last_message_clean = last_message_raw.replace("\n", " ").strip()
    last_code_raw = str(data.get("gating_drop_last_code") or "").strip()
    if last_message_clean:
        drop_line = f"- Last gating drop: {last_message_clean}"
    else:
        drop_line = "- Last gating drop: none"
    if last_code_raw:
        drop_line = f"{drop_line} (code={last_code_raw})"
    lines.append(drop_line)

    streaming_last_message_raw = str(summary.get("last_message") or "").strip()
    streaming_last_message_clean = streaming_last_message_raw.replace("\n", " ").strip()
    streaming_last_code_raw = str(summary.get("last_code") or "").strip()
    if streaming_last_message_clean:
        streaming_drop_line = f"- Streaming last drop: {streaming_last_message_clean}"
    else:
        streaming_drop_line = "- Streaming last drop: none"
    if streaming_last_code_raw:
        streaming_drop_line = f"{streaming_drop_line} (code={streaming_last_code_raw})"
    lines.append(streaming_drop_line)
    lines.append(f"- {streaming_line}")

    sources_summary = summary.get("sources", {})
    if isinstance(sources_summary, dict) and sources_summary:
        ordered_sources = sorted(
            ((name, count) for name, count in sources_summary.items()),
            key=lambda item: (-int(item[1]), str(item[0])),
        )
        sources_text = ", ".join(f"{name}={count}" for name, count in ordered_sources)
    else:
        sources_text = "none"
    lines.append(f"- Streaming gating sources: {sources_text}")
    if artifact_url:
        lines.append(f"- [Download artifact]({artifact_url})")
    else:
        lines.append("- Artifact link unavailable outside GitHub Actions.")
    return "\n".join(lines)


def _format_history_summary(summary_path: Path, artifact_url: str = "") -> str:
    data = json.loads(summary_path.read_text())
    return _format_history_summary_from_data(
        summary_path, data, artifact_url=artifact_url
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Emit JSON summary statistics after validation succeeds",
    )
    parser.add_argument(
        "--summary-path",
        type=Path,
        help="Write JSON summary statistics to the given path on success",
    )
    parser.add_argument(
        "--reset-gating",
        action="store_true",
        help="Clear request gating telemetry counters after reporting",
    )
    parser.add_argument(
        "--summarize-json",
        type=Path,
        help="Summarize an existing history validation JSON file and exit",
    )
    parser.add_argument(
        "--artifact-url",
        type=str,
        default="",
        help="Optional artifact URL when using --summarize-json",
    )
    parser.add_argument(
        "--summary-format",
        choices=("markdown", "streaming", "json"),
        default="markdown",
        help="Output format to use with --summarize-json (default: markdown)",
    )
    args = parser.parse_args()

    if args.summarize_json is not None:
        summary_path: Path = args.summarize_json
        if not summary_path.exists():
            print(
                f"history-axis-validate: summary file {summary_path} not found",
                file=sys.stderr,
            )
            return 1
        try:
            data = json.loads(summary_path.read_text())
        except Exception as exc:  # pragma: no cover - defensive
            print(
                f"history-axis-validate: failed to read summary: {exc}", file=sys.stderr
            )
            return 1
        normalized_streaming = _normalize_streaming_summary(
            data.get("streaming_gating_summary")
        )
        if args.summary_format == "streaming":
            summary_output = _format_streaming_summary_line(normalized_streaming)
        elif args.summary_format == "json":
            summary_output = json.dumps(
                {
                    "summary_path": str(summary_path),
                    "artifact_url": args.artifact_url or None,
                    "total_entries": data.get("total_entries"),
                    "gating_drop_total": data.get("gating_drop_total"),
                    "streaming_gating_summary": normalized_streaming,
                    "stats": data,
                },
                sort_keys=True,
            )
        else:
            summary_output = _format_history_summary_from_data(
                summary_path, data, artifact_url=args.artifact_url
            )
        print(summary_output)
        return 0

    if args.reset_gating and not (args.summary or args.summary_path):
        print(
            "history-axis-validate: --reset-gating requires --summary or --summary-path"
            " so gating telemetry is archived before being cleared.",
            file=sys.stderr,
        )
        return 1

    exit_code = 0

    if os.environ.get("HISTORY_AXIS_VALIDATE_SIMULATE_PERSONA_FAILURE"):
        try:
            requestLog.clear_history()
            from talon_user.lib.requestHistory import RequestLogEntry  # type: ignore

            entry = RequestLogEntry(
                request_id="sim-persona-missing",
                prompt="prompt",
                response="response",
                axes={"directional": ["fog"]},
                persona={"unexpected": "value"},
            )
            requestLog._history.append(entry)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Failed to set up simulated persona failure: {exc}", file=sys.stderr)
            return 1

    if os.environ.get("HISTORY_AXIS_VALIDATE_SIMULATE_PERSONA_ALIAS"):
        try:
            requestLog.clear_history()
            requestLog.append_entry(
                "sim-persona-alias",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_display": "Decide",
                },
            )
        except Exception as exc:  # pragma: no cover - defensive
            print(
                f"Failed to set up simulated persona alias entry: {exc}",
                file=sys.stderr,
            )
            return 1

    if os.environ.get("HISTORY_AXIS_VALIDATE_SIMULATE_INTENT_ALIAS_KEY"):
        try:
            requestLog.clear_history()
            requestLog.append_entry(
                "sim-intent-alias-key",
                "prompt",
                "response",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_preset_key": "for deciding",
                    "intent_display": "For deciding",
                },
            )
        except Exception as exc:  # pragma: no cover - defensive
            print(
                f"Failed to set up simulated intent alias entry: {exc}",
                file=sys.stderr,
            )
            return 1

    simulate_gating_drop = os.environ.get("HISTORY_AXIS_VALIDATE_SIMULATE_GATING_DROP")
    if simulate_gating_drop is not None:
        try:
            reason = "in_flight"
            if simulate_gating_drop == "__DEFAULT__":
                message = requestLog.drop_reason_message(reason)
            else:
                message = simulate_gating_drop
            requestLog.record_gating_drop(reason, source="history-axis-validate")
            requestLog.set_drop_reason(reason, message)
        except Exception as exc:  # pragma: no cover - defensive
            print(
                f"Failed to set up simulated gating drop: {exc}",
                file=sys.stderr,
            )
            return 1

    try:
        requestLog.validate_history_axes()
    except ValueError as exc:
        print(f"History axis validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        "History axis validation passed: all entries include directional lenses, use Concordance-recognised axes, surface persona metadata when snapshots exist, and docs/help now consume the shared AxisSnapshot façade."
    )

    gating_counts = requestLog.gating_drop_stats()
    gating_total = sum(gating_counts.values())
    if gating_total:
        details = ", ".join(
            f"{reason}={count}" for reason, count in _sorted_counts(gating_counts)
        )
        print(f"Request gating drop summary: total={gating_total}; {details}")
    else:
        print("Request gating drop summary: total=0")

    stats = requestLog.history_validation_stats()
    invalid_intent_tokens = int(stats.get("intent_invalid_tokens", 0) or 0)
    if invalid_intent_tokens:
        print(f"Intent invalid tokens detected: {invalid_intent_tokens}")
        exit_code = 1
    normalized_streaming = _normalize_streaming_summary(
        stats.get("streaming_gating_summary")
    )

    last_drop_message = str(stats.get("gating_drop_last_message") or "").strip()
    last_drop_code = str(stats.get("gating_drop_last_code") or "").strip()
    if last_drop_message:
        last_drop_line = f"Last gating drop: {last_drop_message}"
    else:
        last_drop_line = "Last gating drop: none"
    if last_drop_code:
        last_drop_line = f"{last_drop_line} (code={last_drop_code})"
    print(last_drop_line)

    streaming_last_message = str(normalized_streaming.get("last_message") or "").strip()
    streaming_last_code = str(normalized_streaming.get("last_code") or "").strip()
    if not streaming_last_message and last_drop_message:
        streaming_last_message = last_drop_message
    if not streaming_last_code and last_drop_code:
        streaming_last_code = last_drop_code
    if streaming_last_message:
        streaming_last_line = f"Streaming last drop: {streaming_last_message}"
    else:
        streaming_last_line = "Streaming last drop: none"
    if streaming_last_code:
        streaming_last_line = f"{streaming_last_line} (code={streaming_last_code})"
    print(streaming_last_line)

    print(_format_streaming_summary_line(normalized_streaming))

    if args.summary or args.summary_path:
        if args.summary:
            print(json.dumps(stats, sort_keys=True))
        if args.summary_path:
            try:
                args.summary_path.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            args.summary_path.write_text(json.dumps(stats, sort_keys=True, indent=2))

    persona_pairs = stats.get("persona_alias_pairs", {})
    intent_pairs = stats.get("intent_display_pairs", {})
    if persona_pairs:
        print("Persona alias pairs:")
        for canonical in sorted(persona_pairs):
            mapping = persona_pairs[canonical]
            for alias in sorted(mapping):
                count = mapping[alias]
                print(f"- {canonical} => {alias} ({count})")
    if intent_pairs:
        print("Intent display pairs:")
        for canonical in sorted(intent_pairs):
            mapping = intent_pairs[canonical]
            for display in sorted(mapping):
                count = mapping[display]
                print(f"- {canonical} => {display} ({count})")

    if args.reset_gating:
        requestLog.consume_gating_drop_stats()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
