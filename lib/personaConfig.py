from __future__ import annotations

import os
from dataclasses import dataclass
from types import MappingProxyType
from typing import Dict, Iterable, List, Mapping

# Persona and intent axis docs (token -> description), parallel to AXIS_KEY_TO_VALUE
# but kept separate from the core contract axes.
PERSONA_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "voice": {
        "as programmer": "Important: Adopt the stance and language of a programmer; explain and reason like an engineer.",
        "as prompt engineer": "Important: Adopt a prompt-engineer stance; design and refine prompts explicitly.",
        "as scientist": "Important: Speak as a scientist; emphasise evidence, hypotheses, and rigor.",
        "as writer": "Important: Speak as a writer; focus on narrative clarity and flow.",
        "as designer": "Important: Speak as a designer; foreground usability, interaction, and visual clarity.",
        "as teacher": "Important: Speak as a teacher; break things down and scaffold understanding.",
        "as facilitator": "Important: Speak as a facilitator; guide process, balance voices, and keep momentum.",
        "as PM": "Important: Speak as a product manager; focus on outcomes, scope, and stakeholders.",
        "as junior engineer": "Important: Speak as a junior engineer; show curiosity, ask clarifying questions, and be candid about uncertainty.",
        "as principal engineer": "Important: Speak as a principal engineer; bring systems thinking, trade-offs, and pragmatic guidance.",
        "as Kent Beck": "Important: Speak in Kent Beck's pragmatic, iterative style with an emphasis on tests and simplicity.",
    },
    "audience": {
        "to managers": "Important: Aim the answer at managers; highlight outcomes, risk, and staffing.",
        "to team": "Important: Aim the answer at your team; keep it actionable and collaborative.",
        "to stakeholders": "Important: Aim the answer at stakeholders; focus on impact, decisions, and clarity.",
        "to product manager": "Important: Aim the answer at a product manager; connect user value, scope, and trade-offs.",
        "to designer": "Important: Aim the answer at a designer; stress user experience, flows, and visual clarity.",
        "to analyst": "Important: Aim the answer at an analyst; provide structure, data framing, and ways to visualise results.",
        "to programmer": "Important: Aim the answer at a programmer; keep it technical, precise, and implementation-ready.",
        "to LLM": "Important: Aim the answer at a large language model; be explicit, unambiguous, and free of fluff.",
        "to junior engineer": "Important: Aim the answer at a junior engineer; explain clearly and include gentle guidance.",
        "to principal engineer": "Important: Aim the answer at a principal engineer; keep it concise, architectural, and assumption-light.",
        "to Kent Beck": "Important: Aim the answer at Kent Beck; keep it concrete, test-minded, and iterative.",
        "to CEO": "Important: Aim the answer at a CEO; surface business impact, risk, and crisp asks.",
        "to platform team": "Important: Aim the answer at a platform team; emphasise reliability, leverage, and paved-path fit.",
        "to stream aligned team": "Important: Aim the answer at a stream-aligned team; emphasise flow, delivery, and local ownership.",
        "to XP enthusiast": "Important: Aim the answer at an XP enthusiast; value small batches, social programming, and production validation.",
    },
    "tone": {
        "casually": "Important: Use a casual, conversational tone.",
        "formally": "Important: Use a formal, professional tone.",
        "directly": "Important: Be direct and straightforward while remaining respectful.",
        "gently": "Important: Keep the tone gentle and supportive.",
        "kindly": "Important: Use a kind, warm tone.",
    },
    "intent": {
        "inform": "Important: Aim to give the audience the information they need.",
        "entertain": "Important: Aim to entertain the audience.",
        "persuade": "Important: Aim to persuade toward a view or action.",
        "brainstorm": "Important: Aim to uncover possibilities and surface options to consider.",
        "decide": "Important: Aim to converge on a decision with rationale.",
        "plan": "Important: Aim to choose a course of action and what should happen next.",
        "evaluate": "Important: Aim to reach a justified judgment about quality or viability.",
        "coach": "Important: Aim to support someone's growth through guidance and feedback.",
        "appreciate": "Important: Aim to express appreciation or thanks.",
        "resolve": "Important: Aim to bring the problem or issue to a settled, resolved state.",
        "understand": "Important: Aim to absorb and understand the input before acting.",
        "trace": "Important: Aim to uncover how this subject came to be, why it looks this way now, and what should happen next.",
        "announce": "Important: Aim to share news or updates with the audience.",
        "teach": "Important: Aim to help the audience learn and understand the material.",
        "learn": "Important: Aim to deepen your own understanding; the outcome is knowledge, not necessarily a fix.",
    },
}

