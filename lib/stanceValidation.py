from __future__ import annotations

"""Shared stance command validation for `model suggest`.

This module centralises the logic for deciding whether a stance_command
string is actually sayable under the current Persona/Intent preset and
axis vocab. It is used by both the GPT suggestion parser and the
suggestions GUI.
"""

from .personaConfig import persona_docs_map, PERSONA_PRESETS, INTENT_PRESETS

VOICE_TOKENS: set[str] = set(persona_docs_map("voice").keys())
AUDIENCE_TOKENS: set[str] = set(persona_docs_map("audience").keys())
TONE_TOKENS: set[str] = set(persona_docs_map("tone").keys())
PURPOSE_TOKENS: set[str] = set(persona_docs_map("purpose").keys())

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
    - model write <persona_voice> <persona_audience> <persona_tone> <intent_purpose>
      where at least one known purpose token (for teaching/deciding/...) is present.
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
        # Require at least one known purpose token to appear verbatim in the
        # command (for example, 'for teaching', 'for collaborating').
        if not any(purpose in lower for purpose in PURPOSE_TOKENS):
            return False
        return True

    return False
