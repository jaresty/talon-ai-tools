from __future__ import annotations

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
        "to analyst": "The audience for this is an analyst. Consider how best to visualize the result.",
        "to programmer": "The audience for this is a programmer.",
        "to LLM": "The audience for this is a large language model.",
        "to junior engineer": "The audience for this is a junior engineer.",
        "to principal engineer": "The audience for this is a principal engineer.",
        "to Kent Beck": "The audience for this is Kent Beck.",
        "to CEO": "The audience for this is a Chief Executive Officer.",
        "to platform team": "The audience for this is a platform team.",
        "to stream aligned team": "The audience for this is a stream-aligned team.",
        "to XP enthusiast": "The audience for this is an XP enthusiast. They care about early validation with working software in production, small batches, social programming (pairing and mobbing), and balanced, swarm-capable teams of generalists.",
    },
    "tone": {
        "casually": "Use a casual tone and include appropriate emoji.",
        "formally": "Use a formal tone.",
        "directly": "Use a direct tone.",
        "gently": "Use a gentle tone.",
        "kindly": "Use a kind tone.",
    },
    "purpose": {
        "for information": "You are writing to provide information.",
        "for entertainment": "You are writing to entertain.",
        "for persuasion": "You are writing to persuade.",
        "for brainstorming": "You are writing to open up possibilities and explore multiple options.",
        "for deciding": "You are writing to help converge on a decision.",
        "for planning": "You are writing to plan.",
        "for evaluating": "You are evaluating something.",
        "for coaching": "You are coaching someone.",
        "for appreciation": "You are offering appreciation.",
        "for triage": "You are helping to triage. Any suggestions you make should be doable in a short timescale. Do not discuss the time required.",
        "for announcing": "When crafting this, remember the purpose is to create a clear, concise announcement that can be delivered by any appropriate speaker. Make explicit who the announcement is for, what is happening, when and where it occurs, and what actions (if any) the audience should take, without assuming a specific speaker identity or style.",
        "for walk through": "Frame your response as a clear walkthrough, step by step, focusing only on the high-level ideas so the audience gradually builds understanding.",
        "for collaborating": "Collaborate with me iteratively: give only the next-level skeleton (headings/bullets/brief stubs), no extra detail, and expand or finalize only when I explicitly request it.",
        "for teaching": "When creating teaching content, remember the purpose is to help me teach: use a Socratic style where appropriate by starting sections with guiding questions that lead the audience into the explanations.",
        "for project management": "I want to plan a project in a LEAN way.",
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
