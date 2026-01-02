#!/usr/bin/env python3
"""Check presence of CLI binary and shared schema assets for ADR-0063.

The command exits with code 1 when any required artefacts are missing and
prints the missing paths. Once the CLI binary and schema bundle land, this
script should return green and serve as evidence for shared command assets.
"""

from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_PATHS = (
    Path("bin/bar"),
    Path("docs/schema/command-surface.json"),
)


def main() -> int:
    missing = [path for path in REQUIRED_PATHS if not path.exists()]
    if missing:
        for path in missing:
            print(f"missing: {path}", file=sys.stderr)
        return 1
    print("all CLI assets present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
