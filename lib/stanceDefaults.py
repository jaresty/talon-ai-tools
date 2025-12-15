"""Shared helpers for summarising stance and default axis settings."""

from __future__ import annotations

from typing import Dict, List, Optional

from talon import settings

from .modelState import GPTState
from .providerRegistry import provider_registry


def stance_defaults_lines(ctx: Optional[Dict[str, str]] = None) -> List[str]:
    """Return compact stance/default summaries.

    - `ctx` may contain per-request context (voice/audience/tone/intent and
      axis defaults) to override current settings.
    - Falls back to current system prompt and user model_default_* settings.
    """

    def _short(value: object) -> str:
        text = str(value or "").strip()
        return text or "–"

    def _setting(key: str) -> str:
        try:
            return _short(settings.get(key))
        except Exception:
            return "–"

    sys = getattr(GPTState, "system_prompt", None)
    voice = _short((ctx or {}).get("voice", getattr(sys, "voice", "")))
    audience = _short((ctx or {}).get("audience", getattr(sys, "audience", "")))
    tone = _short((ctx or {}).get("tone", getattr(sys, "tone", "")))
    intent = _short((ctx or {}).get("intent", getattr(sys, "intent", "")))

    def _axis_from_ctx_or_setting(key: str, setting_key: str) -> str:
        raw = (ctx or {}).get(key, "")
        return _short(raw) if raw else _setting(setting_key)

    try:
        provider = _short(provider_registry().current_provider_id())
    except Exception:
        provider = "–"
    stance_line = f"Stance: Voice={voice} Audience={audience} Tone={tone} Intent={intent}"
    defaults_line = (
        "Defaults: "
        f"C={_axis_from_ctx_or_setting('completeness', 'user.model_default_completeness')} "
        f"S={_axis_from_ctx_or_setting('scope', 'user.model_default_scope')} "
        f"M={_axis_from_ctx_or_setting('method', 'user.model_default_method')} "
        f"F={_axis_from_ctx_or_setting('form', 'user.model_default_form')} "
        f"Ch={_axis_from_ctx_or_setting('channel', 'user.model_default_channel')} "
        f"Provider={provider}"
    )
    return [stance_line, defaults_line]
