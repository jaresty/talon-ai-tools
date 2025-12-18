#!/usr/bin/env python3
"""Validate axis catalog alignment (axisConfig ↔ Talon lists ↔ static prompts).

This CLI checks for drift between:
- axisConfig tokens and Talon list tokens.
- static prompt axis tokens and the catalog's axis tokens.
- catalog-generated Talon lists and list files when explicitly enabled (default skips list-file validation for catalog-only flow).

Usage:
- Default: `python3 scripts/tools/axis-catalog-validate.py` (catalog-only; skips on-disk lists).
- Custom lists: `... --lists-dir /path/to/lists` to validate another Talon lists directory (add `--no-skip-list-files` to enforce).
- Catalog-only: `--skip-list-files` (default) skips on-disk Talon list validation for catalog-only environments.
- When enforcing list checks (`--no-skip-list-files`), `--lists-dir` is required to point at the Talon lists to validate; regenerate them with `python3 scripts/tools/generate_talon_lists.py --out-dir <dir>` if needed.

Exit code 0 when all checks pass; otherwise exits 1 and prints findings.
"""

from __future__ import annotations

import sys
import tempfile
import argparse
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
from scripts.tools.generate_talon_lists import generate as generate_talon_lists  # noqa: E402


def _format_list(items: List[str]) -> str:
    return ", ".join(sorted(items)) if items else "(none)"


def validate_axis_tokens(catalog) -> List[str]:
    errors: List[str] = []
    axes = catalog.get("axes", {}) or {}
    list_tokens = catalog.get("axis_list_tokens", {}) or {}
    if not axes:
        errors.append("[axis catalog drift] catalog missing axes")
        return errors

    extra_axes = set(list_tokens.keys()) - set(axes.keys())
    if extra_axes:
        errors.append(
            "[axis list drift] axis_list_tokens contains axes not present in catalog axes: "
            f"{_format_list(list(extra_axes))}"
        )

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


def validate_no_legacy_style_axis(catalog) -> List[str]:
    errors: List[str] = []
    axes = catalog.get("axes", {}) or {}
    list_tokens = catalog.get("axis_list_tokens", {}) or {}

    if "style" in axes:
        errors.append(
            "[axis legacy style] catalog axes still include legacy 'style' axis; drop it in favour of form/channel per ADR-0056."
        )
    if "style" in list_tokens:
        errors.append(
            "[axis legacy style] axis_list_tokens still expose legacy 'style' axis; regenerate Talon lists without styleModifier."
        )

    profiled = (catalog.get("static_prompts") or {}).get("profiled", []) or []
    legacy_prompts: List[str] = []
    for entry in profiled:
        axes_map = entry.get("axes")
        if isinstance(axes_map, dict) and "style" in axes_map:
            legacy_prompts.append(str(entry.get("name") or "<unnamed>"))
    if legacy_prompts:
        joined = ", ".join(sorted(set(legacy_prompts)))
        errors.append(
            "[axis legacy style] static_prompts.profiled still reference legacy 'style' axis for: "
            f"{joined}. Remove style assignments before regenerating docs."
        )

    return errors


def validate_static_prompt_axes(catalog) -> List[str]:
    errors: List[str] = []
    axes = catalog.get("axes", {})
    profiled = (catalog.get("static_prompts") or {}).get("profiled", [])

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
    profiled = (catalog.get("static_prompts") or {}).get("profiled", []) or []
    profiled_names = {entry.get("name", "") for entry in profiled if entry.get("name")}
    for entry in profiled:
        name = entry.get("name", "")
        if not name:
            continue
        if name not in descriptions:
            errors.append(
                f"[static prompt description drift] static_prompt_descriptions missing entry for {name!r}"
            )
            continue
        desc = (descriptions.get(name) or "").strip()
        catalog_desc = (entry.get("description") or "").strip()
        if desc != catalog_desc:
            errors.append(
                f"[static prompt description drift] {name!r} catalog description mismatch between overrides and catalog entry"
            )
    extra_descriptions = set(descriptions.keys()) - profiled_names
    if extra_descriptions:
        for name in sorted(extra_descriptions):
            errors.append(
                f"[static prompt description drift] static_prompt_descriptions contains entry not in static_prompts.profiled: {name}"
            )
    return errors


