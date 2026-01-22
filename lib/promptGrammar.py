from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .axisCatalog import axis_catalog
from .axisMappings import DEFAULT_COMPLETENESS_TOKEN
from .personaCatalog import get_persona_intent_catalog
from .personaConfig import PERSONA_KEY_TO_VALUE
from .staticPromptConfig import STATIC_PROMPT_CONFIG
from .talonSettings import axis_incompatibilities, axis_priority, axis_soft_caps

SCHEMA_VERSION = "1.0"


_SLUG_INVALID_CHARS = re.compile(r"[^a-z0-9_-]+")
_MULTIPLE_HYPHENS = re.compile(r"-{2,}")


def _slugify_token(value: str) -> str:
    normalized = value.strip().lower()
    if not normalized:
        return ""
    normalized = normalized.replace(" ", "-")
    normalized = _SLUG_INVALID_CHARS.sub("-", normalized)
    normalized = _MULTIPLE_HYPHENS.sub("-", normalized)
    normalized = normalized.strip("-")
    return normalized


def _unique_slug(label: str, *, category: str, taken: set[str]) -> str:
    base = _slugify_token(label)
    if base and base not in taken:
        taken.add(base)
        return base

    fallback_base = _slugify_token(f"{category}-{label}")
    if not fallback_base:
        fallback_base = base or _slugify_token(f"{category}-token") or "token"

    candidate = fallback_base
    index = 2
    while candidate in taken:
        candidate = f"{fallback_base}-{index}"
        index += 1
    taken.add(candidate)
    return candidate


def _map_slugs(
    labels: Iterable[str], *, category: str, taken: set[str]
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    normalized_labels = {
        str(item).strip()
        for item in labels
        if isinstance(item, str) and str(item).strip()
    }
    for label in sorted(normalized_labels):
        mapping[label] = _unique_slug(label, category=category, taken=taken)
    return mapping


def _strip_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _strip_none(sub_value)
            for key, sub_value in value.items()
            if sub_value is not None
        }
    if isinstance(value, list):
        return [_strip_none(item) for item in value if item is not None]
    if isinstance(value, tuple):
        return [_strip_none(item) for item in value if item is not None]
    if isinstance(value, set):
        return [_strip_none(item) for item in sorted(value)]
    return value


def _normalize(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _normalize(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _normalize(sub_value)
            for key, sub_value in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, list):
        return [_normalize(item) for item in value]
    if isinstance(value, tuple):
        return [_normalize(item) for item in list(value)]
    if isinstance(value, set):
        return [_normalize(item) for item in sorted(value)]
    return value


def _canonicalize_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: _normalize(_strip_none(sub_value))
        for key, sub_value in sorted(value.items(), key=lambda item: str(item[0]))
    }


def _default_static_prompt() -> str:
    # Per ADR 0086: "infer" was retired as it violated task-defines-success principle.
    # Default to empty string to allow open-ended responses when no task is specified,
    # since the current task catalog doesn't cover all possible definitions of success.
    return ""


def _build_axis_section(
    catalog: Mapping[str, Any], taken_slugs: set[str]
) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    axes = catalog.get("axes") or {}
    axis_definitions = _canonicalize_mapping(axes)

    axis_list_tokens_raw = catalog.get("axis_list_tokens") or {}
    axis_list_tokens: dict[str, list[str]] = {}
    for axis, tokens in sorted(
        axis_list_tokens_raw.items(), key=lambda item: str(item[0])
    ):
        axis_list_tokens[str(axis)] = sorted(set(tokens or []))

    axis_slugs: dict[str, dict[str, str]] = {}
    for axis, definitions in axis_definitions.items():
        labels: set[str] = set(definitions.keys())
        labels.update(axis_list_tokens.get(axis, []))
        axis_slugs[axis] = _map_slugs(
            labels, category=f"axis-{axis}", taken=taken_slugs
        )

    for axis, tokens in axis_list_tokens.items():
        if axis not in axis_slugs:
            axis_slugs[axis] = _map_slugs(
                tokens, category=f"axis-{axis}", taken=taken_slugs
            )

    return (
        {
            "definitions": axis_definitions,
            "list_tokens": axis_list_tokens,
        },
        axis_slugs,
    )


