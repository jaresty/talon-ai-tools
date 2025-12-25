from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, Mapping, Tuple

from .personaCatalog import get_persona_intent_catalog
from .personaConfig import (
    IntentPreset,
    PersonaIntentCatalogSnapshot,
    PersonaIntentMaps,
    PersonaPreset,
    persona_intent_maps,
)


def _normalise_alias(value: str | None) -> str:
    if not value:
        return ""
    return value.strip().lower()


def _build_axis_tokens(
    snapshot: PersonaIntentCatalogSnapshot,
) -> Mapping[str, Tuple[str, ...]]:
    tokens: Dict[str, Tuple[str, ...]] = {}
    for axis, values in (snapshot.persona_axis_tokens or {}).items():
        axis_key = (axis or "").strip().lower()
        if axis_key:
            tokens[axis_key] = tuple(sorted({v for v in values if v}))
    for axis, values in (snapshot.intent_axis_tokens or {}).items():
        axis_key = (axis or "").strip().lower()
        if axis_key:
            tokens[axis_key] = tuple(sorted({v for v in values if v}))
    return MappingProxyType(tokens)


def _build_axis_alias_map(maps: PersonaIntentMaps) -> Mapping[str, Mapping[str, str]]:
    axis_alias_map: Dict[str, Mapping[str, str]] = {}
    for axis, mapping in (maps.persona_axis_tokens or {}).items():
        axis_key = (axis or "").strip().lower()
        if not axis_key:
            continue
        entries: Dict[str, str] = {}
        for alias, token in dict(mapping).items():
            alias_key = (alias or "").strip().lower()
            canonical = (token or "").strip()
            if alias_key and canonical:
                entries.setdefault(alias_key, canonical)
        if entries:
            axis_alias_map[axis_key] = MappingProxyType(entries)
    return MappingProxyType(axis_alias_map)


def _build_persona_aliases(maps: PersonaIntentMaps) -> Mapping[str, str]:
    aliases: Dict[str, str] = {}
    for alias, key in (maps.persona_preset_aliases or {}).items():
        normalised = _normalise_alias(alias)
        canonical = (key or "").strip()
        if normalised and canonical:
            aliases.setdefault(normalised, canonical)
    for key in (maps.persona_presets or {}).keys():
        canonical = (key or "").strip()
        if canonical:
            aliases.setdefault(canonical.lower(), canonical)
    return MappingProxyType(aliases)


def _build_intent_aliases(
    maps: PersonaIntentMaps, snapshot: PersonaIntentCatalogSnapshot
) -> Mapping[str, str]:
    aliases: Dict[str, str] = {}
    for alias, key in (maps.intent_preset_aliases or {}).items():
        normalised = _normalise_alias(alias)
        canonical = (key or "").strip()
        if normalised and canonical:
            aliases.setdefault(normalised, canonical)
    for canonical, display in (snapshot.intent_display_map or {}).items():
        canonical_key = (canonical or "").strip()
        display_value = (display or "").strip()
        if canonical_key:
            aliases.setdefault(canonical_key.lower(), canonical_key)
        if canonical_key and display_value:
            aliases.setdefault(display_value.lower(), canonical_key)
    for preset in (snapshot.intent_presets or {}).values():
        canonical_key = (getattr(preset, "key", "") or "").strip()
        canonical_intent = (getattr(preset, "intent", "") or "").strip()
        label = (getattr(preset, "label", "") or "").strip()
        if canonical_key:
            aliases.setdefault(canonical_key.lower(), canonical_key)
        if canonical_intent:
            aliases.setdefault(
                canonical_intent.lower(), canonical_key or canonical_intent
            )
        if label:
            aliases.setdefault(label.lower(), canonical_key or canonical_intent)
    return MappingProxyType(aliases)


def _build_intent_synonyms(maps: PersonaIntentMaps) -> Mapping[str, str]:
    entries: Dict[str, str] = {}
    for alias, canonical in (maps.intent_synonyms or {}).items():
        alias_key = (alias or "").strip().lower()
        canonical_key = (canonical or "").strip()
        if alias_key and canonical_key:
            entries.setdefault(alias_key, canonical_key)
    return MappingProxyType(entries)


def _build_intent_display_map(
    snapshot: PersonaIntentCatalogSnapshot,
) -> Mapping[str, str]:
    return MappingProxyType(dict(snapshot.intent_display_map or {}))


@dataclass(frozen=True)
class PersonaIntentOrchestrator:
    persona_presets: Mapping[str, PersonaPreset]
    intent_presets: Mapping[str, IntentPreset]
    persona_aliases: Mapping[str, str]
    intent_aliases: Mapping[str, str]
    intent_display_map: Mapping[str, str]
    axis_tokens: Mapping[str, Tuple[str, ...]]
    axis_alias_map: Mapping[str, Mapping[str, str]]
    intent_synonyms: Mapping[str, str]

    @classmethod
    def build(cls, *, force_refresh: bool = False) -> "PersonaIntentOrchestrator":
        snapshot = get_persona_intent_catalog()
        maps = persona_intent_maps(force_refresh=force_refresh)
        persona_presets = MappingProxyType(dict(snapshot.persona_presets or {}))
        intent_presets = MappingProxyType(dict(snapshot.intent_presets or {}))
        intent_display_map = _build_intent_display_map(snapshot)
        axis_tokens = _build_axis_tokens(snapshot)
        axis_alias_map = _build_axis_alias_map(maps)
        persona_aliases = _build_persona_aliases(maps)
        intent_aliases = _build_intent_aliases(maps, snapshot)
        intent_synonyms = _build_intent_synonyms(maps)
        return cls(
            persona_presets=persona_presets,
            intent_presets=intent_presets,
            persona_aliases=persona_aliases,
            intent_aliases=intent_aliases,
            intent_display_map=intent_display_map,
            axis_tokens=axis_tokens,
            axis_alias_map=axis_alias_map,
            intent_synonyms=intent_synonyms,
        )

    def canonical_persona_key(self, alias: str | None) -> str:
        normalised = _normalise_alias(alias)
        if not normalised:
            return ""
        return self.persona_aliases.get(normalised, "")

    def canonical_intent_key(self, alias: str | None) -> str:
        normalised = _normalise_alias(alias)
        if not normalised:
            return ""
        canonical = self.intent_aliases.get(normalised, "")
        if canonical:
            return canonical
        synonym = self.intent_synonyms.get(normalised)
        if synonym:
            return synonym
        return ""

    def canonical_axis_token(self, axis: str, alias: str | None) -> str:
        axis_key = (axis or "").strip().lower()
        candidate = (alias or "").strip()
        if not axis_key or not candidate:
            return ""
        lowered = candidate.lower()
        alias_map = self.axis_alias_map.get(axis_key, {})
        if alias_map:
            canonical = alias_map.get(lowered)
            if canonical:
                return canonical
        tokens = self.axis_tokens.get(axis_key, ())
        for token in tokens:
            if token and token.lower() == lowered:
                return token
        return ""


_ORCHESTRATOR_CACHE: PersonaIntentOrchestrator | None = None


def get_persona_intent_orchestrator(
    *, force_refresh: bool = False
) -> PersonaIntentOrchestrator:
    global _ORCHESTRATOR_CACHE
    if force_refresh or _ORCHESTRATOR_CACHE is None:
        _ORCHESTRATOR_CACHE = PersonaIntentOrchestrator.build(
            force_refresh=force_refresh
        )
    return _ORCHESTRATOR_CACHE


def reset_persona_intent_orchestrator_cache() -> None:
    global _ORCHESTRATOR_CACHE
    _ORCHESTRATOR_CACHE = None
