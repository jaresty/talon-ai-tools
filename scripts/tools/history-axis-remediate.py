#!/usr/bin/env python3
"""Clean Concordance history entries of unsupported axis tokens."""

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
    parser.add_argument(
        "--drop-missing-directional",
        action="store_true",
        help="Drop entries that have no directional lens after remediation.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the changes that would be applied without mutating history.",
    )
    args = parser.parse_args()

    stats = requestLog.remediate_history_axes(
        drop_if_missing_directional=args.drop_missing_directional,
        dry_run=args.dry_run,
    )

    print(
        "History remediation stats: total={total} updated={updated} "
        "dropped={dropped} unchanged={unchanged}".format(**stats)
    )

    if args.dry_run:
        print("(dry-run) No changes were applied. Re-run without --dry-run to apply.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
