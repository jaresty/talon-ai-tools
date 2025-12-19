"""Streaming coordination façade for ADR-0045.

Provides a small, testable helper for accumulating streamed text and
recording completion/error state for a single request. `_send_request_streaming`
uses this façade as its in-memory accumulator, and UI surfaces (for example,
the response canvas) can consume snapshots via `canvas_view_from_snapshot`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple, cast

from .axisCatalog import axis_catalog
from .requestLog import append_entry_from_request

GATING_SNAPSHOT_KEYS = (
    "gating_drop_counts",
    "gating_drop_counts_sorted",
    "gating_drop_total",
    "gating_drop_last",
)


def _coerce_int(value: Any) -> Optional[int]:
    try:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            return int(stripped)
    except Exception:
        return None
    return None


def _sorted_counts(items: Dict[str, int]) -> List[Tuple[str, int]]:
    return sorted(items.items(), key=lambda pair: (-pair[1], pair[0]))


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
    gating_drop_counts: Dict[str, int] = field(default_factory=dict)

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

            setattr(GPTState, "last_streaming_events", list(self.events))
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

    def record_gating_drop(
        self, *, reason: str, phase: str = "", source: str = ""
    ) -> None:
        """Record that a gating drop occurred for the active request."""

        reason_value = str(reason or "")
        payload: Dict[str, Any] = {
            "reason": reason_value,
            "phase": str(phase or ""),
        }
        source_value = str(source or "")
        if source_value:
            payload["source"] = source_value

        reason_key = reason_value or ""
        current = self.gating_drop_counts.get(reason_key, 0) + 1
        self.gating_drop_counts[reason_key] = current
        total = sum(self.gating_drop_counts.values())
        payload["reason_count"] = current
        payload["total_count"] = total
        payload["counts"] = dict(self.gating_drop_counts)

        self._record_event("gating_drop", **payload)

        snapshot_extra = {
            "gating_drop_counts": dict(self.gating_drop_counts),
            "gating_drop_total": total,
            "gating_drop_last": {"reason": reason_key, "reason_count": current},
        }
        record_streaming_snapshot(self.run, extra=snapshot_extra)

    def record_log_entry(self, **kwargs: Any) -> str:
        """Record a request-history entry and emit streaming events.

        This is a "real" integration hook off the streaming event stream.
        Callers can route history/log writes through the session so ordering and
        drop outcomes remain observable in tests.
        """

        payload = dict(kwargs)
        answer_text = str(payload.get("answer_text") or "")
        meta_text = str(payload.get("meta_text") or "")
        axes = payload.get("axes")
        axes_keys = sorted(list(axes.keys())) if isinstance(axes, dict) else []
        # Legacy callers may still pass require_directional; drop it now that
        # the runtime enforces directional lenses unconditionally.
        payload.pop("require_directional", None)

        self._record_event(
            "history_write_requested",
            answer_len=len(answer_text),
            meta_len=len(meta_text),
            axes_keys=axes_keys,
        )
        prompt_text = append_entry_from_request(**payload)
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

        setattr(GPTState, "last_streaming_events", [])
        setattr(GPTState, "last_streaming_session", session)
        setattr(GPTState, "last_streaming_snapshot", {})
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


def current_streaming_gating_summary() -> Dict[str, Any]:
    """Return the aggregated gating-drop summary for the active streaming run."""

    snapshot = cast(Dict[str, Any], current_streaming_snapshot())
    counts_raw = snapshot.get("gating_drop_counts")
    counts: Dict[str, int] = {}
    if isinstance(counts_raw, dict):
        for reason, value in counts_raw.items():
            coerced = _coerce_int(value)
            if coerced is None or coerced < 0:
                continue
            counts[str(reason)] = coerced

    total_raw = snapshot.get("gating_drop_total")
    total = _coerce_int(total_raw)
    if total is None or total < 0:
        total = sum(counts.values())

    counts_sorted_raw = snapshot.get("gating_drop_counts_sorted")
    ordered: List[Tuple[str, int]] = []
    if isinstance(counts_sorted_raw, list) and counts_sorted_raw:
        for item in counts_sorted_raw:
            if not isinstance(item, dict):
                continue
            reason = item.get("reason")
            count_value = _coerce_int(item.get("count"))
            if not isinstance(reason, str) or not reason:
                continue
            if count_value is None or count_value < 0:
                continue
            ordered.append((reason, count_value))
            counts.setdefault(reason, count_value)
    elif counts:
        ordered = _sorted_counts(counts)

    last_raw = snapshot.get("gating_drop_last")
    last: Dict[str, Any] = {}
    if isinstance(last_raw, dict):
        reason = str(last_raw.get("reason") or "")
        reason_count_value = last_raw.get("reason_count")
        reason_count = _coerce_int(reason_count_value)
        if reason_count is None and reason:
            reason_count = counts.get(reason, 0)
        if reason or (reason_count or 0):
            last = {
                "reason": reason,
                "reason_count": reason_count or 0,
            }

    counts_sorted = [{"reason": reason, "count": count} for reason, count in ordered]

    return {
        "total": total,
        "counts": counts,
        "counts_sorted": counts_sorted,
        "last": last,
    }


def record_streaming_snapshot(
    run: StreamingRun, *, extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Persist the current streaming snapshot to GPTState and return it."""

    base_snapshot = run.snapshot()
    snapshot = dict(base_snapshot)

    try:
        from .modelState import GPTState
    except Exception:
        GPTState = None  # type: ignore[assignment]

    prior_snapshot: Dict[str, Any] = {}
    if GPTState is not None:
        try:
            prior_snapshot = cast(
                Dict[str, Any], getattr(GPTState, "last_streaming_snapshot", {}) or {}
            )
        except Exception:
            prior_snapshot = {}

    same_request = prior_snapshot.get("request_id") == snapshot.get("request_id")

    if extra:
        extra_dict = cast(Dict[str, Any], extra)
        extra_counts = extra_dict.get("gating_drop_counts")
        extra_total = extra_dict.get("gating_drop_total")
        extra_last = extra_dict.get("gating_drop_last")

        merged_counts: Dict[str, int] = {}
        prior_counts: Dict[str, Any] = {}
        if same_request:
            prior_counts_raw = prior_snapshot.get("gating_drop_counts", {}) or {}
            if isinstance(prior_counts_raw, dict):
                prior_counts = prior_counts_raw

        if isinstance(extra_counts, dict):
            if extra_total is not None:
                for reason, value in extra_counts.items():
                    coerced = _coerce_int(value)
                    if coerced is None:
                        continue
                    merged_counts[str(reason)] = coerced
                # Preserve prior reasons not present in the extra payload.
                for reason, value in prior_counts.items():
                    if str(reason) in merged_counts:
                        continue
                    coerced = _coerce_int(value)
                    if coerced is None:
                        continue
                    merged_counts[str(reason)] = coerced
            else:
                for reason, value in prior_counts.items():
                    coerced = _coerce_int(value)
                    if coerced is None:
                        continue
                    merged_counts[str(reason)] = coerced
                for reason, value in extra_counts.items():
                    coerced = _coerce_int(value)
                    if coerced is None:
                        continue
                    reason_key = str(reason)
                    merged_counts[reason_key] = (
                        merged_counts.get(reason_key, 0) + coerced
                    )
        elif same_request:
            for reason, value in prior_counts.items():
                coerced = _coerce_int(value)
                if coerced is None:
                    continue
                merged_counts[str(reason)] = coerced

        if merged_counts:
            snapshot["gating_drop_counts"] = merged_counts
            snapshot["gating_drop_counts_sorted"] = [
                {"reason": reason, "count": count}
                for reason, count in _sorted_counts(merged_counts)
            ]
            if extra_total is not None:
                coerced_total = _coerce_int(extra_total)
                snapshot["gating_drop_total"] = (
                    coerced_total
                    if coerced_total is not None
                    else sum(merged_counts.values())
                )
            else:
                snapshot["gating_drop_total"] = sum(merged_counts.values())
        elif same_request:
            # Preserve prior counts/total when no new counts arrived.
            if "gating_drop_counts" in prior_snapshot:
                snapshot["gating_drop_counts"] = dict(
                    prior_snapshot["gating_drop_counts"]
                )
            if "gating_drop_counts_sorted" in prior_snapshot:
                prior_sorted = prior_snapshot["gating_drop_counts_sorted"]
                if isinstance(prior_sorted, list):
                    snapshot["gating_drop_counts_sorted"] = list(prior_sorted)
            if "gating_drop_total" in prior_snapshot:
                snapshot["gating_drop_total"] = prior_snapshot["gating_drop_total"]

        if isinstance(extra_last, dict):
            snapshot["gating_drop_last"] = {
                "reason": str(extra_last.get("reason") or ""),
                "reason_count": _coerce_int(extra_last.get("reason_count"))
                or merged_counts.get(str(extra_last.get("reason") or ""), 0),
            }
        elif same_request and "gating_drop_last" in prior_snapshot:
            snapshot["gating_drop_last"] = prior_snapshot["gating_drop_last"]

        # Apply any remaining metadata outside the gating summary keys.
        for key, value in extra_dict.items():
            if key in GATING_SNAPSHOT_KEYS:
                continue
            snapshot[key] = value
    elif same_request:
        for key in GATING_SNAPSHOT_KEYS:
            if key in prior_snapshot and key not in snapshot:
                if key == "gating_drop_counts":
                    snapshot[key] = dict(prior_snapshot[key])
                elif key == "gating_drop_counts_sorted":
                    prior_sorted = prior_snapshot[key]
                    if isinstance(prior_sorted, list):
                        snapshot[key] = list(prior_sorted)
                else:
                    snapshot[key] = prior_snapshot[key]

    if "gating_drop_counts" not in snapshot:
        snapshot.pop("gating_drop_counts_sorted", None)

    if GPTState is not None:
        try:
            setattr(GPTState, "last_streaming_snapshot", snapshot)
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
