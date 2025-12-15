#!/usr/bin/env python3
"""
Codemod helper to rename the Persona/Intent Why axis from "intent" to "intent".

This is a mechanical helper only; it does not run automatically. It targets the
main persona/intent touchpoints and can be iterated safely in small batches.
"""

from __future__ import annotations

import argparse
import pathlib
import re
from typing import Iterable


DEFAULT_PATTERNS = (
    # axis key/value maps
    (r'PERSONA_KEY_TO_VALUE\["intent"\]', 'PERSONA_KEY_TO_VALUE["intent"]'),
    (r'"intent":', '"intent":'),
    # system prompt field/setting names
    (r"\bpurpose\b", "intent"),
    (r"model_default_intent", "model_default_intent"),
    (r"modelIntent", "modelIntent"),
    # tests/help labels
    (r"Intent", "Intent"),
)


def apply_replacements(text: str, replacements: Iterable[tuple[str, str]]) -> str:
    new_text = text
    for pattern, repl in replacements:
        new_text = re.sub(pattern, repl, new_text)
    return new_text


def codemod_file(path: pathlib.Path, replacements: Iterable[tuple[str, str]]) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = apply_replacements(original, replacements)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def iter_files(root: pathlib.Path, globs: tuple[str, ...]) -> Iterable[pathlib.Path]:
    for pattern in globs:
        yield from root.rglob(pattern)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Codemod the Persona/Intent Why axis from 'intent' to 'intent'."
    )
    parser.add_argument(
        "--root",
        type=pathlib.Path,
        default=pathlib.Path("."),
        help="Repo root to search from (default: current directory).",
    )
    parser.add_argument(
        "--glob",
        action="append",
        default=[
            "*.py",
            "*.talon",
            "*.md",
        ],
        help="Glob patterns to include (can be repeated). Defaults to Python/Talon/Markdown.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        nargs=2,
        metavar=("PATTERN", "REPLACEMENT"),
        help="Additional regex replacement to apply (can be repeated).",
    )
    args = parser.parse_args()

    replacements: list[tuple[str, str]] = list(DEFAULT_PATTERNS)
    if args.pattern:
        replacements.extend([(p, r) for p, r in args.pattern])

    changed = 0
    scanned = 0
    for path in iter_files(args.root, tuple(args.glob)):
        if not path.is_file():
            continue
        scanned += 1
        if codemod_file(path, replacements):
            changed += 1
            print(f"updated: {path}")

    print(f"Codemod complete. Scanned {scanned} files; changed {changed}.")


if __name__ == "__main__":
    main()
