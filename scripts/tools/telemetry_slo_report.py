#!/usr/bin/env python3
"""Report CLI telemetry SLO readiness for ADR-0063.

This helper inspects local telemetry artefacts emitted by the CLI stub.
Until the CLI records latency and availability metrics, the command exits
non-zero so loops can capture blocker evidence.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TELEMETRY_PATH = Path("var/cli-telemetry/latency.json")


def main() -> int:
    if not TELEMETRY_PATH.exists():
        print(
            f"missing telemetry artefact: {TELEMETRY_PATH} (expected latency sample)",
            file=sys.stderr,
        )
        return 1

    try:
        payload = json.loads(TELEMETRY_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"invalid telemetry payload: {exc}", file=sys.stderr)
        return 1

    for key in ("p50_ms", "p95_ms", "success_rate"):
        if key not in payload:
            print(f"telemetry missing key: {key}", file=sys.stderr)
            return 1

    print("telemetry metrics ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
