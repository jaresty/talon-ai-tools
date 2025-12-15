#!/usr/bin/env python3
"""Refresh the axis token lines in GPT/readme.md from the catalog generator."""

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

from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines  # noqa: E402


START_MARKER = "Completeness (`completenessModifier`):"
END_MARKER = "  - Additional form/channel notes:"


def refresh_readme(readme_path: Path) -> None:
    content = readme_path.read_text(encoding="utf-8").splitlines()
    try:
        start_idx = next(
            i
            for i, line in enumerate(content)
            if START_MARKER in line or f"- {START_MARKER}" in line
        )
    except StopIteration:
        raise RuntimeError(f"Could not find start marker {START_MARKER!r} in README")
    try:
        end_idx = next(i for i, line in enumerate(content) if END_MARKER in line)
    except StopIteration:
        raise RuntimeError(f"Could not find end marker {END_MARKER!r} in README")
    if end_idx <= start_idx:
        raise RuntimeError("End marker appears before start marker in README")

    generated_lines = render_readme_axis_lines().strip().splitlines()
    new_content = content[:start_idx] + generated_lines + content[end_idx:]
    readme_path.write_text("\n".join(new_content) + "\n", encoding="utf-8")
    print(f"Refreshed axis lines in {readme_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--readme",
        type=Path,
        default=ROOT / "GPT" / "readme.md",
        help="Path to GPT README to update.",
    )
    args = parser.parse_args()
    refresh_readme(args.readme)
    return 0


if __name__ == "__main__":
    sys.exit(main())
