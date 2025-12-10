"""Global request history log utilities."""

from __future__ import annotations

from typing import Optional
from copy import deepcopy

from .requestHistory import RequestHistory, RequestLogEntry

_history = RequestHistory()


def append_entry(
    request_id: str,
    prompt: str,
    response: str,
    meta: str = "",
    recipe: str = "",
    started_at_ms: Optional[int] = None,
    duration_ms: Optional[int] = None,
    axes: Optional[dict[str, list[str]]] = None,
) -> None:
    """Append a request entry to the bounded history ring."""
    try:
        print(
            f"[requestLog] append id={request_id!r} prompt_len={len(prompt or '')} "
            f"response_len={len(response or '')} recipe={recipe!r} duration_ms={duration_ms} "
            f"axes_keys={list((axes or {}).keys())}"
        )
    except Exception:
        pass
    axes_payload = axes or {}
    _history.append(
        RequestLogEntry(
            request_id=request_id,
            prompt=prompt,
            response=response,
            meta=meta,
            recipe=recipe,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
            axes=axes_payload,
        )
    )
    try:
        latest_entry = _history.latest() if hasattr(_history, "latest") else None
        latest_id = latest_entry.request_id if latest_entry else "?"
        print(
            f"[requestLog] stored entries={len(_history)} latest_id={latest_id} hist_id={id(_history)}"
        )
    except Exception:
        pass


def append_entry_from_request(
    request_id: str,
    request: object | None,
    answer_text: str,
    meta_text: str = "",
    *,
    recipe: str = "",
    started_at_ms: Optional[int] = None,
    duration_ms: Optional[int] = None,
    axes: Optional[dict[str, list[str]]] = None,
) -> str:
    """Append a history entry derived from a request dict.

    This helper centralises the prompt/axes extraction semantics used when
    logging completed GPT requests so callers share a single contract for
    history entries.
    """

    prompt_text = ""
    try:
        request_dict = request or {}
        if isinstance(request_dict, dict):
            messages = request_dict.get("messages", [])
            user_messages = [
                m for m in messages if isinstance(m, dict) and m.get("role") == "user"
            ]
            if user_messages:
                parts: list[str] = []
                for item in user_messages[0].get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
                prompt_text = "\n\n".join(parts).strip()
    except Exception:
        prompt_text = ""

    axes_source = axes or {}
    try:
        axes_copy = deepcopy(axes_source)
    except Exception:
        axes_copy = dict(axes_source)

    append_entry(
        request_id,
        prompt_text,
        answer_text,
        meta_text,
        recipe=recipe,
        started_at_ms=started_at_ms,
        duration_ms=duration_ms,
        axes=axes_copy,
    )
    return prompt_text


def latest() -> Optional[RequestLogEntry]:
    return _history.latest()


def nth_from_latest(offset: int) -> Optional[RequestLogEntry]:
    return _history.nth_from_latest(offset)


def all_entries():
    try:
        entries = _history.all()
        print(f"[requestLog] all_entries len={len(entries)} hist_id={id(_history)}")
        return entries
    except Exception as e:
        try:
            print(f"[requestLog] all_entries failed: {e}")
        except Exception:
            pass
        return []


def clear_history() -> None:
    while len(_history):
        _history._entries.popleft()  # type: ignore[attr-defined]


__all__ = [
    "append_entry",
    "append_entry_from_request",
    "latest",
    "nth_from_latest",
    "all_entries",
    "clear_history",
]
