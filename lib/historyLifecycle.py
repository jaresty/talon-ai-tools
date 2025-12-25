from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence

from .requestLog import (
    AxisSnapshot,
    DropReason,
    axis_snapshot_from_axes as requestlog_axis_snapshot_from_axes,
    consume_gating_drop_stats as requestlog_consume_gating_drop_stats,
    consume_last_drop_reason as requestlog_consume_last_drop_reason,
    consume_last_drop_reason_record as requestlog_consume_last_drop_reason_record,
    drop_reason_message as requestlog_drop_reason_message,
    gating_drop_source_stats as requestlog_gating_drop_source_stats,
    gating_drop_stats as requestlog_gating_drop_stats,
    history_validation_stats as requestlog_history_validation_stats,
    last_drop_reason as requestlog_last_drop_reason,
    record_gating_drop as requestlog_record_gating_drop,
    set_drop_reason as requestlog_set_drop_reason,
)
from .requestState import RequestDropReason

_HISTORY_AXIS_KEYS: tuple[str, ...] = (
    "completeness",
    "scope",
    "method",
    "form",
    "channel",
    "directional",
)


class HistoryAxisSnapshot:
    def __init__(self, snapshot: AxisSnapshot):
        self._snapshot = snapshot

    def as_dict(self) -> dict[str, list[str]]:
        return self._snapshot.as_dict()

    def to_dict(self) -> dict[str, list[str]]:
        return self._snapshot.as_dict()

    def known_axes(self) -> dict[str, list[str]]:
        return self._snapshot.known_axes()

    def get(self, key: str, default: list[str] | None = None) -> list[str] | None:
        return self._snapshot.get(key, default)

    def __contains__(self, key: object) -> bool:
        return key in self._snapshot

    def __iter__(self):
        return iter(self._snapshot)

    def __len__(self) -> int:
        return len(self._snapshot)


@dataclass(frozen=True)
class HistorySnapshotEntry:
    label: str
    prompt: str = ""
    response: str = ""
    meta: str = ""
    recipe: str = ""
    axes_snapshot: HistoryAxisSnapshot = field(
        default_factory=lambda: HistoryAxisSnapshot(AxisSnapshot({}))
    )
    axes: dict[str, list[str]] = field(default_factory=dict)
    provider_id: str = ""
    persona: dict[str, str] = field(default_factory=dict)
    request_id: str = ""
    path: str = ""
    created_at: datetime.datetime | None = None


def history_snapshot_entry_from(
    *,
    label: str,
    axes: Mapping[str, Sequence[str]] | None,
    persona: Mapping[str, str] | None = None,
    prompt: str = "",
    response: str = "",
    meta: str = "",
    recipe: str = "",
    provider_id: str = "",
    request_id: str = "",
    path: str = "",
    timestamp: datetime.datetime | None = None,
) -> HistorySnapshotEntry:
    snapshot = axes_snapshot_from_axes(axes)
    canonical_axes = {
        key: list(values) for key, values in snapshot.known_axes().items()
    }
    return HistorySnapshotEntry(
        label=label,
        prompt=prompt,
        response=response,
        meta=meta,
        recipe=recipe,
        axes_snapshot=HistoryAxisSnapshot(snapshot),
        axes=canonical_axes,
        provider_id=provider_id,
        persona=dict(persona or {}),
        request_id=request_id,
        path=path,
        created_at=timestamp,
    )


def coerce_history_snapshot_entry(entry: object) -> HistorySnapshotEntry:
    if isinstance(entry, HistorySnapshotEntry):
        return entry
    axes_payload = getattr(entry, "axes", {}) or {}
    snapshot = axes_snapshot_from_axes(axes_payload)
    canonical_axes = {
        key: list(values) for key, values in snapshot.known_axes().items()
    }
    persona_map = dict(getattr(entry, "persona", {}) or {})
    label = (
        getattr(entry, "label", "")
        or getattr(entry, "request_id", "")
        or "history-entry"
    )
    return HistorySnapshotEntry(
        label=label,
        prompt=(getattr(entry, "prompt", "") or ""),
        response=(getattr(entry, "response", "") or ""),
        meta=(getattr(entry, "meta", "") or ""),
        recipe=(getattr(entry, "recipe", "") or ""),
        axes_snapshot=HistoryAxisSnapshot(snapshot),
        axes=canonical_axes,
        provider_id=(getattr(entry, "provider_id", "") or ""),
        persona=persona_map,
        request_id=(getattr(entry, "request_id", "") or ""),
        path=(getattr(entry, "path", "") or ""),
        created_at=getattr(entry, "created_at", None),
    )


