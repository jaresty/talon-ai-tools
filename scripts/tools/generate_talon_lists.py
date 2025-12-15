#!/usr/bin/env python3
"""Generate Talon list files for axes and static prompts from the catalog SSOT.

This helper writes token-only list files so Talon grammars stay aligned with
`lib/axisConfig.py` / `lib/staticPromptConfig.py` without manual edits.
Existing files in the output directory will be overwritten.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from lib.axisCatalog import axis_catalog  # type: ignore  # noqa: E402
from lib.staticPromptConfig import static_prompt_catalog  # type: ignore  # noqa: E402


LIST_NAMES = [
    "completenessModifier.talon-list",
    "scopeModifier.talon-list",
    "methodModifier.talon-list",
    "formModifier.talon-list",
    "channelModifier.talon-list",
    "directionalModifier.talon-list",
    "staticPrompt.talon-list",
]


def _write_list(filename: Path, list_name: str, tokens: list[str]) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"list: user.{list_name}", "-"]
    for token in sorted(tokens):
        if token:
            lines.append(f"{token}: {token}")
    text = "\n".join(lines) + "\n"
    filename.write_text(text, encoding="utf-8")


def generate(out_dir: Path) -> None:
    catalog = axis_catalog()
    axes = catalog.get("axes", {}) or {}
    axis_lists = catalog.get("axis_list_tokens", {}) or {}

    axis_to_list_name = {
        "completeness": "completenessModifier",
        "scope": "scopeModifier",
        "method": "methodModifier",
        "form": "formModifier",
        "channel": "channelModifier",
        "directional": "directionalModifier",
    }

    for axis, list_name in axis_to_list_name.items():
        tokens = axis_lists.get(axis) or list((axes.get(axis) or {}).keys())
        _write_list(out_dir / f"{list_name}.talon-list", list_name, tokens)

    static_catalog = static_prompt_catalog()
    static_tokens = static_catalog.get("talon_list_tokens") or []
    _write_list(out_dir / "staticPrompt.talon-list", "staticPrompt", static_tokens)


def _read_tokens(path: Path) -> list[str]:
    tokens: list[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or s.startswith("list:") or s == "-":
                    continue
                if ":" not in s:
                    continue
                key, _ = s.split(":", 1)
                key = key.strip()
                if key:
                    tokens.append(key)
    except FileNotFoundError:
        return []
    return tokens


def _compare_lists(expected_dir: Path, actual_dir: Path) -> list[str]:
    errors: list[str] = []
    for name in LIST_NAMES:
        expected = set(_read_tokens(expected_dir / name))
        actual = set(_read_tokens(actual_dir / name))
        if expected != actual:
            missing = expected - actual
            extra = actual - expected
            if missing:
                errors.append(f"{name} missing: {', '.join(sorted(missing))}")
            if extra:
                errors.append(f"{name} extra: {', '.join(sorted(extra))}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Talon list files from the axis/static prompt catalog."
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "GPT" / "lists",
        help="Output directory for generated Talon lists (default: GPT/lists).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write over existing files; instead, compare generated output to the target directory and exit non-zero on drift.",
    )
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            generate(tmp_path)
            errors = _compare_lists(tmp_path, args.out_dir)
            if errors:
                print("Talon list check failed:")
                for err in errors:
                    print(f" - {err}")
                return 1
        print("Talon list check passed.")
        return 0

    generate(args.out_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
