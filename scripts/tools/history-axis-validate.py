#!/usr/bin/env python3
"""Validate request history entries for directional lenses and supported axis keys."""

from __future__ import annotations

import argparse
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
    parser.parse_args()

    try:
        requestLog.validate_history_axes()
    except ValueError as exc:
        print(f"History axis validation failed: {exc}", file=sys.stderr)
        return 1

    print(
        "History axis validation passed: all entries include directional lenses and use Concordance-recognised axes."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