def _build_static_section(
    catalog: Mapping[str, Any], taken_slugs: set[str]
) -> tuple[dict[str, Any], dict[str, str]]:
    static_catalog = catalog.get("static_prompts") or {}
    static_profiles = catalog.get("static_prompt_profiles") or {}
    static_descriptions = catalog.get("static_prompt_descriptions") or {}

    section = {
        "catalog": _normalize(_strip_none(static_catalog)),
        "profiles": _canonicalize_mapping(static_profiles),
        "descriptions": _canonicalize_mapping(static_descriptions),
    }

    labels: set[str] = set(section["profiles"].keys()) | set(
        section["descriptions"].keys()
    )
    for name in STATIC_PROMPT_CONFIG.keys():
        if isinstance(name, str) and name.strip():
            labels.add(name.strip())
    profiled = static_catalog.get("catalog", {}).get("profiled", [])
    for entry in profiled:
        name = str(entry.get("name", "")).strip()
        if name:
            labels.add(name)

    slug_map = _map_slugs(labels, category="static", taken=taken_slugs)
    return section, slug_map


def _build_persona_section(
    taken_slugs: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    snapshot = get_persona_intent_catalog()

    persona_axes_raw = snapshot.persona_axis_tokens or {}
    persona_axes: dict[str, list[str]] = {}
    for axis, tokens in sorted(persona_axes_raw.items(), key=lambda item: str(item[0])):
        persona_axes[str(axis)] = sorted(tokens or [])

    persona_presets_raw = snapshot.persona_presets or {}
    persona_presets = {
        key: _normalize(_strip_none(value))
        for key, value in sorted(
            persona_presets_raw.items(), key=lambda item: str(item[0])
        )
    }

    persona_spoken_map = _canonicalize_mapping(snapshot.persona_spoken_map or {})

    persona_docs_raw = PERSONA_KEY_TO_VALUE or {}
    persona_docs = {
        str(axis): _canonicalize_mapping(mapping)
        for axis, mapping in sorted(
            persona_docs_raw.items(), key=lambda item: str(item[0])
        )
    }

    intent_presets_raw = snapshot.intent_presets or {}
    intent_presets = {
        key: _normalize(_strip_none(value))
        for key, value in sorted(
            intent_presets_raw.items(), key=lambda item: str(item[0])
        )
    }

    intent_axis_tokens = snapshot.intent_axis_tokens or {}
    intent_section = {
        "axis_tokens": {
            str(key): sorted(tokens or [])
            for key, tokens in sorted(
                intent_axis_tokens.items(), key=lambda item: str(item[0])
            )
        },
        "presets": intent_presets,
        "spoken_map": _canonicalize_mapping(snapshot.intent_spoken_map or {}),
        "buckets": _canonicalize_mapping(snapshot.intent_buckets or {}),
        "display_map": _canonicalize_mapping(snapshot.intent_display_map or {}),
        "docs": persona_docs.get("intent", {}),
    }

    persona_axes_slugs: dict[str, dict[str, str]] = {}
    for axis, tokens in persona_axes.items():
        persona_axes_slugs[axis] = _map_slugs(
            tokens, category=f"persona-{axis}", taken=taken_slugs
        )

    for axis, tokens in intent_section["axis_tokens"].items():
        existing = persona_axes_slugs.get(axis)
        if existing is None:
            persona_axes_slugs[axis] = _map_slugs(
                tokens, category=f"persona-{axis}", taken=taken_slugs
            )
        else:
            missing = [token for token in tokens if token not in existing]
            if missing:
                existing.update(
                    _map_slugs(missing, category=f"persona-{axis}", taken=taken_slugs)
                )
                persona_axes_slugs[axis] = existing

    persona_preset_tokens = [
        f"persona={str(key).strip()}"
        for key in persona_presets.keys()
        if str(key).strip()
    ]
    persona_preset_slugs = _map_slugs(
        persona_preset_tokens, category="persona-preset", taken=taken_slugs
    )

    persona_slug_map: dict[str, Any] = {
        "axes": persona_axes_slugs,
        "presets": persona_preset_slugs,
    }

    section = {
        "axes": persona_axes,
        "docs": persona_docs,
        "presets": persona_presets,
        "spoken_map": persona_spoken_map,
        "intent": intent_section,
    }
    return section, persona_slug_map


def _build_hierarchy_section() -> dict[str, Any]:
    return {
        "axis_priority": list(axis_priority()),
        "axis_soft_caps": axis_soft_caps(),
        "axis_incompatibilities": axis_incompatibilities(),
        "defaults": {
            "static_prompt": _default_static_prompt(),
            "completeness": DEFAULT_COMPLETENESS_TOKEN,
        },
    }


def _compute_checksum(section: Any) -> str:
    canonical = json.dumps(
        section,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def prompt_grammar_payload() -> dict[str, Any]:
    catalog = axis_catalog()
    taken_slugs: set[str] = set()
    axis_section, axis_slugs = _build_axis_section(catalog, taken_slugs)
    static_section, static_slugs = _build_static_section(catalog, taken_slugs)
    persona_section, persona_slugs = _build_persona_section(taken_slugs)
    hierarchy_section = _build_hierarchy_section()

    canonical_to_slug: dict[str, str] = {}

    def _register(mapping: Mapping[str, str]) -> None:
        for canonical, slug in mapping.items():
            canonical_to_slug[canonical] = slug

    for mapping in axis_slugs.values():
        _register(mapping)
    _register(static_slugs)
    persona_axes_slugs = persona_slugs.get("axes", {})
    for mapping in persona_axes_slugs.values():
        _register(mapping)
    _register(persona_slugs.get("presets", {}))

    command_slugs = _map_slugs(
        ["build", "completion", "help"],
        category="command",
        taken=taken_slugs,
    )
    _register(command_slugs)

    override_slugs: dict[str, dict[str, str]] = {}

    override_slugs["static"] = _map_slugs(
        (f"static={label}" for label in static_slugs.keys()),
        category="override-static",
        taken=taken_slugs,
    )
    _register(override_slugs["static"])

    for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
        labels = axis_slugs.get(axis, {})
        if not labels:
            continue
        override_slugs[axis] = _map_slugs(
            (f"{axis}={label}" for label in labels.keys()),
            category=f"override-{axis}",
            taken=taken_slugs,
        )
        _register(override_slugs[axis])

    for axis in ("voice", "audience", "tone", "intent"):
        labels = persona_axes_slugs.get(axis, {})
        if not labels:
            continue
        key = f"persona.{axis}"
        override_slugs[key] = _map_slugs(
            (f"{axis}={label}" for label in labels.keys()),
            category=f"override-{axis}",
            taken=taken_slugs,
        )
        _register(override_slugs[key])

    canonical_to_slug = dict(sorted(canonical_to_slug.items()))

    slug_section = {
        "axes": axis_slugs,
        "static": static_slugs,
        "persona": persona_slugs,
        "commands": command_slugs,
        "overrides": override_slugs,
        "canonical_to_slug": canonical_to_slug,
    }

    sections: dict[str, Any] = {
        "axes": axis_section,
        "static_prompts": static_section,
        "persona": persona_section,
        "hierarchy": hierarchy_section,
        "slugs": slug_section,
    }

    checksums = {name: _compute_checksum(content) for name, content in sections.items()}

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        **sections,
        "checksums": checksums,
    }
    return payload


__all__ = ["SCHEMA_VERSION", "prompt_grammar_payload"]
