from __future__ import annotations

from collections.abc import Mapping, Sequence

from .requestLog import (
    AxisSnapshot,
    axis_snapshot_from_axes as requestlog_axis_snapshot_from_axes,
    consume_gating_drop_stats as requestlog_consume_gating_drop_stats,
    gating_drop_source_stats as requestlog_gating_drop_source_stats,
    gating_drop_stats as requestlog_gating_drop_stats,
    history_validation_stats as requestlog_history_validation_stats,
    record_gating_drop as requestlog_record_gating_drop,
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


__all__ = [
    "axes_snapshot_from_axes",
    "history_axes_for",
    "record_gating_drop",
    "gating_drop_stats",
    "gating_drop_source_stats",
    "consume_gating_drop_stats",
    "history_validation_stats",
]