def validate_static_prompt_sections_present(catalog) -> List[str]:
    """Ensure catalog carries the static prompt sections expected by SSOT."""

    errors: List[str] = []
    if not catalog.get("static_prompts"):
        errors.append("[static prompt drift] catalog missing static_prompts")
    if not catalog.get("static_prompt_descriptions"):
        errors.append(
            "[static prompt drift] catalog missing static_prompt_descriptions"
        )
    if not catalog.get("static_prompt_profiles"):
        errors.append("[static prompt drift] catalog missing static_prompt_profiles")
    return errors


def validate_static_prompt_required_profiles(
    catalog, required: list[str] | None = None
) -> List[str]:
    """Ensure key static prompt profiles exist in the catalog."""

    errors: List[str] = []
    profiled = (catalog.get("static_prompts") or {}).get("profiled", []) or []
    names = {entry.get("name") for entry in profiled if entry.get("name")}
    # Default required set is the static prompt profiles advertised in the catalog.
    required_names = required or list(
        (catalog.get("static_prompt_profiles") or {}).keys()
    )
    missing = [name for name in required_names if name and name not in names]
    if missing:
        errors.append(
            f"[static prompt drift] required static prompt profiles missing from catalog: {', '.join(sorted(missing))}"
        )
    return errors


def validate_static_prompt_profile_keys(catalog) -> List[str]:
    """Ensure static prompt profile keys and profiled entries stay aligned."""

    errors: List[str] = []
    profiles = set((catalog.get("static_prompt_profiles") or {}).keys())
    profiled = {
        entry.get("name")
        for entry in (catalog.get("static_prompts") or {}).get("profiled", [])
    }
    missing_profiles = profiled - profiles
    missing_profiled = profiles - profiled
    if missing_profiles:
        errors.append(
            f"[static prompt drift] profiled static prompts missing from static_prompt_profiles: {', '.join(sorted(missing_profiles))}"
        )
    if missing_profiled:
        errors.append(
            f"[static prompt drift] static_prompt_profiles contains entries not in static_prompts.profiled: {', '.join(sorted(missing_profiled))}"
        )
    return errors


def _read_list_tokens(path: Path) -> list[str]:
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


