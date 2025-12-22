from __future__ import annotations

from typing import Union

from .requestLog import RequestDropReason, drop_reason_message


def render_drop_reason(reason: Union[RequestDropReason, str]) -> str:
    """Return a rendered drop message, falling back to the canonical template."""

    try:
        message = drop_reason_message(reason)  # type: ignore[arg-type]
    except Exception:
        message = ""
    if message and message.strip():
        return message
    reason_text = str(reason).strip() or "unknown"
    return f"GPT: Request blocked; reason={reason_text}."
