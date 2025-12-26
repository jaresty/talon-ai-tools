from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from collections.abc import Mapping, Sequence
from typing import cast

from . import requestLog as requestlog_module
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
    latest as requestlog_latest,
    nth_from_latest as requestlog_nth_from_latest,
    record_gating_drop as requestlog_record_gating_drop,
    set_drop_reason as requestlog_set_drop_reason,
    all_entries as requestlog_all_entries,
    append_entry as requestlog_append_entry,
    append_entry_from_request as requestlog_append_entry_from_request,
    clear_history as requestlog_clear_history,
    validate_history_axes as requestlog_validate_history_axes,
    remediate_history_axes as requestlog_remediate_history_axes,
    _filter_axes_payload as requestlog_filter_axes_payload,
    KNOWN_AXIS_KEYS as requestlog_known_axis_keys,
)
from .requestState import (
    RequestDropReason,
    RequestEvent,
    RequestEventKind,
    RequestPhase,
    RequestState,
    Surface,
    lifecycle_status_for,
    transition,
)
from .requestLifecycle import (
    RequestLifecycleState,
    RequestStatus,
    is_in_flight as lifecycle_is_in_flight,
    reduce_request_state as lifecycle_reduce_request_state,
    try_start_request as lifecycle_try_start_request,
)

_HISTORY_AXIS_KEYS: tuple[str, ...] = (
    "completeness",
    "scope",
    "method",
    "form",
    "channel",
    "directional",
)

if isinstance(requestlog_known_axis_keys, tuple):
    KNOWN_AXIS_KEYS = requestlog_known_axis_keys
else:
    KNOWN_AXIS_KEYS = tuple(requestlog_known_axis_keys)


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


def persona_header_lines(entry: object) -> list[str]:
    from .suggestionCoordinator import recipe_header_lines_from_snapshot

    snapshot = getattr(entry, "persona", {}) or {}
    if not snapshot:
        return []
    try:
        lines = recipe_header_lines_from_snapshot(snapshot)
    except Exception:
        return []
    return [
        line
        for line in lines
        if line.startswith("persona_preset: ") or line.startswith("intent_preset: ")
    ]


def parse_persona_summary_line(line: str, prefix: str) -> tuple[str, list[str]]:
    body = line[len(prefix) :].strip()
    if not body:
        return "", []
    if body.endswith(")") and "(" in body:
        descriptor, detail = body.split("(", 1)
        descriptor = descriptor.strip()
        parts = [part.strip() for part in detail[:-1].split(";") if part.strip()]
        return descriptor, parts
    return body, []


def _render_persona_summary(line: str) -> str:
    descriptor, parts = parse_persona_summary_line(line, "persona_preset: ")
    spoken = ""
    label = ""
    others: list[str] = []
    for part in parts:
        lower = part.lower()
        if lower.startswith("say: persona "):
            spoken = part[len("say: persona ") :].strip()
            continue
        if lower.startswith("label="):
            label = part.split("=", 1)[1].strip()
            continue
        others.append(part)
    display = spoken or label or descriptor or "persona"
    details: list[str] = []
    if descriptor and descriptor != display:
        details.append(f"key={descriptor}")
    if label and label != display:
        details.append(f"label={label}")
    if spoken:
        details.append(f"say: persona {spoken}")
    details.extend(others)
    fragment = f"persona {display}"
    if details:
        fragment += f" ({'; '.join(details)})"
    return fragment


def _render_intent_summary(line: str) -> str:
    descriptor, parts = parse_persona_summary_line(line, "intent_preset: ")
    spoken = ""
    label = ""
    display = ""
    purpose = ""
    others: list[str] = []
    for part in parts:
        lower = part.lower()
        if lower.startswith("say: intent "):
            spoken = part[len("say: intent ") :].strip()
            continue
        if lower.startswith("label="):
            label = part.split("=", 1)[1].strip()
            continue
        if lower.startswith("display="):
            display = part.split("=", 1)[1].strip()
            continue
        if lower.startswith("purpose="):
            purpose = part.split("=", 1)[1].strip()
            continue
        others.append(part)
    primary = descriptor or display or label or "intent"
    details: list[str] = []
    if descriptor:
        details.append(f"key={descriptor}")
    if label and label not in (primary, display):
        details.append(f"label={label}")
    if display and display != primary:
        details.append(f"display={display}")
    say_value = spoken or descriptor or primary
    if say_value:
        details.append(f"say: intent {say_value}")
    if purpose:
        details.append(f"purpose={purpose}")
    details.extend(others)
    fragment = f"intent {primary}"
    if details:
        fragment += f" ({'; '.join(details)})"
    return fragment