def validate_generated_lists(catalog, lists_dir: Path) -> List[str]:
    """Ensure committed Talon lists match catalog-generated tokens."""

    errors: List[str] = []
    if not lists_dir.exists():
        errors.append(
            f"[list generation drift] lists_dir not found: {lists_dir} (pass --lists-dir to point at Talon lists; regenerate with scripts/tools/generate_talon_lists.py)"
        )
        return errors
    if not lists_dir.is_dir():
        errors.append(
            f"[list generation drift] lists_dir is not a directory: {lists_dir} (pass --lists-dir to point at Talon lists; regenerate with scripts/tools/generate_talon_lists.py)"
        )
        return errors

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        generate_talon_lists(tmp_path)

        list_names = [
            "completenessModifier.talon-list",
            "scopeModifier.talon-list",
            "methodModifier.talon-list",
            "formModifier.talon-list",
            "channelModifier.talon-list",
            "directionalModifier.talon-list",
            "staticPrompt.talon-list",
        ]

        for name in list_names:
            target_path = lists_dir / name
            if not target_path.exists():
                errors.append(
                    f"[list generation drift] {name} not found in lists_dir={lists_dir} (regenerate via scripts/tools/generate_talon_lists.py --out-dir {lists_dir})"
                )
                continue
            expected = set(_read_list_tokens(tmp_path / name))
            actual = set(_read_list_tokens(target_path))
            if expected != actual:
                missing = expected - actual
                extra = actual - expected
                if missing:
                    errors.append(
                        f"[list generation drift] {name} missing tokens from catalog generator: {_format_list(list(missing))} (regenerate via scripts/tools/generate_talon_lists.py --out-dir {lists_dir})"
                    )
                if extra:
                    errors.append(
                        f"[list generation drift] {name} contains tokens not in catalog generator: {_format_list(list(extra))} (regenerate via scripts/tools/generate_talon_lists.py --out-dir {lists_dir})"
                    )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate axis/static prompt catalog and Talon list alignment."
    )
    parser.add_argument(
        "--lists-dir",
        type=Path,
        default=None,
        help="Path to the directory containing Talon list files (default: none; catalog-only unless --no-skip-list-files; regenerate with scripts/tools/generate_talon_lists.py --out-dir <dir>)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print a short summary when validation succeeds.",
    )
    parser.add_argument(
        "--skip-list-files",
        action="store_true",
        default=True,
        help="Skip validating Talon list files on disk (catalog-only environments). Set to false with --no-skip-list-files to enforce list checks.",
    )
    parser.add_argument(
        "--no-skip-list-files",
        action="store_false",
        dest="skip_list_files",
        help="Alias to force list file validation (for repos that track Talon lists); requires --lists-dir.",
    )
    args = parser.parse_args()

    errors: List[str] = []
    lists_dir = args.lists_dir

    if not args.skip_list_files:
        if lists_dir is None:
            errors.append(
                "[list generation drift] lists_dir is required when enforcing list checks (pass --lists-dir; regenerate via scripts/tools/generate_talon_lists.py --out-dir <dir>)"
            )
        elif not lists_dir.exists():
            errors.append(
                f"[list generation drift] lists_dir not found: {lists_dir} (pass --lists-dir to point at Talon lists; regenerate via scripts/tools/generate_talon_lists.py --out-dir <dir>)"
            )
        elif not lists_dir.is_dir():
            errors.append(
                f"[list generation drift] lists_dir is not a directory: {lists_dir} (pass --lists-dir to point at Talon lists; regenerate via scripts/tools/generate_talon_lists.py --out-dir <dir>)"
            )

        if errors:
            print(f"Axis catalog validation failed (errors: {len(errors)}):")
            for err in sorted(errors):
                print(f" - {err}")
            return 1

    effective_lists_dir: Path | None = None if args.skip_list_files else lists_dir
    catalog = axis_catalog(lists_dir=effective_lists_dir)
    errors.extend(validate_axis_tokens(catalog))
    errors.extend(validate_no_legacy_style_axis(catalog))
    errors.extend(validate_static_prompt_axes(catalog))
    errors.extend(validate_static_prompt_descriptions(catalog))
    errors.extend(validate_static_prompt_sections_present(catalog))
    errors.extend(validate_static_prompt_required_profiles(catalog))
    errors.extend(validate_static_prompt_profile_keys(catalog))
    if not args.skip_list_files:
        errors.extend(validate_generated_lists(catalog, lists_dir))

    if errors:
        print(f"Axis catalog validation failed (errors: {len(errors)}):")
        for err in sorted(errors):
            print(f" - {err}")
        return 1

    axes = catalog.get("axes", {}) or {}
    lists_mode = "skipped" if args.skip_list_files else f"validated@{lists_dir}"
    lists_dir_display = "<skipped>" if args.skip_list_files else str(lists_dir)
    lists_dir_arg = (
        f" lists_dir_arg={lists_dir}" if args.skip_list_files and lists_dir else ""
    )
    note = ""
    if args.skip_list_files and lists_dir:
        note = (
            f"Note: lists_dir={lists_dir} provided but list validation skipped "
            f"(lists_dir=<skipped>, lists_validation=skipped); pass --no-skip-list-files to enforce."
        )

    if args.verbose:
        print(
            f"Axis catalog validation passed. Axes={len(axes)} static_prompts={len(catalog.get('static_prompts', {}).get('profiled', []))} lists_dir={lists_dir_display}{lists_dir_arg} lists_validation={lists_mode}"
        )
        if note:
            print(note)
    else:
        if note:
            print(note)
        if args.skip_list_files:
            print("Axis catalog validation passed.")
        else:
            print(
                f"Axis catalog validation passed. Axes={len(axes)} static_prompts={len(catalog.get('static_prompts', {}).get('profiled', []))} lists_dir={lists_dir_display} lists_validation={lists_mode}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
