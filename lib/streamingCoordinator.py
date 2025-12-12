"""Streaming coordination façade for ADR-0045.

Provides a small, testable helper for accumulating streamed text and
recording completion/error state for a single request. This module does not
yet wrap `_send_request_streaming` directly; existing streaming flows remain
unchanged. Future slices can thread this façade through `modelHelpers`,
canvases, destinations, and logs as described in ADR-0045.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class StreamingRun:
    """In-memory accumulator for a single streaming response.

    This structure keeps streamed text chunks and high-level status flags in
    one place so tests can exercise streaming accumulation and error
    transitions without depending on UI or network layers.
    """

    request_id: str
    chunks: List[str] = field(default_factory=list)
    completed: bool = False
    errored: bool = False
    error_message: str = ""

    def on_chunk(self, text: str) -> None:
        """Append a streamed text chunk.

        Chunks received after an error are ignored; callers should record the
        first error and stop forwarding further chunks.
        """

        if self.errored:
            return
        if not text:
            return
        # Treat whitespace-only chunks as empty to avoid surprising spaces
        # when concatenating text for logs or canvases.
        text_str = str(text)
        if not text_str.strip():
            return
        self.chunks.append(text_str)

    def on_complete(self) -> None:
        """Mark the stream as successfully completed."""

        if self.errored:
            # Preserve the error state; completion after error is ignored.
            return
        self.completed = True

    def on_error(self, message: str) -> None:
        """Mark the stream as errored.

        The accumulated chunks are preserved so UIs or logs can still render
        partial output when appropriate.
        """

        self.errored = True
        self.error_message = str(message or "")
        self.completed = False

    @property
    def text(self) -> str:
        """Return the concatenated streamed text so far."""

        return "".join(self.chunks)

    def snapshot(self) -> Dict[str, Any]:
        """Return a serialisable snapshot of the streaming state.

        This intentionally mirrors the style of other ADR-0045 helpers that
        expose small, structured snapshots for downstream consumers.
        """

        return {
            "request_id": self.request_id,
            "text": self.text,
            "completed": self.completed,
            "errored": self.errored,
            "error_message": self.error_message,
        }


def new_streaming_run(request_id: str) -> StreamingRun:
    """Create a new `StreamingRun` for the given request id.

    This helper exists mainly for symmetry with other coordinator-style
    modules in this repo and to give tests a single entrypoint.
    """

    return StreamingRun(request_id=str(request_id))


def canvas_view_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a small, canvas-friendly view of a streaming snapshot.

    This helper does not depend on UI types. It provides a stable shape
    for response canvases and tests to consume `StreamingRun.snapshot()`
    output without depending on the full snapshot structure.
    """

    text = str(snapshot.get("text") or "")
    completed = bool(snapshot.get("completed"))
    errored = bool(snapshot.get("errored"))
    error_message = str(snapshot.get("error_message") or "")

    if errored:
        status = "errored"
    elif completed:
        status = "completed"
    else:
        status = "inflight"

    return {
        "text": text,
        "status": status,
        "error_message": error_message,
    }
