#!/usr/bin/env python3
"""Export suggestion skip counts as a telemetry-friendly JSON payload."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict


def _coerce_counts(raw: dict[str, object]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for key, value in raw.items():
        try:
            count = int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        counts[str(key)] = count
    return counts


def _load_counts(args: argparse.Namespace) -> tuple[Dict[str, int], str | None]:
    if args.counts is not None:
        data = json.loads(args.counts)
        if not isinstance(data, dict):  # pragma: no cover - sanity guard
            raise ValueError("--counts must contain a JSON object")
        return _coerce_counts(data), None

    if args.counts_json is not None:
        counts_path = Path(args.counts_json)
        data = json.loads(counts_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):  # pragma: no cover - sanity guard
            raise ValueError("--counts-json must contain a JSON object")
        return _coerce_counts(data), str(counts_path)

    from talon_user.lib.suggestionCoordinator import suggestion_skip_counts

    counts = suggestion_skip_counts()
    if not isinstance(counts, dict):  # pragma: no cover - sanity guard
        raise ValueError("suggestion_skip_counts() did not return a mapping")
    return _coerce_counts(counts), None


def _build_payload(counts: Dict[str, int], source: str | None) -> Dict[str, object]:
    payload: Dict[str, object] = {}
    payload["counts"] = dict(counts)

    total = sum(payload["counts"].values())
    payload["total_skipped"] = total
    payload["reason_counts"] = [
        {"reason": key, "count": value}
        for key, value in sorted(payload["counts"].items())
        if value > 0
    ]

    if source:
        payload["counts_source"] = source

    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--counts",
        help="JSON string containing skip counts (reason -> count)",
    )
    parser.add_argument(
        "--counts-json",
        help="Path to JSON file containing skip counts (reason -> count)",
    )
    parser.add_argument(
        "--output",
        help="Write telemetry JSON to this path instead of stdout",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output with indentation",
    )

    args = parser.parse_args(argv)

    try:
        counts, source = _load_counts(args)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = _build_payload(counts, source)
    indent = 2 if args.pretty else None
    output_text = json.dumps(payload, indent=indent)
    if args.pretty:
        output_text += "\n"

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
    else:
        sys.stdout.write(output_text)
        if args.pretty:
            sys.stdout.flush()

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
