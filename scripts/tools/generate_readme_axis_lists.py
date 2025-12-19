#!/usr/bin/env python3
"""Render README-style axis token lines from the catalog SSOT."""

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

from talon_user.lib.axisCatalog import axis_catalog  # type: ignore  # noqa: E402
from talon_user.lib.requestLog import axis_snapshot_from_axes  # type: ignore  # noqa: E402


def _render_axis_line(axis: str, label: str, tokens: list[str]) -> str:
    backticked = ", ".join(f"`{token}`" for token in tokens)
    return f"{label}: {backticked}"


def render_readme_axis_lines(lists_dir: Path | None = None) -> str:
    catalog = axis_catalog(lists_dir=lists_dir)
    axes = catalog.get("axes", {}) or {}
    axis_lists = catalog.get("axis_list_tokens", {}) or {}
    order = [
        ("completeness", "Completeness (`completenessModifier`)"),
        ("scope", "Scope (`scopeModifier`)"),
        ("method", "Method (`methodModifier`)"),
        ("form", "Form (`formModifier`)"),
        ("channel", "Channel (`channelModifier`)"),
        ("directional", "Directional (`directionalModifier`)"),
    ]

    canonical_axes: dict[str, list[str]] = {}
    for axis, _ in order:
        token_candidates: list[str] = []
        list_tokens = axis_lists.get(axis)
        if list_tokens:
            token_candidates.extend(list_tokens)
        axis_tokens = axes.get(axis) or {}
        token_candidates.extend(axis_tokens.keys())
        seen: set[str] = set()
        for token in token_candidates:
            snapshot = axis_snapshot_from_axes({axis: [token]})
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
        canonical_axes[axis] = sorted(seen)

    lines: list[str] = []
    for axis, label in order:
        tokens = canonical_axes.get(axis, [])
        if not tokens:
            continue
        lines.append(_render_axis_line(axis, label, tokens))
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default="tmp/readme-axis-lists.md",
        help="Output path (use - for stdout).",
    )
    parser.add_argument(
        "--lists-dir",
        type=Path,
        default=None,
        help="Optional Talon lists directory for axis list tokens (catalog-only when omitted).",
    )
    args = parser.parse_args()
    content = render_readme_axis_lines(lists_dir=args.lists_dir)
    if args.out in ("-", "/dev/stdout"):
        print(content)
        return 0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"Wrote README axis lines to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
