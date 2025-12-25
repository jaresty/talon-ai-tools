from __future__ import annotations

from typing import Dict

from .personaConfig import (
    IntentPreset,
    PersonaIntentCatalogSnapshot,
    PersonaPreset,
    persona_intent_catalog_snapshot,
)


def get_persona_intent_catalog() -> PersonaIntentCatalogSnapshot:
    """Return the canonical persona/intent catalog snapshot."""

    return persona_intent_catalog_snapshot()


def get_persona_presets() -> Dict[str, PersonaPreset]:
    """Return persona presets keyed by identifier."""

    snapshot = get_persona_intent_catalog()
    return dict(snapshot.persona_presets)


def get_persona_spoken_map() -> Dict[str, str]:
    """Return spoken alias map for persona presets."""

    snapshot = get_persona_intent_catalog()
    return dict(snapshot.persona_spoken_map)


def get_intent_presets() -> Dict[str, IntentPreset]:
    """Return intent presets keyed by identifier."""

    snapshot = get_persona_intent_catalog()
    return dict(snapshot.intent_presets)


def get_intent_display_map() -> Dict[str, str]:
    """Return canonical intent display label mapping."""

    snapshot = get_persona_intent_catalog()
    return dict(snapshot.intent_display_map)
