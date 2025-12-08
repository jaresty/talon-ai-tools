"""Bounded, in-memory request history ring.

Keeps recent requests with prompt/response/meta snapshots without touching
GPTState. Intended to power the request log drawer and back/forward recall.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Deque, Iterable, List, Optional


@dataclass(frozen=True)
class RequestLogEntry:
    request_id: str
    prompt: str
    response: str
    meta: str = ""
    started_at_ms: Optional[int] = None
    duration_ms: Optional[int] = None


class RequestHistory:
    """Fixed-size ring buffer of request entries."""

    def __init__(self, max_entries: int = 20):
        self._max = max_entries
        self._entries: Deque[RequestLogEntry] = deque(maxlen=max_entries)

    def append(self, entry: RequestLogEntry) -> None:
        """Add a new entry, evicting the oldest when at capacity."""
        self._entries.append(entry)

    def latest(self) -> Optional[RequestLogEntry]:
        """Return the most recent entry, if any."""
        if not self._entries:
            return None
        return self._entries[-1]

    def nth_from_latest(self, offset: int) -> Optional[RequestLogEntry]:
        """Return the entry offset steps back from the latest (offset=0 is latest)."""
        if offset < 0:
            return None
        if offset >= len(self._entries):
            return None
        # deque does not support reversed index directly; convert to list once.
        return list(self._entries)[-(offset + 1)]

    def all(self) -> List[RequestLogEntry]:
        """Return a copy of all entries from oldest to newest."""
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


__all__ = ["RequestLogEntry", "RequestHistory"]