INTENT_SPOKEN_TO_CANONICAL: Dict[str, str] = {
    "for information": "inform",
    "for entertainment": "entertain",
    "for persuasion": "persuade",
    "for brainstorming": "brainstorm",
    "for deciding": "decide",
    "for planning": "plan",
    "for evaluating": "evaluate",
    "for coaching": "coach",
    "for appreciation": "appreciate",
    "for resolving": "resolve",
    "for understanding": "understand",
    "for tracing": "trace",
    "for announcing": "announce",
    "for teaching": "teach",
    "for learning": "learn",
}

INTENT_CANONICAL_TOKENS: set[str] = set(PERSONA_KEY_TO_VALUE["intent"].keys())
INTENT_CANONICAL_TO_SPOKEN: Dict[str, str] = {
    canonical: spoken for spoken, canonical in INTENT_SPOKEN_TO_CANONICAL.items()
}

ALLOWED_PERSONA_AXES = frozenset({"voice", "audience", "tone"})


def persona_key_to_value_map(axis: str) -> dict[str, str]:
    """Return the key->description map for a persona/intent axis."""
    return PERSONA_KEY_TO_VALUE.get(axis, {})


def persona_hydrate_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Hydrate persona/intent tokens to descriptions (or pass through)."""
    if not tokens:
        return []
    mapping = persona_key_to_value_map(axis)
    return [mapping.get(token, token) for token in tokens if token]


def persona_docs_map(axis: str) -> dict[str, str]:
    """Return a key->description map for UI/docs surfaces."""
    return persona_key_to_value_map(axis)


def persona_axis_tokens(axis: str) -> set[str]:
    """Return canonical persona/intent tokens for the requested axis."""

    key = str(axis or "").strip().lower()
    if not key:
        return set()
    mapping = PERSONA_KEY_TO_VALUE.get(key)
    if not mapping:
        return set()
    return {token for token in mapping.keys() if token}


def canonical_persona_token(axis: str, raw: str) -> str:
    """Return the canonical persona/intent token for ``raw`` or ``""`` if unknown."""

    if not raw:
        return ""
    key = str(axis or "").strip().lower()
    if not key:
        return ""
    token = str(raw).strip()
    if not token:
        return ""
    if key == "intent":
        token = normalize_intent_token(token)
    tokens = persona_axis_tokens(key)
    if not tokens:
        return ""
    lowered = {t.lower(): t for t in tokens}
    return lowered.get(token.lower(), "")


def normalize_intent_token(value: str) -> str:
    """Normalize spoken or canonical intent tokens to the canonical single-word form."""
    token = str(value or "").strip()
    if not token:
        return ""
    token_l = token.lower()
    for key in INTENT_CANONICAL_TOKENS:
        if token_l == key.lower():
            return key
    for spoken, canonical in INTENT_SPOKEN_TO_CANONICAL.items():
        if token_l == spoken.lower():
            return canonical
    return token


def intent_bucket_spoken_tokens() -> dict[str, list[str]]:
    """Return intent buckets with spoken tokens (for <...>) covering all canonical intents."""
    spoken_buckets: dict[str, list[str]] = {}
    # Invert spoken map to prefer the first spoken form for each canonical token.
    for bucket, members in INTENT_BUCKETS.items():
        bucket_spoken: list[str] = []
        for canonical in members:
            spoken = INTENT_CANONICAL_TO_SPOKEN.get(canonical)
            bucket_spoken.append(spoken or canonical)
        spoken_buckets[bucket] = bucket_spoken
    return spoken_buckets


@dataclass(frozen=True)
class PersonaPreset:
    key: str
    label: str
    spoken: str | None = None
    voice: str | None = None
    audience: str | None = None
    tone: str | None = None


@dataclass(frozen=True)
class IntentPreset:
    key: str
    label: str
    intent: str


PERSONA_PRESETS: tuple[PersonaPreset, ...] = (
    PersonaPreset(
        key="peer_engineer_explanation",
        label="Peer engineer explanation",
        spoken="peer",
        voice="as programmer",
        audience="to programmer",
    ),
    PersonaPreset(
        key="coach_junior",
        label="Coach junior",
        spoken="coach",
        voice="as teacher",
        audience="to junior engineer",
        tone="gently",
    ),
    PersonaPreset(
        key="teach_junior_dev",
        label="Teach junior dev",
        spoken="mentor",
        voice="as teacher",
        audience="to junior engineer",
        tone="kindly",
    ),
    PersonaPreset(
        key="stakeholder_facilitator",
        label="Stakeholder facilitator",
        spoken="stake",
        voice="as facilitator",
        audience="to stakeholders",
        tone="directly",
    ),
    PersonaPreset(
        key="designer_to_pm",
        label="Designer to PM",
        spoken="design",
        voice="as designer",
        audience="to product manager",
        tone="directly",
    ),
    PersonaPreset(
        key="product_manager_to_team",
        label="Product manager to team",
        spoken="pm",
        voice="as PM",
        audience="to team",
        tone="kindly",
    ),
    PersonaPreset(
        key="executive_brief",
        label="Executive brief",
        spoken="exec",
        voice="as programmer",
        audience="to CEO",
        tone="directly",
    ),
    PersonaPreset(
        key="scientist_to_analyst",
        label="Scientist to analyst",
        spoken="science",
        voice="as scientist",
        audience="to analyst",
        tone="formally",
    ),
    PersonaPreset(
        key="fun_mode",
        label="Fun mode",
        spoken="fun",
        tone="casually",
    ),
)


INTENT_PRESETS: tuple[IntentPreset, ...] = (
    IntentPreset(
        key="teach",
        label="Teach / explain",
        intent="teach",
    ),
    IntentPreset(
        key="decide",
        label="Decide",
        intent="decide",
    ),
    IntentPreset(
        key="plan",
        label="Plan / organise",
        intent="plan",
    ),
    IntentPreset(
        key="evaluate",
        label="Evaluate / review",
        intent="evaluate",
    ),
    IntentPreset(
        key="brainstorm",
        label="Brainstorm",
        intent="brainstorm",
    ),
    IntentPreset(
        key="appreciate",
        label="Appreciate / thank",
        intent="appreciate",
    ),
    IntentPreset(
        key="persuade",
        label="Persuade",
        intent="persuade",
    ),
    IntentPreset(
        key="coach",
        label="Coach",
        intent="coach",
    ),
    IntentPreset(
        key="entertain",
        label="Entertain",
        intent="entertain",
    ),
    IntentPreset(
        key="resolve",
        label="Resolve",
        intent="resolve",
    ),
    IntentPreset(
        key="understand",
        label="Understand",
        intent="understand",
    ),
    IntentPreset(
        key="trace",
        label="Trace origins",
        intent="trace",
    ),
    IntentPreset(
        key="inform",
        label="Inform",
        intent="inform",
    ),
    IntentPreset(
        key="announce",
        label="Announce",
        intent="announce",
    ),
    IntentPreset(
        key="learn",
        label="Learn",
        intent="learn",
    ),
)


INTENT_BUCKETS: dict[str, tuple[str, ...]] = {
    "task": (
        "inform",
        "brainstorm",
        "decide",
        "plan",
        "evaluate",
        "resolve",
        "understand",
        "trace",
        "announce",
        "teach",
        "learn",
    ),
    "relational": ("appreciate", "persuade", "coach", "entertain"),
}


def intent_bucket_presets() -> dict[str, list[str]]:
    """Return intent preset keys grouped into task/relational buckets."""

    preset_keys = [preset.key for preset in INTENT_PRESETS if preset.key]
    buckets: dict[str, list[str]] = {}
    for bucket, members in INTENT_BUCKETS.items():
        filtered = [m for m in members if m in preset_keys]
        if filtered:
            buckets[bucket] = filtered
    return buckets


def _persona_spoken_map_from_presets(
    presets: Dict[str, PersonaPreset],
) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for key, preset in presets.items():
        key_l = (key or "").strip().lower()
        if key_l:
            mapping.setdefault(key_l, key)
        spoken = (preset.spoken or "").strip().lower()
        if spoken:
            mapping.setdefault(spoken, key)
        label = (preset.label or "").strip().lower()
        if label:
            mapping.setdefault(label, key)
    return mapping


def _intent_spoken_map() -> Dict[str, str]:
    mapping = {
        spoken.lower(): canonical
        for spoken, canonical in INTENT_SPOKEN_TO_CANONICAL.items()
    }
    for canonical in INTENT_CANONICAL_TOKENS:
        canonical_l = canonical.lower()
        mapping.setdefault(canonical_l, canonical)
    return mapping


@dataclass(frozen=True)
class PersonaIntentCatalogSnapshot:
    persona_presets: Dict[str, PersonaPreset]
    persona_spoken_map: Dict[str, str]
    persona_axis_tokens: Dict[str, List[str]]
    intent_presets: Dict[str, IntentPreset]
    intent_spoken_map: Dict[str, str]
    intent_axis_tokens: Dict[str, List[str]]
    intent_buckets: Dict[str, List[str]]
    intent_display_map: Dict[str, str]


@dataclass(frozen=True)
class PersonaIntentMaps:
    persona_axis_tokens: Mapping[str, Mapping[str, str]]
    intent_synonyms: Mapping[str, str]
    persona_presets: Mapping[str, PersonaPreset]
    persona_preset_aliases: Mapping[str, str]
    intent_presets: Mapping[str, IntentPreset]
    intent_preset_aliases: Mapping[str, str]
    intent_display_map: Mapping[str, str]


_PERSONA_INTENT_MAPS_CACHE: PersonaIntentMaps | None = None


def _build_persona_intent_maps_from_snapshot(
    snapshot: PersonaIntentCatalogSnapshot,
) -> PersonaIntentMaps:
    persona_axis_map: Dict[str, Mapping[str, str]] = {}
    for axis_key, tokens in (snapshot.persona_axis_tokens or {}).items():
        axis_lower = (axis_key or "").strip().lower()
        if not axis_lower:
            continue
        mapping: Dict[str, str] = {}
        for token in tokens or []:
            token_str = (token or "").strip()
            if token_str:
                mapping.setdefault(token_str.lower(), token_str)
        if mapping:
            persona_axis_map[axis_lower] = MappingProxyType(mapping)

    intent_axis_tokens = snapshot.intent_axis_tokens.get("intent", []) or []
    if intent_axis_tokens:
        intent_axis_map: Dict[str, str] = {}
        for token in intent_axis_tokens:
            token_str = (token or "").strip()
            if token_str:
                intent_axis_map.setdefault(token_str.lower(), token_str)
        if intent_axis_map:
            persona_axis_map["intent"] = MappingProxyType(intent_axis_map)

    persona_presets = MappingProxyType(dict(snapshot.persona_presets or {}))
    persona_aliases: Dict[str, str] = {}
    for alias, canonical in (snapshot.persona_spoken_map or {}).items():
        alias_str = (alias or "").strip().lower()
        canonical_str = (canonical or "").strip()
        if alias_str and canonical_str:
            persona_aliases.setdefault(alias_str, canonical_str)
    for key, preset in persona_presets.items():
        canonical_key = (key or "").strip()
        if not canonical_key:
            continue
        canonical_lower = canonical_key.lower()
        persona_aliases.setdefault(canonical_lower, canonical_key)
        spoken = (getattr(preset, "spoken", "") or "").strip()
        if spoken:
            persona_aliases.setdefault(spoken.lower(), canonical_key)
        label = (getattr(preset, "label", "") or "").strip()
        if label:
            persona_aliases.setdefault(label.lower(), canonical_key)

    persona_aliases_proxy = MappingProxyType(persona_aliases)

    intent_presets = MappingProxyType(dict(snapshot.intent_presets or {}))
    intent_aliases: Dict[str, str] = {}
    intent_synonyms: Dict[str, str] = {}
    for spoken, canonical in (snapshot.intent_spoken_map or {}).items():
        spoken_str = (spoken or "").strip().lower()
        canonical_str = (canonical or "").strip()
        if spoken_str and canonical_str:
            intent_synonyms.setdefault(spoken_str, canonical_str)
            intent_aliases.setdefault(spoken_str, canonical_str)
    for canonical, display in (snapshot.intent_display_map or {}).items():
        canonical_str = (canonical or "").strip()
        if not canonical_str:
            continue
        display_str = (display or "").strip()
        if display_str:
            intent_synonyms.setdefault(display_str.lower(), canonical_str)
            intent_aliases.setdefault(display_str.lower(), canonical_str)
        intent_synonyms.setdefault(canonical_str.lower(), canonical_str)
        intent_aliases.setdefault(canonical_str.lower(), canonical_str)
    for key, preset in intent_presets.items():
        canonical_key = (key or "").strip()
        if not canonical_key:
            continue
        intent_aliases.setdefault(canonical_key.lower(), canonical_key)
        label = (getattr(preset, "label", "") or "").strip()
        if label:
            intent_aliases.setdefault(label.lower(), canonical_key)
        intent_value = (getattr(preset, "intent", "") or "").strip()
        if intent_value:
            intent_aliases.setdefault(intent_value.lower(), canonical_key)

    return PersonaIntentMaps(
        persona_axis_tokens=MappingProxyType(persona_axis_map),
        intent_synonyms=MappingProxyType(intent_synonyms),
        persona_presets=persona_presets,
        persona_preset_aliases=persona_aliases_proxy,
        intent_presets=intent_presets,
        intent_preset_aliases=MappingProxyType(intent_aliases),
        intent_display_map=MappingProxyType(dict(snapshot.intent_display_map or {})),
    )


def _should_cache_persona_maps() -> bool:
    return not os.environ.get("PYTEST_CURRENT_TEST")


def persona_intent_maps(*, force_refresh: bool = False) -> PersonaIntentMaps:
    """Return cached persona/intent maps for callers that need alias lookups."""

    global _PERSONA_INTENT_MAPS_CACHE

    if not force_refresh and _should_cache_persona_maps():
        if _PERSONA_INTENT_MAPS_CACHE is not None:
            return _PERSONA_INTENT_MAPS_CACHE

    snapshot = persona_intent_catalog_snapshot()
    maps = _build_persona_intent_maps_from_snapshot(snapshot)

    if _should_cache_persona_maps() and not force_refresh:
        _PERSONA_INTENT_MAPS_CACHE = maps

    return maps


def persona_intent_maps_reset() -> None:
    """Clear any cached persona/intent maps."""

    global _PERSONA_INTENT_MAPS_CACHE
    _PERSONA_INTENT_MAPS_CACHE = None


def validate_persona_presets(
    presets: Iterable[PersonaPreset] | None = None,
) -> None:
    """Ensure persona presets use only Concordance-recognised persona axes."""

    presets_iterable = list(presets) if presets is not None else list(PERSONA_PRESETS)
    voice_tokens = persona_axis_tokens("voice")
    audience_tokens = persona_axis_tokens("audience")
    tone_tokens = persona_axis_tokens("tone")
    for preset in presets_iterable:
        invalid_axes: list[str] = []
        if preset.voice and preset.voice not in voice_tokens:
            invalid_axes.append(f"voice={preset.voice}")
        if preset.audience and preset.audience not in audience_tokens:
            invalid_axes.append(f"audience={preset.audience}")
        if preset.tone and preset.tone not in tone_tokens:
            invalid_axes.append(f"tone={preset.tone}")
        if invalid_axes:
            joined = ", ".join(invalid_axes)
            raise ValueError(
                f"Persona preset '{preset.key}' includes unsupported axis tokens: {joined}"
            )


def validate_intent_presets(
    presets: Iterable[IntentPreset] | None = None,
) -> None:
    """Ensure intent presets map to canonical intents."""

    presets_iterable = list(presets) if presets is not None else list(INTENT_PRESETS)
    allowed_intents = persona_axis_tokens("intent")
    for preset in presets_iterable:
        if preset.intent not in allowed_intents:
            raise ValueError(
                f"Intent preset '{preset.key}' references unsupported intent token: {preset.intent}"
            )


def persona_catalog() -> dict[str, PersonaPreset]:
    """Return a keyed persona preset catalog.

    This provides a single, typed view over PERSONA_PRESETS for GPT actions,
    help hub, suggestion GUIs, and docs to consume.
    """

    return {preset.key: preset for preset in PERSONA_PRESETS}


def intent_catalog() -> dict[str, IntentPreset]:
    """Return a keyed intent preset catalog.

    This aligns INTENT_PRESETS with the intent axis and bucket maps so callers
    can treat it as the canonical intent preset surface.
    """

    return {preset.key: preset for preset in INTENT_PRESETS}


def persona_intent_catalog_snapshot() -> PersonaIntentCatalogSnapshot:
    """Return a consolidated snapshot of persona/intent presets and axis metadata."""

    personas = persona_catalog()
    persona_spoken_map = _persona_spoken_map_from_presets(personas)
    persona_axes = {
        axis: sorted(persona_axis_tokens(axis))
        for axis in ("voice", "audience", "tone")
    }
    intents = intent_catalog()
    intent_spoken_map = _intent_spoken_map()
    intent_axes = {"intent": sorted(persona_axis_tokens("intent"))}
    raw_buckets = intent_bucket_presets()
    intent_buckets = {
        bucket: [key for key in keys if key in intents]
        for bucket, keys in raw_buckets.items()
    }
    intent_display_map = {
        canonical: INTENT_CANONICAL_TO_SPOKEN.get(canonical, canonical)
        for canonical in intents.keys()
    }
    return PersonaIntentCatalogSnapshot(
        persona_presets=personas,
        persona_spoken_map=persona_spoken_map,
        persona_axis_tokens=persona_axes,
        intent_presets=intents,
        intent_spoken_map=intent_spoken_map,
        intent_axis_tokens=intent_axes,
        intent_buckets=intent_buckets,
        intent_display_map=intent_display_map,
    )
