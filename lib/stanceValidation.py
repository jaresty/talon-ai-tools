from __future__ import annotations

"""Shared stance command validation for `model suggest`.

This module centralises the logic for deciding whether a stance_command
string is actually sayable under the current Persona/Intent preset and
axis vocab. It is used by both the GPT suggestion parser and the
suggestions GUI.
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
    (preset.label or preset.key).strip().lower()
    for preset in PERSONA_PRESETS
    if (preset.label or preset.key).strip()
}
_INTENT_PRESET_SPOKEN_SET: set[str] = {
    (preset.key or "").strip().lower()
    for preset in INTENT_PRESETS
    if (preset.key or "").strip()
}


def valid_stance_command(cmd: str) -> bool:
    """Return True if cmd is a sayable stance command.

    Allowed forms (case-insensitive, with optional whitespace):
    - model write <persona_voice> <persona_audience> <persona_tone> <intent>
      where at least one known intent token (for teaching/deciding/...) is present.
    - persona <personaPreset>
    - intent <intentPreset>
    - persona <personaPreset> · intent <intentPreset> (or the reverse order).
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
        name = lower[len("intent ") :].strip()
        return name in _INTENT_PRESET_SPOKEN_SET

    if lower.startswith("model write "):
        tail = lower[len("model write ") :].strip()
        if not tail:
            return False

        # Require at least one known intent token to appear verbatim in the
        # command (for example, 'for teaching', 'teach').
        if not (
            any(intent in lower for intent in INTENT_TOKENS)
            or any(intent in lower for intent in INTENT_SPOKEN_TOKENS)
        ):
            return False

        # Enforce that the tail can be composed entirely from known
        # Persona/Intent axis phrases. This is intentionally conservative: we
        # treat axis tokens as whole phrases (for example, "as teacher",
        # "to junior engineer", "kindly", "for teaching") and require that
        # they tile the tail without leftovers.
        remaining = tail
        seen_intent = False
        # Sort by length so longer multi-word phrases ("to junior engineer")
        # win over their substrings.
        axis_phrases = sorted(
            AXIS_TOKENS | INTENT_SPOKEN_TOKENS, key=len, reverse=True
        )
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
                    if phrase_l in INTENT_TOKENS or phrase_l in INTENT_SPOKEN_TOKENS:
                        seen_intent = True
                    remaining = stripped[len(phrase_l) :]
                    break
            if not matched:
                return False
        # At least one intent phrase must have been matched explicitly.
        return seen_intent

    return False
