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
from lib.personaConfig import persona_intent_maps  # type: ignore  # noqa: E402
from lib.personaOrchestrator import get_persona_intent_orchestrator  # type: ignore  # noqa: E402


LIST_NAMES = [
    "completenessModifier.talon-list",
    "scopeModifier.talon-list",
    "methodModifier.talon-list",
    "formModifier.talon-list",
    "channelModifier.talon-list",
    "directionalModifier.talon-list",
    "staticPrompt.talon-list",
    "personaPreset.talon-list",
    "intentPreset.talon-list",
]


def _write_list(filename: Path, list_name: str, tokens: list[str]) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"list: user.{list_name}", "-"]
    for token in sorted(tokens):
        if token:
            lines.append(f"{token}: {token}")
    text = "\n".join(lines) + "\n"
    filename.write_text(text, encoding="utf-8")


def _write_mapping_list(
    filename: Path, list_name: str, mapping: dict[str, str]
) -> None:
    filename.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"list: user.{list_name}", "-"]
    for alias, canonical in sorted(mapping.items(), key=lambda item: item[0].lower()):
        alias = alias.strip()
        canonical = canonical.strip()
        if not alias or not canonical:
            continue
        lines.append(f"{alias}: {canonical}")
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

    persona_mapping: dict[str, str] = {}
    intent_mapping: dict[str, str] = {}

    def _record_persona(alias: object, canonical: object) -> None:
        alias_str = str(alias or "").strip()
        canonical_str = str(canonical or "").strip()
        if alias_str and canonical_str:
            persona_mapping.setdefault(alias_str, canonical_str)

    def _record_intent(alias: object, canonical: object) -> None:
        alias_str = str(alias or "").strip()
        canonical_str = str(canonical or "").strip()
        if alias_str and canonical_str:
            intent_mapping.setdefault(alias_str, canonical_str)

    try:
        orchestrator = get_persona_intent_orchestrator()
    except Exception:
        orchestrator = None

    if orchestrator is not None:
        persona_presets = getattr(orchestrator, "persona_presets", {}) or {}
        for key, preset in persona_presets.items():
            canonical = str(getattr(preset, "key", key) or "").strip()
            if not canonical:
                continue
            _record_persona(canonical, canonical)
            _record_persona(getattr(preset, "spoken", ""), canonical)
            _record_persona(getattr(preset, "label", ""), canonical)
        for alias, canonical in (
            getattr(orchestrator, "persona_aliases", {}) or {}
        ).items():
            _record_persona(alias, canonical)

        intent_presets = getattr(orchestrator, "intent_presets", {}) or {}
        intent_display_map = dict(getattr(orchestrator, "intent_display_map", {}) or {})
        for key, preset in intent_presets.items():
            canonical = str(getattr(preset, "key", key) or "").strip()
            if not canonical:
                continue
            _record_intent(canonical, canonical)
            _record_intent(intent_display_map.get(canonical), canonical)
            _record_intent(
                intent_display_map.get(
                    str(getattr(preset, "intent", "") or "").strip()
                ),
                canonical,
            )
            _record_intent(getattr(preset, "intent", ""), canonical)
            _record_intent(getattr(preset, "label", ""), canonical)
        for alias, canonical in (
            getattr(orchestrator, "intent_aliases", {}) or {}
        ).items():
            _record_intent(alias, canonical)
        for alias, canonical in (
            getattr(orchestrator, "intent_synonyms", {}) or {}
        ).items():
            _record_intent(alias, canonical)

    maps = persona_intent_maps()
    if maps is not None:
        persona_presets = getattr(maps, "persona_presets", {}) or {}
        persona_aliases = getattr(maps, "persona_preset_aliases", {}) or {}
        for key, preset in persona_presets.items():
            canonical = str(getattr(preset, "key", key) or "").strip()
            if not canonical:
                continue
            _record_persona(canonical, canonical)
            _record_persona(getattr(preset, "spoken", ""), canonical)
            _record_persona(getattr(preset, "label", ""), canonical)
        for alias, canonical in persona_aliases.items():
            _record_persona(alias, canonical)

        intent_presets = getattr(maps, "intent_presets", {}) or {}
        for key, preset in intent_presets.items():
            canonical = str(getattr(preset, "key", key) or "").strip()
            if not canonical:
                continue
            _record_intent(canonical, canonical)
            _record_intent(getattr(preset, "intent", ""), canonical)
        intent_aliases = getattr(maps, "intent_preset_aliases", {}) or {}
        intent_synonyms = getattr(maps, "intent_synonyms", {}) or {}
        for alias, canonical in intent_aliases.items():
            _record_intent(alias, canonical)
        for alias, canonical in intent_synonyms.items():
            _record_intent(alias, canonical)

    _write_mapping_list(
        out_dir / "personaPreset.talon-list", "personaPreset", persona_mapping
    )
    _write_mapping_list(
        out_dir / "intentPreset.talon-list", "intentPreset", intent_mapping
    )


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
                alias, value = s.split(":", 1)
                alias = alias.strip()
                value = value.strip()
                if alias:
                    tokens.append(f"{alias}:{value}")
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
