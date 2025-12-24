from __future__ import annotations

"""Shared stance command validation for `model suggest`.

This module centralises the logic for deciding whether a stance_command
string is actually sayable under the current Persona preset and axis
vocab. It is used by both the GPT suggestion parser and the suggestions
GUI.
"""

from .personaConfig import persona_docs_map


def _axis_tokens(axis: str) -> set[str]:
    """Return the latest persona/intent tokens for the given axis."""

    try:
        return set(persona_docs_map(axis).keys())
    except Exception:
        return set()


def _persona_presets():
    """Return the latest persona presets (reload-safe).

    Prefer the persona catalog when available so stance validation shares the
    same preset surface as GPT actions, Help Hub, and suggestion GUIs.
    """

    try:
        from . import personaConfig

        catalog = getattr(personaConfig, "persona_catalog", None)
        if callable(catalog):
            return tuple(catalog().values())
        return tuple(getattr(personaConfig, "PERSONA_PRESETS", ()))
    except Exception:
        return ()


def _intent_presets():
    """Return the latest intent presets (reload-safe).

    Prefer the intent catalog when available so stance validation stays aligned
    with the canonical IntentPreset set.
    """

    try:
        from . import personaConfig

        catalog = getattr(personaConfig, "intent_catalog", None)
        if callable(catalog):
            return tuple(catalog().values())
        return tuple(getattr(personaConfig, "INTENT_PRESETS", ()))
    except Exception:
        return ()


def _persona_preset_spoken_set() -> set[str]:
    """Return spoken tokens for persona presets."""

    spoken: set[str] = set()
    for preset in _persona_presets():
        for name in {
            (preset.spoken or "").strip().lower(),
            (preset.label or "").strip().lower(),
            (preset.key or "").strip().lower(),
        }:
            if name:
                spoken.add(name)
    return spoken


def _intent_preset_spoken_set() -> set[str]:
    """Return spoken tokens for intent presets."""

    spoken: set[str] = set()
    for preset in _intent_presets():
        key = (preset.key or "").strip().lower()
        if key:
            spoken.add(key)
    return spoken


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
        return name in _persona_preset_spoken_set()

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
        voice_tokens = _axis_tokens("voice")
        audience_tokens = _axis_tokens("audience")
        tone_tokens = _axis_tokens("tone")
        axis_phrases = sorted(
            voice_tokens | audience_tokens | tone_tokens, key=len, reverse=True
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
                    if (
                        phrase_l in voice_tokens
                        or phrase_l in audience_tokens
                        or phrase_l in tone_tokens
                    ):
                        seen_persona_axis = True
                    remaining = stripped[len(phrase_l) :]
                    break
            if not matched:
                return False
        # At least one Persona axis token is required; intent-only tails are not valid.
        return seen_persona_axis

    return False
