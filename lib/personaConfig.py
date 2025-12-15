from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

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
        "plainly": "Important: Use straightforward, everyday language with minimal ornamentation.",
        "tightly": "Important: Be concise and dense; remove fluff and redundancy.",
        "headline first": "Important: Lead with the main headline or point first, then add brief supporting details.",
    },
    "intent": {
        "inform": "Important: Aim to inform clearly and accurately.",
        "entertain": "Important: Aim to entertain the audience.",
        "persuade": "Important: Aim to persuade toward a view or action.",
        "brainstorm": "Important: Aim to explore possibilities and surface multiple options.",
        "decide": "Important: Aim to converge on a decision with rationale.",
        "plan": "Important: Aim to organise work into a plan or roadmap.",
        "evaluate": "Important: Aim to assess and form a justified judgment.",
        "coach": "Important: Aim to support someone's growth through guidance and feedback.",
        "appreciate": "Important: Aim to express appreciation or thanks.",
        "resolve": "Important: Aim to resolve a bug, problem, or issue.",
        "understand": "Important: Aim to absorb and understand the input before acting.",
        "announce": "Important: Aim to deliver a clear, concise announcement for the audience.",
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
