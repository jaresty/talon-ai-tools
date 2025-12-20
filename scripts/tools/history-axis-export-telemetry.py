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
from typing import Any, Dict, Iterable, List, Tuple

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


def _sorted_counts(summary: Dict[str, Any]) -> List[Tuple[str, int]]:
    streaming = summary.get("streaming_gating_summary")
    if not isinstance(streaming, dict):
        return []

    counts_sorted = streaming.get("counts_sorted")
    if isinstance(counts_sorted, list):
        ordered: List[Tuple[str, int]] = []
        for item in counts_sorted:
            if not isinstance(item, dict):
                continue
            reason = item.get("reason")
            count = item.get("count")
            if isinstance(reason, str) and reason:
                try:
                    ordered.append((reason, int(count)))
                except (TypeError, ValueError):
                    continue
        if ordered:
            return ordered

    counts = streaming.get("counts")
    if not isinstance(counts, dict):
        return []

    ordered_counts: List[Tuple[str, int]] = []
    for reason, value in counts.items():
        if not isinstance(reason, str) or not reason:
            continue
        try:
            ordered_counts.append((reason, int(value)))
        except (TypeError, ValueError):
            continue
    ordered_counts.sort(key=lambda item: (-item[1], item[0]))
    return ordered_counts


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


def build_payload(
    data: Dict[str, Any],
    *,
    top_n: int,
    artifact_url: str | None,
) -> Dict[str, Any]:
    streaming = data.get("streaming_gating_summary")
    if not isinstance(streaming, dict):
        streaming = {}

    ordered_counts = _sorted_counts(data)
    sum_counts = sum(count for _, count in ordered_counts)
    top_reasons, other_total = _top_reasons(ordered_counts, limit=top_n)

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
    }

    if artifact_url:
        payload["artifact_url"] = artifact_url
    if other_total:
        payload["other_gating_drops"] = other_total
    if total_entries > 0:
        payload["gating_drop_rate"] = round(streaming_total / total_entries, 4)

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
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output with indentation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.top < 1:
        raise SystemExit("--top must be >= 1")

    data = _load_summary(args.summary_path)
    payload = build_payload(
        data,
        top_n=args.top,
        artifact_url=args.artifact_url,
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
