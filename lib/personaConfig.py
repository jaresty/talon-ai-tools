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
    },
    "purpose": {
        "for information": "The goal is to provide clear information.",
        "for entertainment": "The goal is to entertain the audience.",
        "for persuasion": "The goal is to persuade the audience toward a view or action.",
        "for brainstorming": "The goal is to explore possibilities and surface multiple options.",
        "for deciding": "The goal is to help converge on a decision.",
        "for planning": "The goal is to organise work into a plan or roadmap.",
        "for evaluating": "The goal is to assess something and form a judgment.",
        "for coaching": "The goal is to support someone's growth through guidance and feedback.",
        "for appreciation": "The goal is to express appreciation or thanks.",
        "for triage": "The goal is to quickly sort and prioritise issues or options.",
        "for announcing": "The goal is to share a clear, concise announcement with the chosen audience.",
        "for walk through": "The goal is to walk the audience through the topic so their understanding builds gradually.",
        "for collaborating": "The goal is to collaborate iteratively with the user on the outcome.",
        "for teaching": "The goal is to help the audience learn and understand the material.",
        "for project management": "The goal is to support project management and coordination decisions.",
    },
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
    purpose: str


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
        purpose="for teaching",
    ),
    IntentPreset(
        key="decide",
        label="Decide",
        purpose="for deciding",
    ),
    IntentPreset(
        key="plan",
        label="Plan / organise",
        purpose="for planning",
    ),
    IntentPreset(
        key="evaluate",
        label="Evaluate / review",
        purpose="for evaluating",
    ),
    IntentPreset(
        key="brainstorm",
        label="Brainstorm",
        purpose="for brainstorming",
    ),
    IntentPreset(
        key="appreciate",
        label="Appreciate / thank",
        purpose="for appreciation",
    ),
    IntentPreset(
        key="persuade",
        label="Persuade",
        purpose="for persuasion",
    ),
    IntentPreset(
        key="coach",
        label="Coach",
        purpose="for coaching",
    ),
    IntentPreset(
        key="collaborate",
        label="Collaborate",
        purpose="for collaborating",
    ),
    IntentPreset(
        key="entertain",
        label="Entertain",
        purpose="for entertainment",
    ),
)

INTENT_BUCKETS: dict[str, tuple[str, ...]] = {
    # Task/intellectual intents (ADR 048 split)
    "task": ("teach", "decide", "plan", "evaluate", "brainstorm"),
    # Relational/social intents (ADR 048 split)
    "relational": ("appreciate", "persuade", "coach", "collaborate", "entertain"),
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
