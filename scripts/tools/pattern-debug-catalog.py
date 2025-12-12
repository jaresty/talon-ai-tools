#!/usr/bin/env python3
"""Emit the pattern debug catalog (name/description/axes) for inspection."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from bootstrap import bootstrap  # type: ignore
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from talon_user.lib.patternDebugCoordinator import pattern_debug_catalog  # noqa: E402


def main() -> int:
    catalog = pattern_debug_catalog()
    json.dump(catalog, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
