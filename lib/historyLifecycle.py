from __future__ import annotations

from collections.abc import Mapping, Sequence

from .requestLog import (
    AxisSnapshot,
    axis_snapshot_from_axes as requestlog_axis_snapshot_from_axes,
)

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


__all__ = ["axes_snapshot_from_axes", "history_axes_for"]
