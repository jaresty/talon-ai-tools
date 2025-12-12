#!/usr/bin/env python3
"""Validate axis catalog alignment (axisConfig ↔ Talon lists ↔ static prompts).

This CLI checks for drift between:
- axisConfig tokens and Talon list tokens.
- static prompt axis tokens and the catalog's axis tokens.

Exit code 0 when all checks pass; otherwise exits 1 and prints findings.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Talon bootstrap (optional)
try:
    from bootstrap import bootstrap  # type: ignore
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from talon_user.lib.axisCatalog import axis_catalog  # noqa: E402


def _format_list(items: List[str]) -> str:
    return ", ".join(sorted(items)) if items else "(none)"


def validate_axis_tokens(catalog) -> List[str]:
    errors: List[str] = []
    axes = catalog["axes"]
    list_tokens = catalog["axis_list_tokens"]

    for axis_name, token_map in axes.items():
        axis_tokens = set((token_map or {}).keys())
        talon_tokens = set(list_tokens.get(axis_name, []))
        extra = talon_tokens - axis_tokens
        missing = axis_tokens - talon_tokens
        if extra:
            errors.append(
                f"[axis list drift] axis={axis_name} Talon list tokens not in axisConfig: {_format_list(list(extra))}"
            )
        if missing:
            errors.append(
                f"[axis list drift] axis={axis_name} axisConfig tokens missing from Talon list: {_format_list(list(missing))}"
            )
    return errors


def validate_static_prompt_axes(catalog) -> List[str]:
    errors: List[str] = []
    axes = catalog["axes"]
    profiled = catalog["static_prompts"].get("profiled", [])

    for entry in profiled:
        name = entry.get("name", "<unknown>")
        entry_axes = entry.get("axes", {}) or {}
        for axis_name, value in entry_axes.items():
            if axis_name == "completeness":
                # Completeness may include free-form hints (for example, "path"); skip drift checks.
                continue
            tokens = value if isinstance(value, list) else [value]
            axis_tokens = set((axes.get(axis_name) or {}).keys())
            for token in tokens:
                if token not in axis_tokens:
                    errors.append(
                        f"[static prompt drift] staticPrompt={name} axis={axis_name} token {token!r} not in axisConfig"
                    )
    return errors


def validate_static_prompt_descriptions(catalog) -> List[str]:
    errors: List[str] = []
    descriptions = catalog.get("static_prompt_descriptions", {}) or {}
    profiled = catalog.get("static_prompts", {}).get("profiled", []) or []
    for entry in profiled:
        name = entry.get("name", "")
        if not name:
            continue
        desc = (descriptions.get(name) or "").strip()
        catalog_desc = (entry.get("description") or "").strip()
        if desc != catalog_desc:
            errors.append(
                f"[static prompt description drift] {name!r} catalog description mismatch between overrides and catalog entry"
            )
    return errors


def main() -> int:
    catalog = axis_catalog()
    errors: List[str] = []
    errors.extend(validate_axis_tokens(catalog))
    errors.extend(validate_static_prompt_axes(catalog))
    errors.extend(validate_static_prompt_descriptions(catalog))

    if errors:
        print("Axis catalog validation failed:")
        for err in errors:
            print(f" - {err}")
        return 1

    print("Axis catalog validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
