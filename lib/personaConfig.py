from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# Persona and intent axis docs (token -> description), parallel to AXIS_KEY_TO_VALUE
# but kept separate from the core contract axes.
PERSONA_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {
    "voice": {
        "as programmer": "Act as a programmer.",
        "as prompt engineer": "Act as a prompt engineer.",
        "as scientist": "Act as a scientist.",
        "as writer": "Act as a writer.",
        "as designer": "Act as a designer.",
        "as teacher": "Act as a teacher.",
        "as facilitator": "Act as a facilitator.",
        "as PM": "Act as a product manager.",
        "as junior engineer": "Act as a junior engineer.",
        "as principal engineer": "Act as a principal engineer.",
        "as Kent Beck": "Act as Kent Beck.",
    },
    "audience": {
        "to managers": "The audience for this is a group of managers.",
        "to team": "The audience for this is your team members.",
        "to stakeholders": "The audience for this is the stakeholders.",
        "to product manager": "The audience for this is a product manager.",
        "to designer": "The audience for this is a designer.",
        "to analyst": "The audience for this is an analyst. Prefer clear structure and, where helpful, concrete ways to visualise the result.",
        "to programmer": "The audience for this is a programmer.",
        "to LLM": "The audience for this is a large language model.",
        "to junior engineer": "The audience for this is a junior engineer.",
        "to principal engineer": "The audience for this is a principal engineer.",
        "to Kent Beck": "The audience for this is Kent Beck.",
        "to CEO": "The audience for this is a Chief Executive Officer.",
        "to platform team": "The audience for this is a platform team.",
        "to stream aligned team": "The audience for this is a stream-aligned team.",
        "to XP enthusiast": "The audience for this is an XP enthusiast. They value early validation with working software in production, small batches, social programming (pairing and mobbing), and balanced, swarm-capable teams of generalists.",
    },
    "tone": {
        "casually": "Use a casual, conversational tone.",
        "formally": "Use a formal tone.",
        "directly": "Use a direct, straightforward tone while remaining respectful.",
        "gently": "Use a gentle tone.",
        "kindly": "Use a kind, warm tone.",
        "plainly": "Use straightforward, everyday language with minimal ornamentation.",
        "tightly": "Be concise and dense; remove fluff and redundancy.",
        "headline first": "Lead with the main headline/point first, then layer brief supporting details.",
    },
    "intent": {
        "inform": "The goal is to provide clear information.",
        "entertain": "The goal is to entertain the audience.",
        "persuade": "The goal is to persuade the audience toward a view or action.",
        "brainstorm": "The goal is to explore possibilities and surface multiple options.",
        "decide": "The goal is to help converge on a decision.",
        "plan": "The goal is to organise work into a plan or roadmap.",
        "evaluate": "The goal is to assess something and form a judgment.",
        "coach": "The goal is to support someone's growth through guidance and feedback.",
        "appreciate": "The goal is to express appreciation or thanks.",
        "resolve": "The goal is to resolve a bug, problem, or issue.",
        "understand": "The goal is to understand or absorb the input (for example, a ticket or problem statement).",
        "announce": "The goal is to share a clear, concise announcement with the chosen audience.",
        "teach": "The goal is to help the audience learn and understand the material.",
        "learn": "The goal is to deepen understanding; the outcome is knowledge, not necessarily a fix.",
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
    "for announcing": "announce",
    "for teaching": "teach",
    "for learning": "learn",
}

INTENT_CANONICAL_TOKENS: set[str] = set(PERSONA_KEY_TO_VALUE["intent"].keys())
INTENT_CANONICAL_TO_SPOKEN: Dict[str, str] = {
    canonical: spoken for spoken, canonical in INTENT_SPOKEN_TO_CANONICAL.items()
}

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
    # Task/intellectual intents (ADR 048 split)
    "task": (
        "inform",
        "brainstorm",
        "decide",
        "plan",
        "evaluate",
        "resolve",
        "understand",
        "announce",
        "teach",
        "learn",
    ),
    # Relational/social intents (ADR 048 split)
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