def _coerce_axes_mapping(
    axes: Mapping[str, Sequence[str]] | None,
) -> dict[str, list[str]]:
    if not axes:
        return {}
    return {
        key: [str(value).strip() for value in values] for key, values in axes.items()
    }


def axes_snapshot_from_axes(axes: Mapping[str, Sequence[str]] | None) -> AxisSnapshot:
    payload = _coerce_axes_mapping(axes)
    payload.pop("style", None)
    raw_snapshot = requestlog_axis_snapshot_from_axes(payload)
    dedup_axes: dict[str, list[str]] = {}
    for key in raw_snapshot.keys():
        values = list(raw_snapshot.get(key, []) or [])
        seen: set[str] = set()
        deduped: list[str] = []
        for value in values:
            if value not in seen:
                seen.add(value)
                deduped.append(value)
        if deduped:
            dedup_axes[key] = deduped
    return AxisSnapshot({key: tuple(values) for key, values in dedup_axes.items()})


def history_axes_for(axes: Mapping[str, Sequence[str]] | None) -> dict[str, list[str]]:
    snapshot = axes_snapshot_from_axes(axes)
    result: dict[str, list[str]] = {}
    for key in _HISTORY_AXIS_KEYS:
        sequence = snapshot.get(key, []) or []
        seen: set[str] = set()
        deduped: list[str] = []
        for value in sequence:
            if value not in seen:
                seen.add(value)
                deduped.append(value)
        result[key] = deduped
    return result


def record_gating_drop(reason: RequestDropReason, *, source: object = "") -> None:
    """Record a gating drop for lifecycle telemetry."""

    requestlog_record_gating_drop(reason, source=source)


def gating_drop_stats(*, reset: bool = False) -> dict[str, int]:
    """Return gating drop counts aggregated by reason."""

    return requestlog_gating_drop_stats(reset=reset)


def gating_drop_source_stats(*, reset: bool = False) -> dict[str, int]:
    """Return gating drop counts aggregated by source."""

    return requestlog_gating_drop_source_stats(reset=reset)


def consume_gating_drop_stats() -> dict[str, int]:
    """Return and clear accumulated gating drop statistics."""

    return requestlog_consume_gating_drop_stats()


def history_validation_stats() -> dict[str, object]:
    """Return lifecycle validation stats (history + gating telemetry)."""

    return requestlog_history_validation_stats()


def set_drop_reason(reason: RequestDropReason, message: str | None = None) -> None:
    """Set the last drop reason via the lifecycle façade."""

    requestlog_set_drop_reason(reason, message)


def last_drop_reason() -> str:
    """Return the most recent drop reason message."""

    return requestlog_last_drop_reason()


def consume_last_drop_reason() -> str:
    """Consume and clear the last drop reason message."""

    return requestlog_consume_last_drop_reason()


def consume_last_drop_reason_record() -> DropReason:
    """Consume and clear the structured drop reason record."""

    return requestlog_consume_last_drop_reason_record()


def drop_reason_message(reason: RequestDropReason) -> str:
    """Return the rendered message for a drop reason."""

    return requestlog_drop_reason_message(reason)


def clear_drop_reason() -> None:
    """Clear any cached drop reason (success path)."""

    requestlog_set_drop_reason("")


__all__ = [
    "HistoryAxisSnapshot",
    "HistorySnapshotEntry",
    "axes_snapshot_from_axes",
    "history_axes_for",
    "history_snapshot_entry_from",
    "coerce_history_snapshot_entry",
    "record_gating_drop",
    "gating_drop_stats",
    "gating_drop_source_stats",
    "consume_gating_drop_stats",
    "history_validation_stats",
    "set_drop_reason",
    "last_drop_reason",
    "consume_last_drop_reason",
    "consume_last_drop_reason_record",
    "drop_reason_message",
    "clear_drop_reason",
]
