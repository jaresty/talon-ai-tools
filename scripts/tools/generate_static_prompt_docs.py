#!/usr/bin/env python3
"""Generate static prompt documentation from the catalog SSOT."""

from __future__ import annotations

import argparse
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

from talon_user.GPT.gpt import _build_static_prompt_docs  # type: ignore  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="tmp/static-prompt-docs.md",
        help="Output path (use - for stdout).",
    )
    args = parser.parse_args()

    content = _build_static_prompt_docs()

    if args.out in ("-", "/dev/stdout"):
        print(content)
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote static prompt docs to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
