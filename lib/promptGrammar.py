from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from .axisCatalog import axis_catalog
from .axisMappings import DEFAULT_COMPLETENESS_TOKEN
from .personaCatalog import get_persona_intent_catalog
from .personaConfig import PERSONA_KEY_TO_VALUE
from .staticPromptConfig import STATIC_PROMPT_CONFIG
from .talonSettings import axis_incompatibilities, axis_priority, axis_soft_caps

SCHEMA_VERSION = "1.0"


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
    if "infer" in STATIC_PROMPT_CONFIG:
        return "infer"
    if STATIC_PROMPT_CONFIG:
        return next(iter(sorted(STATIC_PROMPT_CONFIG.keys())))
    return ""


def _build_axis_section(catalog: Mapping[str, Any]) -> dict[str, Any]:
    axes = catalog.get("axes") or {}
    axis_definitions = _canonicalize_mapping(axes)

    axis_list_tokens_raw = catalog.get("axis_list_tokens") or {}
    axis_list_tokens: dict[str, list[str]] = {}
    for axis, tokens in sorted(
        axis_list_tokens_raw.items(), key=lambda item: str(item[0])
    ):
        axis_list_tokens[str(axis)] = sorted(set(tokens or []))

    return {
        "definitions": axis_definitions,
        "list_tokens": axis_list_tokens,
    }


def _build_static_section(catalog: Mapping[str, Any]) -> dict[str, Any]:
    static_catalog = catalog.get("static_prompts") or {}
    static_profiles = catalog.get("static_prompt_profiles") or {}
    static_descriptions = catalog.get("static_prompt_descriptions") or {}

    return {
        "catalog": _normalize(_strip_none(static_catalog)),
        "profiles": _canonicalize_mapping(static_profiles),
        "descriptions": _canonicalize_mapping(static_descriptions),
    }


def _build_persona_section() -> dict[str, Any]:
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
            key: sorted(tokens or [])
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

    return {
        "axes": persona_axes,
        "docs": persona_docs,
        "presets": persona_presets,
        "spoken_map": persona_spoken_map,
        "intent": intent_section,
    }


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
    axis_section = _build_axis_section(catalog)
    static_section = _build_static_section(catalog)
    persona_section = _build_persona_section()
    hierarchy_section = _build_hierarchy_section()

    sections: dict[str, Any] = {
        "axes": axis_section,
        "static_prompts": static_section,
        "persona": persona_section,
        "hierarchy": hierarchy_section,
    }

    checksums = {name: _compute_checksum(content) for name, content in sections.items()}

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        **sections,
        "checksums": checksums,
    }
    return payload


__all__ = ["SCHEMA_VERSION", "prompt_grammar_payload"]
