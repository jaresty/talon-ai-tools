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
from talon_user.lib.historyLifecycle import axes_snapshot_from_axes  # noqa: E402
from talon_user.lib.helpDomain import (  # noqa: E402
    help_index,
    help_metadata_snapshot,
    help_metadata_summary_lines,
)

axis_snapshot_from_axes = axes_snapshot_from_axes


def _metadata_summary_lines(catalog: dict) -> list[str]:
    try:
        entries = help_index(
            [],
            patterns=[],
            presets=[],
            read_list_items=lambda _name: [],
            catalog=catalog,
        )
        snapshot = help_metadata_snapshot(entries)
    except Exception:
        return []
    return help_metadata_summary_lines(snapshot)


def _canonical_axis_tokens(
    axis: str, axis_tokens: dict[str, dict[str, str]], axis_lists: dict[str, list[str]]
) -> list[str]:
    token_candidates: list[str] = []
    token_candidates.extend(axis_lists.get(axis, []) or [])
    token_candidates.extend((axis_tokens.get(axis) or {}).keys())
    seen: set[str] = set()
    for token in token_candidates:
        snapshot = axes_snapshot_from_axes({axis: [token]})
        canonical = snapshot.get(axis, []) or []
        if canonical:
            for value in canonical:
                if value not in seen:
                    seen.add(value)
            continue
        cleaned = str(token).strip()
        if not cleaned or cleaned.lower().startswith("important:"):
            continue
        lowered = cleaned.lower()
        if lowered not in seen:
            seen.add(lowered)
    return sorted(seen)


def render_cheatsheet(catalog: dict) -> str:
    axes = catalog.get("axes", {}) or {}
    axis_lists = catalog.get("axis_list_tokens", {}) or {}
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
        ("form", "Form (`formModifier`)"),
        ("channel", "Channel (`channelModifier`)"),
        ("directional", "Direction (`directionalModifier`)"),
    ]
    for axis, heading in order:
        tokens = _canonical_axis_tokens(axis, axes, axis_lists)
        if not tokens:
            continue
        lines.append(f"- {heading}: " + ", ".join(f"`{t}`" for t in tokens))

    metadata_lines = _metadata_summary_lines(catalog)
    if metadata_lines:
        lines.extend(
            [
                "",
                "## Help metadata summary",
                "",
            ]
        )
        lines.extend(metadata_lines)

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
