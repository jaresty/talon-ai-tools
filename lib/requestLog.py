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
    started_at_ms: Optional[int] = None,
    duration_ms: Optional[int] = None,
) -> None:
    """Append a request entry to the bounded history ring."""
    _history.append(
        RequestLogEntry(
            request_id=request_id,
            prompt=prompt,
            response=response,
            meta=meta,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
        )
    )


def latest() -> Optional[RequestLogEntry]:
    return _history.latest()


def nth_from_latest(offset: int) -> Optional[RequestLogEntry]:
    return _history.nth_from_latest(offset)


def all_entries():
    return _history.all()


def clear_history() -> None:
    while len(_history):
        _history._entries.popleft()  # type: ignore[attr-defined]


__all__ = ["append_entry", "latest", "nth_from_latest", "all_entries", "clear_history"]
