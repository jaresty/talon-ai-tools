"""Global request history log utilities."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Iterable, Mapping, Optional, Tuple
from copy import deepcopy

from .requestState import RequestDropReason

try:
    from .modelHelpers import notify
except Exception:  # pragma: no cover - defensive fallback for stubs

    def notify(_msg: str) -> None:
        return None


from .axisMappings import axis_registry_tokens, axis_value_to_key_map_for
from .axisCatalog import axis_catalog
from .requestHistory import RequestHistory, RequestLogEntry

_history = RequestHistory()


@dataclass(frozen=True)
class DropReason:
    code: RequestDropReason = ""
    message: str = ""


_last_drop_reason = DropReason()


KNOWN_AXIS_KEYS: tuple[str, ...] = (
    "completeness",
    "scope",
    "method",
    "form",
    "channel",
    "directional",
)


@dataclass(frozen=True)
class AxisSnapshot:
    """Structured view of Concordance-relevant axes for history/log surfaces."""

    axes: Mapping[str, Tuple[str, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        axes_source = self.axes or {}
        axes_map = {
            key: tuple(str(value).strip() for value in values if str(value).strip())
            for key, values in axes_source.items()
        }
        object.__setattr__(self, "axes", MappingProxyType(axes_map))

    def get(self, key: str, default: Optional[list[str]] = None) -> Optional[list[str]]:
        if key in self.axes:
            return list(self.axes[key])
        return default

    def keys(self):
        return iter(self.axes.keys())

    def items(self):
        for key, values in self.axes.items():
            yield key, list(values)

    def values(self):
        for values in self.axes.values():
            yield list(values)

    def __contains__(self, key: object) -> bool:
        return key in self.axes

    def __iter__(self):
        return self.keys()

    def __len__(self) -> int:
        return len(self.axes)

    def as_dict(self) -> dict[str, list[str]]:
        return {key: list(values) for key, values in self.axes.items()}

    def known_axes(self) -> dict[str, list[str]]:
        """Return only Concordance-recognised axes."""

        return {key: list(values) for key, values in self.axes.items()}


def _filter_axes_payload(
    axes: Optional[dict[str, list[str]]],
) -> dict[str, list[str]]:
    """Normalise and filter axes payload for request history.

    Ensures token-only axis state per ADR-034/ADR-0045/ADR-048 by:
    - Trimming blanks
    - Dropping obviously hydrated values that start with 'Important:'
    - Keeping known axis tokens when present in axisMappings
    - Applying axis caps/deduplication (scope×2, method×3, form×1, channel×1)
    - Rejecting the legacy ``style`` axis in favour of form/channel
    - Dropping non-catalog axis keys instead of passing them through
    """
    if not axes:
        return {}

    # Lazy imports to avoid cycles with modelHelpers/talonSettings callers.
    try:
        from .talonSettings import _canonicalise_axis_tokens
    except Exception:  # pragma: no cover - defensive fallback for stubs

        def _canonicalise_axis_tokens(axis: str, tokens: list[str]) -> list[str]:
            return tokens

    catalog = axis_catalog()
    axis_tokens = {
        axis: set((tokens or {}).keys()) for axis, tokens in catalog["axes"].items()
    }
    axis_list_tokens = {
        axis: set(tokens or []) for axis, tokens in catalog["axis_list_tokens"].items()
    }

    filtered: dict[str, list[str]] = {}

    for axis_name, raw_values in axes.items():
        values: list[str]
        if isinstance(raw_values, list):
            values = [str(v).strip() for v in raw_values]
        else:
            values = [str(raw_values).strip()]

        # Drop empty values early.
        values = [v for v in values if v]
        if not values:
            continue

        if axis_name == "style":
            raise ValueError("style axis is removed; use form/channel instead.")

        if axis_name in (
            "completeness",
            "scope",
            "method",
            "form",
            "channel",
            "directional",
        ):
            mapping = axis_value_to_key_map_for(axis_name)
            known_tokens = axis_registry_tokens(axis_name)
            # Include tokens from the axis catalog and Talon lists to catch drift.
            known_tokens = known_tokens.union(axis_tokens.get(axis_name, set()))
            known_tokens = known_tokens.union(axis_list_tokens.get(axis_name, set()))
            known_tokens_lower = {t.lower() for t in known_tokens}
            mapping_lower_keys = {k.lower() for k in mapping} if mapping else set()
            kept: list[str] = []
            for token in values:
                lower = token.lower()
                if lower.startswith("important:"):
                    # Skip obviously hydrated/system-prompt strings.
                    continue
                if known_tokens_lower and lower in known_tokens_lower:
                    kept.append(lower)
                    continue
                if (
                    not known_tokens_lower
                    and mapping_lower_keys
                    and lower in mapping_lower_keys
                ):
                    kept.append(lower)
            if kept:
                if axis_name != "completeness":
                    kept = _canonicalise_axis_tokens(axis_name, kept)
                filtered[axis_name] = kept

    return filtered


def axis_snapshot_from_axes(axes: Optional[dict[str, list[str]]]) -> AxisSnapshot:
    """Pure helper: normalise axes into a Concordance-aligned snapshot."""

    filtered = _filter_axes_payload(axes)
    known_axes = {
        key: list(values) for key, values in filtered.items() if key in KNOWN_AXIS_KEYS
    }
    return AxisSnapshot(axes=known_axes)


def append_entry(
    request_id: str,
    prompt: str,
    response: str,
    meta: str = "",
    recipe: str = "",
    started_at_ms: Optional[int] = None,
    duration_ms: Optional[int] = None,
    axes: Optional[dict[str, list[str]]] = None,
    provider_id: str = "",
) -> None:
    """Append a request entry to the bounded history ring.

    Entries missing a directional lens are dropped immediately in line with
    ADR-048/ADR-0056 concordance requirements.
    """
    if not request_id or not str(request_id).strip():
        message = drop_reason_message("missing_request_id")
        try:
            notify(message)
        except Exception:
            pass
        set_drop_reason("missing_request_id")
        return
    try:
        print(
            f"[requestLog] append id={request_id!r} prompt_len={len(prompt or '')} "
            f"response_len={len(response or '')} recipe={recipe!r} duration_ms={duration_ms} "
            f"axes_keys={list((axes or {}).keys())} provider_id={provider_id}"
        )
    except Exception:
        pass
    axes_payload = _filter_axes_payload(axes)
    if (
        not axes_payload
        or not isinstance(axes_payload, dict)
        or not axes_payload.get("directional")
    ):
        try:
            print(f"[requestLog] drop id={request_id!r} missing directional")
        except Exception:
            pass
        message = drop_reason_message("missing_directional")
        try:
            notify(message)
        except Exception:
            pass
        set_drop_reason("missing_directional")
        return
    set_drop_reason("")
    _history.append(
        RequestLogEntry(
            request_id=request_id,
            prompt=prompt,
            response=response,
            meta=meta,
            recipe=recipe,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
            axes=axes_payload,
            provider_id=provider_id or "",
        )
    )
    try:
        latest_entry = _history.latest() if hasattr(_history, "latest") else None
        latest_id = latest_entry.request_id if latest_entry else "?"
        print(
            f"[requestLog] stored entries={len(_history)} latest_id={latest_id} hist_id={id(_history)}"
        )
    except Exception:
        pass


def append_entry_from_request(
    request_id: str,
    request: object | None,
    answer_text: str,
    meta_text: str = "",
    *,
    recipe: str = "",
    started_at_ms: Optional[int] = None,
    duration_ms: Optional[int] = None,
    axes: Optional[dict[str, list[str]]] = None,
    provider_id: str = "",
) -> str:
    """Append a history entry derived from a request dict.

    This helper centralises the prompt/axes extraction semantics used when
    logging completed GPT requests so callers share a single contract for
    history entries.
    """

    prompt_text = ""
    try:
        request_dict = request or {}
        if isinstance(request_dict, dict):
            messages = request_dict.get("messages", [])
            user_messages = [
                m for m in messages if isinstance(m, dict) and m.get("role") == "user"
            ]
            if user_messages:
                parts: list[str] = []
                for item in user_messages[0].get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        parts.append(item.get("text", ""))
                prompt_text = "\n\n".join(parts).strip()
    except Exception:
        prompt_text = ""

    axes_source = axes or {}
    try:
        axes_copy = deepcopy(axes_source)
    except Exception:
        axes_copy = dict(axes_source)

    axes_payload = _filter_axes_payload(axes_copy)

    append_entry(
        request_id,
        prompt_text,
        answer_text,
        meta_text,
        recipe=recipe,
        started_at_ms=started_at_ms,
        duration_ms=duration_ms,
        axes=axes_payload,
        provider_id=provider_id,
    )
    return prompt_text


def latest() -> Optional[RequestLogEntry]:
    return _history.latest()


def nth_from_latest(offset: int) -> Optional[RequestLogEntry]:
    return _history.nth_from_latest(offset)


def all_entries():
    try:
        entries = _history.all()
        print(f"[requestLog] all_entries len={len(entries)} hist_id={id(_history)}")
        return entries
    except Exception as e:
        try:
            print(f"[requestLog] all_entries failed: {e}")
        except Exception:
            pass
        return []


def clear_history() -> None:
    while len(_history):
        _history._entries.popleft()  # type: ignore[attr-defined]
    set_drop_reason("")


def drop_reason_message(reason: RequestDropReason) -> str:
    """Render a user-facing drop reason message for a reason code."""

    if reason == "in_flight":
        return "GPT: A request is already running; wait for it to finish or cancel it first."
    if reason == "missing_request_id":
        return "GPT: History entry dropped; missing request id."
    if reason == "missing_directional":
        return (
            "GPT: History entry dropped; add a directional lens "
            "(fog/fig/dig/ong/rog/bog/jog) and retry."
        )
    if reason == "history_save_failed":
        return "GPT: Failed to save history entry."
    if reason == "history_save_no_entry":
        return "GPT: No request history available to save."
    if reason == "history_save_empty_prompt":
        return "GPT: No prompt content available to save for this history entry."
    if reason == "history_save_copy_failed":
        return "GPT: Unable to copy history save path."
    if reason == "history_save_open_action_unavailable":
        return "GPT: Unable to open history save; app.open action is unavailable."
    if reason == "history_save_open_exception":
        return "GPT: Unable to open history save path."
    if reason == "history_save_path_unset":
        return "GPT: No saved history path available; run 'model history save exchange' first."
    if reason == "history_save_path_not_found":
        return "GPT: Saved history path not found; rerun 'model history save exchange'."
    if reason == "history_save_dir_create_failed":
        return "GPT: Could not create history save directory."
    if reason == "history_save_write_failed":
        return "GPT: Failed to write history save file."
    if reason == "history_save_missing_directional":
        return (
            "GPT: Cannot save history source; entry is missing a directional lens "
            "(fog/fig/dig/ong/rog/bog/jog)."
        )
    return ""


def validate_history_axes() -> None:
    """Ensure stored history entries use Concordance-recognised axes with directional lenses."""

    for entry in _history.all():
        axes = entry.axes or {}
        if not isinstance(axes, dict):
            try:
                axes = dict(axes)
            except Exception:
                axes = {}

        directional = axes.get("directional")
        if isinstance(directional, list):
            directional_tokens = [
                str(token).strip() for token in directional if str(token).strip()
            ]
        elif directional:
            directional_tokens = [str(directional).strip()]
        else:
            directional_tokens = []

        if not directional_tokens:
            request_id = entry.request_id or "?"
            raise ValueError(
                f"History entry {request_id!r} is missing a directional lens; Concordance requires one."
            )

        unknown = sorted(key for key in axes.keys() if key not in KNOWN_AXIS_KEYS)
        if unknown:
            keys = ", ".join(unknown)
            request_id = entry.request_id or "?"
            raise ValueError(
                f"History entry {request_id!r} includes unsupported axis keys: {keys}"
            )


def remediate_history_axes(
    *,
    drop_if_missing_directional: bool = False,
    dry_run: bool = False,
) -> dict[str, int]:
    """Rewrite stored history axes to match Concordance guardrails.

    Returns a stats dictionary containing counts for `total`, `updated`, `dropped`,
    and `unchanged`. When `drop_if_missing_directional` is true, entries whose
    cleaned axes lack a directional lens are removed. When `dry_run` is true the
    stats are computed without mutating the in-memory history ring.
    """

    entries = list(_history.all())
    stats = {"total": len(entries), "updated": 0, "dropped": 0, "unchanged": 0}
    new_entries = []

    for entry in entries:
        original_axes = entry.axes or {}
        try:
            cleaned_axes = _filter_axes_payload(original_axes)
        except ValueError:
            stats["dropped"] += 1
            continue

        has_directional = bool(cleaned_axes.get("directional"))
        if drop_if_missing_directional and not has_directional:
            stats["dropped"] += 1
            continue

        if cleaned_axes != original_axes:
            stats["updated"] += 1
            new_entries.append(
                RequestLogEntry(
                    request_id=entry.request_id,
                    prompt=entry.prompt,
                    response=entry.response,
                    meta=entry.meta,
                    recipe=entry.recipe,
                    started_at_ms=entry.started_at_ms,
                    duration_ms=entry.duration_ms,
                    axes=cleaned_axes,
                    provider_id=entry.provider_id,
                )
            )
        else:
            stats["unchanged"] += 1
            new_entries.append(entry)

    if not dry_run:
        _history._entries = deque(new_entries, maxlen=_history._max)  # type: ignore[attr-defined]
        set_drop_reason("")

    return stats


def set_drop_reason(reason: RequestDropReason, message: str | None = None) -> None:
    """Set the last drop reason for Concordance-facing surfaces.

    Store both a structured drop reason code and the rendered message so surfaces
    can reason about why something was blocked without parsing free-form text.
    """

    global _last_drop_reason
    if not reason:
        _last_drop_reason = DropReason()
        return
    rendered = message if message is not None else drop_reason_message(reason)
    _last_drop_reason = DropReason(code=reason, message=rendered)


def last_drop_reason() -> str:
    return _last_drop_reason.message


def last_drop_reason_code() -> RequestDropReason:
    return _last_drop_reason.code


def consume_last_drop_reason() -> str:
    """Return and clear the last drop reason (consuming)."""

    reason = _last_drop_reason.message
    set_drop_reason("")
    return reason


def consume_last_drop_reason_record() -> DropReason:
    """Return and clear the last drop reason record (consuming)."""

    record = _last_drop_reason
    set_drop_reason("")
    return record


__all__ = [
    "append_entry",
    "append_entry_from_request",
    "latest",
    "nth_from_latest",
    "all_entries",
    "clear_history",
    "drop_reason_message",
    "set_drop_reason",
    "last_drop_reason",
    "last_drop_reason_code",
    "consume_last_drop_reason",
    "consume_last_drop_reason_record",
    "axis_snapshot_from_axes",
    "AxisSnapshot",
]
