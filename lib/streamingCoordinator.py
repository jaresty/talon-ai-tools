"""Streaming coordination façade for ADR-0045.

Provides a small, testable helper for accumulating streamed text and
recording completion/error state for a single request. `_send_request_streaming`
uses this façade as its in-memory accumulator, and UI surfaces (for example,
the response canvas) can consume snapshots via `canvas_view_from_snapshot`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .axisCatalog import axis_catalog
from .requestLog import append_entry_from_request


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
    axes: Dict[str, List[str]] = field(default_factory=dict)

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
            "axes": dict(self.axes),
        }


def filtered_axes_from_request(request: Dict[str, Any]) -> Dict[str, List[str]]:
    """Return catalog-backed axis tokens for a request payload.

    Keep this logic co-located with the streaming accumulator so callers can
    adopt a single contract for "which axes are attached to a streaming run".

    Behaviour is intentionally conservative:
    - Only known axis keys are included.
    - Only tokens present in the axis catalog are retained.
    - Empty/unknown tokens are dropped.
    """

    axes = (request or {}).get("axes") or {}
    if not isinstance(axes, dict):
        return {}

    try:
        catalog = axis_catalog()
        axes_map = catalog.get("axes", {}) or {}
    except Exception:
        axes_map = {}

    filtered: Dict[str, List[str]] = {}
    for axis in (
        "completeness",
        "scope",
        "method",
        "form",
        "channel",
        "directional",
    ):
        vals = axes.get(axis) or []
        if isinstance(vals, list):
            tokens = [str(v) for v in vals if str(v)]
        else:
            tokens = [str(vals)] if vals else []
        known = set((axes_map.get(axis) or {}).keys())
        kept = [t for t in tokens if t in known]
        if kept:
            filtered[axis] = kept

    return filtered


@dataclass
class StreamingSession:
    """Thin façade over `StreamingRun` with record helpers.

    ADR-0056 sketches a `StreamingSession` as an orchestrated surface that owns
    chunk accumulation and snapshot recording. This implementation is
    intentionally minimal: it wraps the existing `StreamingRun` and delegates to
    the `record_streaming_*` helpers so call sites can migrate incrementally.

    The session also records a small, ordered event stream for tests and future
    integrations (history/log/UI hooks).
    """

    run: StreamingRun
    events: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def request_id(self) -> str:
        return self.run.request_id

    @property
    def text(self) -> str:
        return self.run.text

    def _record_event(self, kind: str, **payload: Any) -> None:
        event = {"kind": kind, "request_id": self.request_id}
        event.update(payload)
        self.events.append(event)
        try:
            from .modelState import GPTState

            GPTState.last_streaming_events = list(self.events)
        except Exception:
            pass

    def record_snapshot(self) -> Dict[str, Any]:
        self._record_event("snapshot")
        return record_streaming_snapshot(self.run)

    def record_chunk(self, text: str) -> Dict[str, Any]:
        self._record_event("chunk", chunk_len=len(str(text or "")))
        return record_streaming_chunk(self.run, text)

    def record_error(self, message: str) -> Dict[str, Any]:
        self._record_event("error", message=str(message or ""))
        return record_streaming_error(self.run, message)

    def record_complete(self) -> Dict[str, Any]:
        self._record_event("complete")
        return record_streaming_complete(self.run)

    def record_log_entry(self, **kwargs: Any) -> str:
        """Record a request-history entry and emit streaming events.

        This is a "real" integration hook off the streaming event stream.
        Callers can route history/log writes through the session so ordering and
        drop outcomes remain observable in tests.
        """

        answer_text = str(kwargs.get("answer_text") or "")
        meta_text = str(kwargs.get("meta_text") or "")
        axes = kwargs.get("axes")
        axes_keys = sorted(list(axes.keys())) if isinstance(axes, dict) else []
        require_directional = bool(kwargs.get("require_directional", True))

        self._record_event(
            "history_write_requested",
            answer_len=len(answer_text),
            meta_len=len(meta_text),
            axes_keys=axes_keys,
            require_directional=require_directional,
        )
        prompt_text = append_entry_from_request(**kwargs)
        self._record_event("log_entry", prompt_len=len(str(prompt_text or "")))
        return prompt_text

    def record_history_saved(
        self, path: str, *, success: bool, error: str = ""
    ) -> None:
        """Record that a history source file was written.

        This is used by history-save actions (outside the streaming sender) so
        the streaming event stream can still capture the end-to-end lifecycle:
        request → response → history save.
        """

        self._record_event(
            "history_saved",
            path=str(path or ""),
            success=bool(success),
            error=str(error or ""),
        )

    def record_ui_refresh_requested(self, *, forced: bool, reason: str) -> None:
        """Record that a UI refresh was requested during streaming."""

        self._record_event(
            "ui_refresh_requested",
            forced=bool(forced),
            reason=str(reason or ""),
        )

    def record_ui_refresh_executed(
        self, *, forced: bool, reason: str, success: bool, error: str = ""
    ) -> None:
        """Record whether a UI refresh attempt executed successfully."""

        self._record_event(
            "ui_refresh_executed",
            forced=bool(forced),
            reason=str(reason or ""),
            success=bool(success),
            error=str(error or ""),
        )

    def cancel_requested(self, state: object, *, source: str, detail: str = "") -> bool:
        """Return True if cancel is requested, recording an event."""

        requested = False
        phase = ""
        try:
            requested = bool(getattr(state, "cancel_requested", False))
            phase = str(getattr(state, "phase", "") or "")
        except Exception:
            requested = False
        if requested:
            self._record_event(
                "cancel_requested",
                source=str(source or ""),
                phase=phase,
                detail=str(detail or ""),
            )
        return requested

    def record_cancel_executed(
        self, *, source: str, emitted: bool, error: str = ""
    ) -> None:
        """Record that cancel handling ran (cleanup/emit)."""

        self._record_event(
            "cancel_executed",
            source=str(source or ""),
            emitted=bool(emitted),
            error=str(error or ""),
        )

    def set_axes_from_request(self, request: Dict[str, Any]) -> None:
        """Best-effort attach catalog-backed axes to the streaming run."""

        try:
            self.run.axes = filtered_axes_from_request(request)
        except Exception:
            # Defensive: streaming should continue even if axis catalog access fails.
            self.run.axes = {}


def new_streaming_run(request_id: str) -> StreamingRun:
    """Create a new `StreamingRun` for the given request id.

    This helper exists mainly for symmetry with other coordinator-style
    modules in this repo and to give tests a single entrypoint.
    """

    return StreamingRun(request_id=str(request_id))


def new_streaming_session(request_id: str) -> StreamingSession:
    """Create a new `StreamingSession` for the given request id."""

    session = StreamingSession(run=new_streaming_run(request_id))
    try:
        from .modelState import GPTState

        GPTState.last_streaming_events = []
        GPTState.last_streaming_session = session
    except Exception:
        pass
    return session


def canvas_view_from_snapshot(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Return a small, canvas-friendly view of a streaming snapshot.

    This helper does not depend on UI types. It provides a stable shape
    for response canvases and tests to consume `StreamingRun.snapshot()`
    output without depending on the full snapshot structure.

    It also mirrors the confirmation/recap behaviour by stripping any
    trailing "Model interpretation" meta section from the text payload,
    so canvas consumers never briefly render meta inside the primary
    answer body while streaming.
    """

    from .modelHelpers import split_answer_and_meta

    raw_text = str(snapshot.get("text") or "")
    text, _meta = split_answer_and_meta(raw_text)
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


def current_streaming_snapshot() -> Dict[str, Any]:
    """Return the current GPTState streaming snapshot (if any) as a copy."""

    try:
        from .modelState import GPTState

        snap = getattr(GPTState, "last_streaming_snapshot", {}) or {}
        return dict(snap)
    except Exception:
        return {}


def record_streaming_snapshot(run: StreamingRun) -> Dict[str, Any]:
    """Persist the current streaming snapshot to GPTState and return it."""

    snapshot = run.snapshot()
    try:
        from .modelState import GPTState

        GPTState.last_streaming_snapshot = snapshot
    except Exception:
        pass
    return snapshot


def record_streaming_chunk(run: StreamingRun, text: str) -> Dict[str, Any]:
    """Append a chunk and persist the updated snapshot."""

    run.on_chunk(text)
    return record_streaming_snapshot(run)


def record_streaming_error(run: StreamingRun, message: str) -> Dict[str, Any]:
    """Mark error and persist the snapshot."""

    run.on_error(message)
    return record_streaming_snapshot(run)


def record_streaming_complete(run: StreamingRun) -> Dict[str, Any]:
    """Mark completion and persist the snapshot."""

    run.on_complete()
    return record_streaming_snapshot(run)