def persona_summary_fragments(entry: object) -> list[str]:
    header_lines = persona_header_lines(entry)
    if not header_lines:
        return []
    fragments: list[str] = []
    for line in header_lines:
        if line.startswith("persona_preset: "):
            fragment = _render_persona_summary(line)
        elif line.startswith("intent_preset: "):
            fragment = _render_intent_summary(line)
        else:
            fragment = ""
        if fragment.strip():
            fragments.append(fragment)
    return fragments


def latest():
    return requestlog_latest()


def nth_from_latest(offset: int):
    return requestlog_nth_from_latest(offset)


def all_entries():
    entries = requestlog_all_entries()
    if isinstance(entries, list):
        return entries
    try:
        return list(entries)
    except TypeError:
        return []


def append_entry(*args, **kwargs):
    return requestlog_append_entry(*args, **kwargs)


def append_history_entry(entry: object) -> None:
    requestlog_module._history.append(entry)  # type: ignore[attr-defined]


def append_entry_from_request(**kwargs):
    return requestlog_append_entry_from_request(**kwargs)


def clear_history() -> None:
    requestlog_clear_history()


def validate_history_axes() -> None:
    requestlog_validate_history_axes()


def remediate_history_axes(
    *, drop_if_missing_directional: bool = False, dry_run: bool = False
) -> dict[str, int]:
    return requestlog_remediate_history_axes(
        drop_if_missing_directional=drop_if_missing_directional,
        dry_run=dry_run,
    )


def current_streaming_gating_summary() -> dict[str, object]:
    from .streamingCoordinator import current_streaming_gating_summary as _summary

    return _summary()


def try_begin_request(state=None, *, source: str = "") -> tuple[bool, str]:
    from .requestGating import try_begin_request as _try_begin_request

    return _try_begin_request(state, source=source)


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


def filter_axes_payload(
    axes: Mapping[str, Sequence[str]] | None,
) -> dict[str, list[str]]:
    payload = _coerce_axes_mapping(axes)
    return requestlog_filter_axes_payload(payload)


axis_snapshot_from_axes = axes_snapshot_from_axes


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


def last_drop_reason_code() -> RequestDropReason:
    """Return the canonical drop reason code for the last drop."""

    return requestlog_module.last_drop_reason_code()


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


def state_is_in_flight(state: RequestState) -> bool:
    lifecycle_state = lifecycle_status_for(state)
    return lifecycle_is_in_flight(lifecycle_state)


def state_try_start_request(
    state: RequestState,
) -> tuple[bool, RequestDropReason]:
    lifecycle_state = lifecycle_status_for(state)
    allowed, reason = lifecycle_try_start_request(lifecycle_state)
    return allowed, cast(RequestDropReason, reason)


def reduce_request_state(
    state: RequestLifecycleState,
    event: str,
) -> RequestLifecycleState:
    return lifecycle_reduce_request_state(state, event)


__all__ = [
    "AxisSnapshot",
    "KNOWN_AXIS_KEYS",
    "HistoryAxisSnapshot",
    "HistorySnapshotEntry",
    "axes_snapshot_from_axes",
    "filter_axes_payload",
    "history_axes_for",
    "history_snapshot_entry_from",
    "coerce_history_snapshot_entry",
    "persona_header_lines",
    "parse_persona_summary_line",
    "persona_summary_fragments",
    "latest",
    "nth_from_latest",
    "all_entries",
    "append_entry",
    "append_history_entry",
    "append_entry_from_request",
    "clear_history",
    "validate_history_axes",
    "remediate_history_axes",
    "current_streaming_gating_summary",
    "try_begin_request",
    "RequestDropReason",
    "RequestEvent",
    "RequestEventKind",
    "RequestPhase",
    "RequestState",
    "RequestLifecycleState",
    "RequestStatus",
    "Surface",
    "lifecycle_status_for",
    "transition",
    "state_is_in_flight",
    "state_try_start_request",
    "reduce_request_state",
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
