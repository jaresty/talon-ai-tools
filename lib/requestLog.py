"""Global request history log utilities."""

from __future__ import annotations

from typing import Optional

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
) -> None:
    """Append a request entry to the bounded history ring."""
    try:
        print(
            f"[requestLog] append id={request_id!r} prompt_len={len(prompt or '')} "
            f"response_len={len(response or '')} recipe={recipe!r} duration_ms={duration_ms}"
        )
    except Exception:
        pass
    _history.append(
        RequestLogEntry(
            request_id=request_id,
            prompt=prompt,
            response=response,
            meta=meta,
            recipe=recipe,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
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


__all__ = ["append_entry", "latest", "nth_from_latest", "all_entries", "clear_history"]
