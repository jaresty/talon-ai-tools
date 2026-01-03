from __future__ import annotations

from typing import Union

from .historyLifecycle import (
    RequestDropReason,
    drop_reason_message,
    last_drop_reason,
    last_drop_reason_code,
)


def render_drop_reason(reason: Union[RequestDropReason, str]) -> str:
    """Return a rendered drop message, falling back to the canonical template."""

    dynamic_message = ""
    try:
        code = last_drop_reason_code()
        if code:
            code_key = str(code).strip()
            reason_key = str(reason or "").strip()
            if reason_key and code_key and code_key == reason_key:
                dynamic_message = last_drop_reason()
    except Exception:
        dynamic_message = ""
    if dynamic_message and dynamic_message.strip():
        return dynamic_message

    try:
        message = drop_reason_message(reason)  # type: ignore[arg-type]
    except Exception:
        message = ""
    if message and message.strip():
        return message

    reason_text = str(reason).strip() or "unknown"
    return f"GPT: Request blocked; reason={reason_text}."
