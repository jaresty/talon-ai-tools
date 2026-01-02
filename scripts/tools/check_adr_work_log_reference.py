#!/usr/bin/env python3
"""Ensure ADR-0063 references its sibling work-log file."""

from __future__ import annotations

import sys
from pathlib import Path

ADR_PATH = Path("docs/adr/0063-go-cli-single-source-of-truth.md")
REQUIRED_TOKEN = "0063-go-cli-single-source-of-truth.work-log.md"


def main() -> int:
    if not ADR_PATH.exists():
        print(f"missing ADR document: {ADR_PATH}", file=sys.stderr)
        return 1

    text = ADR_PATH.read_text(encoding="utf-8")
    if REQUIRED_TOKEN not in text:
        print(
            f"work-log reference '{REQUIRED_TOKEN}' absent from {ADR_PATH}",
            file=sys.stderr,
        )
        return 1

    print("adr references work-log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
