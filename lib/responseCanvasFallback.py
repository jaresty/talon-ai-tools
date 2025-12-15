"""Lightweight fallback for response canvas content during streaming."""

from __future__ import annotations

from typing import Optional


_FALLBACKS: dict[str, str] = {}
_MAX_FALLBACK_CHARS = 8000


def clear_response_fallback(request_id: Optional[str]) -> None:
    """Clear cached fallback text for a request."""
    if not request_id:
        return
    _FALLBACKS.pop(request_id, None)


def set_response_fallback(request_id: Optional[str], text: str) -> None:
    """Set or append fallback text for a request."""
    if not request_id or not text:
        return
    _FALLBACKS[request_id] = text


def append_response_fallback(request_id: Optional[str], chunk: str) -> None:
    """Append chunk text to a request’s fallback buffer."""
    if not request_id or not chunk:
        return
    existing = _FALLBACKS.get(request_id, "")
    combined = existing + chunk
    if len(combined) > _MAX_FALLBACK_CHARS:
        combined = combined[-_MAX_FALLBACK_CHARS :]
    _FALLBACKS[request_id] = combined


def fallback_for(request_id: Optional[str]) -> str:
    """Return cached fallback text for a request, or empty string."""
    if not request_id:
        return ""
    return _FALLBACKS.get(request_id, "")


def clear_all_fallbacks() -> None:
    """Clear all cached fallback buffers."""
    _FALLBACKS.clear()


__all__ = [
    "clear_response_fallback",
    "set_response_fallback",
    "append_response_fallback",
    "fallback_for",
    "clear_all_fallbacks",
]
