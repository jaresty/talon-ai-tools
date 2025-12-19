#!/usr/bin/env python3
"""Validate request history entries for directional lenses and supported axis keys."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

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
    args = parser.parse_args()

    if args.reset_gating and not (args.summary or args.summary_path):
        print(
            "history-axis-validate: --reset-gating requires --summary or --summary-path"
            " so gating telemetry is archived before being cleared.",
            file=sys.stderr,
        )
        return 1

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
                    "intent_display": "For deciding",
                },
            )
        except Exception as exc:  # pragma: no cover - defensive
            print(
                f"Failed to set up simulated persona alias entry: {exc}",
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
            f"{reason}={count}" for reason, count in sorted(gating_counts.items())
        )
        print(f"Request gating drop summary: total={gating_total}; {details}")
    else:
        print("Request gating drop summary: total=0")

    stats = requestLog.history_validation_stats()
    if args.summary or args.summary_path:
        import json

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

    return 0


if __name__ == "__main__":
    sys.exit(main())
