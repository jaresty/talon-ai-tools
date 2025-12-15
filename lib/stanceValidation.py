from __future__ import annotations

"""Shared stance command validation for `model suggest`.

This module centralises the logic for deciding whether a stance_command
string is actually sayable under the current Persona preset and axis
vocab. It is used by both the GPT suggestion parser and the suggestions
GUI.
"""

from .personaConfig import (
    INTENT_SPOKEN_TO_CANONICAL,
    persona_docs_map,
    PERSONA_PRESETS,
    INTENT_PRESETS,
)

VOICE_TOKENS: set[str] = set(persona_docs_map("voice").keys())
AUDIENCE_TOKENS: set[str] = set(persona_docs_map("audience").keys())
TONE_TOKENS: set[str] = set(persona_docs_map("tone").keys())
INTENT_TOKENS: set[str] = set(persona_docs_map("intent").keys())
# Spoken variants for intent tokens (Talon list keys).
INTENT_SPOKEN_TOKENS: set[str] = set(INTENT_SPOKEN_TO_CANONICAL.keys())
AXIS_TOKENS: set[str] = VOICE_TOKENS | AUDIENCE_TOKENS | TONE_TOKENS | INTENT_TOKENS

_PERSONA_PRESET_SPOKEN_SET: set[str] = {
    name
    for preset in PERSONA_PRESETS
    for name in {
        (preset.spoken or "").strip().lower(),
        (preset.label or "").strip().lower(),
        (preset.key or "").strip().lower(),
    }
    if name
}
_INTENT_PRESET_SPOKEN_SET: set[str] = {
    (preset.key or "").strip().lower()
    for preset in INTENT_PRESETS
    if (preset.key or "").strip()
}


def valid_stance_command(cmd: str) -> bool:
    """Return True if cmd is a sayable stance command.

    Allowed forms (case-insensitive, with optional whitespace):
    - model write <persona_voice> <persona_audience> <persona_tone>
      (intent is set via the separate `intent <token>` command, not here).
    - persona <personaPreset>
    - persona <personaPreset> · persona <personaPreset> (or other persona-only
      combinations using presets).
    """
    if not cmd:
        return False
    text = (cmd or "").strip()
    lower = text.lower()

    # Combined persona/intent separated by '·'
    parts = [p.strip() for p in lower.split("·") if p.strip()]
    if len(parts) > 1:
        # All parts must validate individually.
        return all(valid_stance_command(p) for p in parts)

    # Single-part commands.
    if lower.startswith("persona "):
        name = lower[len("persona ") :].strip()
        return name in _PERSONA_PRESET_SPOKEN_SET

    if lower.startswith("intent "):
        return False

    if lower.startswith("model write "):
        tail = lower[len("model write ") :].strip()
        if not tail:
            return False

        # Enforce that the tail can be composed entirely from known Persona
        # axis phrases, and that there is at least one Persona axis
        # (voice/audience/tone) token. Intent tokens are not allowed here;
        # intent is set via the separate `intent <token>` command.
        remaining = tail
        seen_persona_axis = False
        # Sort by length so longer multi-word phrases ("to junior engineer")
        # win over their substrings.
        axis_phrases = sorted(VOICE_TOKENS | AUDIENCE_TOKENS | TONE_TOKENS, key=len, reverse=True)
        while remaining:
            stripped = remaining.lstrip()
            if not stripped:
                break
            matched = False
            for phrase in axis_phrases:
                phrase_l = phrase.strip().lower()
                if not phrase_l:
                    continue
                if stripped.startswith(phrase_l):
                    matched = True
                    if phrase_l in VOICE_TOKENS or phrase_l in AUDIENCE_TOKENS or phrase_l in TONE_TOKENS:
                        seen_persona_axis = True
                    remaining = stripped[len(phrase_l) :]
                    break
            if not matched:
                return False
        # At least one Persona axis token is required; intent-only tails are not valid.
        return seen_persona_axis

    return False
