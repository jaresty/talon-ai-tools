from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, Mapping, Tuple

from .personaConfig import (
    IntentPreset,
    PersonaIntentCatalogSnapshot,
    PersonaIntentMaps,
    PersonaPreset,
    persona_intent_catalog_snapshot,
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
        if axis:
            tokens[axis] = tuple(sorted({v for v in values if v}))
    for axis, values in (snapshot.intent_axis_tokens or {}).items():
        if axis:
            tokens[axis] = tuple(sorted({v for v in values if v}))
    return MappingProxyType(tokens)


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


@dataclass(frozen=True)
class PersonaIntentOrchestrator:
    persona_presets: Mapping[str, PersonaPreset]
    intent_presets: Mapping[str, IntentPreset]
    persona_aliases: Mapping[str, str]
    intent_aliases: Mapping[str, str]
    intent_display_map: Mapping[str, str]
    axis_tokens: Mapping[str, Tuple[str, ...]]

    @classmethod
    def build(cls, *, force_refresh: bool = False) -> "PersonaIntentOrchestrator":
        snapshot = persona_intent_catalog_snapshot()
        maps = persona_intent_maps(force_refresh=force_refresh)
        persona_presets = MappingProxyType(dict(snapshot.persona_presets or {}))
        intent_presets = MappingProxyType(dict(snapshot.intent_presets or {}))
        intent_display_map = MappingProxyType(dict(snapshot.intent_display_map or {}))
        axis_tokens = _build_axis_tokens(snapshot)
        persona_aliases = _build_persona_aliases(maps)
        intent_aliases = _build_intent_aliases(maps, snapshot)
        return cls(
            persona_presets=persona_presets,
            intent_presets=intent_presets,
            persona_aliases=persona_aliases,
            intent_aliases=intent_aliases,
            intent_display_map=intent_display_map,
            axis_tokens=axis_tokens,
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
