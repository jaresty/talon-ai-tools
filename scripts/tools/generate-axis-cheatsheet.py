#!/usr/bin/env python3
"""Generate an axis cheat sheet from the catalog SSOT.

Default output: tmp/readme-axis-cheatsheet.md (stdout when --out=-).
"""

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

from talon_user.lib.axisCatalog import axis_catalog  # noqa: E402


def render_cheatsheet(catalog: dict) -> str:
    axes = catalog.get("axes", {}) or {}
    lines: list[str] = [
        "# Axis Cheat Sheet (catalog-generated)",
        "",
        "These tokens are generated from the axis catalog (axisConfig + Talon lists).",
        "",
    ]
    order = [
        ("completeness", "Completeness (`completenessModifier`)"),
        ("scope", "Scope (`scopeModifier`)"),
        ("method", "Method (`methodModifier`)"),
        ("style", "Style (`styleModifier`)"),
        ("directional", "Direction (`directionalModifier`)"),
    ]
    for axis, heading in order:
        tokens = list((axes.get(axis) or {}).keys())
        if not tokens:
            continue
        lines.append(f"- {heading}: " + ", ".join(f"`{t}`" for t in tokens))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="tmp/readme-axis-cheatsheet.md",
        help="Output path (use - for stdout).",
    )
    args = parser.parse_args()

    catalog = axis_catalog()
    content = render_cheatsheet(catalog)

    if args.out == "-" or args.out == "/dev/stdout":
        print(content)
        return 0

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote axis cheat sheet to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
