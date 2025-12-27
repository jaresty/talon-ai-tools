"""Global request history log utilities."""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Iterable, Mapping, Optional, Tuple, cast
from copy import deepcopy

from .requestState import RequestDropReason

try:
    from .modelHelpers import notify
except Exception:  # pragma: no cover - defensive fallback for stubs
    from typing import Callable

    notify = cast(Callable[[str], None], lambda message: None)


from .axisMappings import axis_registry_tokens, axis_value_to_key_map_for
from .axisCatalog import axis_catalog
from .personaConfig import canonical_persona_token, persona_intent_maps
from .personaOrchestrator import get_persona_intent_orchestrator
from .requestHistory import RequestHistory, RequestLogEntry

_history = RequestHistory()


@dataclass(frozen=True)
class DropReason:
    code: RequestDropReason = ""
    message: str = ""


_last_drop_reason = DropReason()
_gating_drop_counts: Counter[RequestDropReason] = Counter()
_gating_drop_sources: Counter[str] = Counter()
_gating_drop_reason_sources: Counter[tuple[RequestDropReason, str]] = Counter()
_last_gating_drop_source: str = ""


def _normalise_gating_source(source: object) -> str:
    text = str(source or "").strip()
    return text if text else "unspecified"


def record_gating_drop(reason: RequestDropReason, *, source: object = "") -> None:
    """Record a request gating drop for telemetry/guardrail reporting."""

    if not reason:
        return
    try:
        _gating_drop_counts[reason] += 1
    except Exception:
        pass

    source_key = _normalise_gating_source(source)
    try:
        _gating_drop_sources[source_key] += 1
    except Exception:
        pass

    try:
        _gating_drop_reason_sources[(reason, source_key)] += 1
    except Exception:
        pass

    global _last_gating_drop_source
    _last_gating_drop_source = source_key


def gating_drop_stats(*, reset: bool = False) -> dict[str, int]:
    """Return counts of gating drops grouped by reason code.

    When ``reset`` is True the internal counters are cleared after reading to
    support periodic telemetry snapshots (for example, CI guardrails).
    """

    stats = {code: int(count) for code, count in _gating_drop_counts.items() if count}
    if reset:
        _gating_drop_counts.clear()
        _gating_drop_sources.clear()
        _gating_drop_reason_sources.clear()
        global _last_gating_drop_source
        _last_gating_drop_source = ""
    return stats


def gating_drop_source_stats(*, reset: bool = False) -> dict[str, int]:
    """Return counts of gating drops grouped by source identifier."""

    stats = {
        source: int(count) for source, count in _gating_drop_sources.items() if count
    }
    if reset:
        _gating_drop_sources.clear()
        _gating_drop_reason_sources.clear()
        global _last_gating_drop_source
        _last_gating_drop_source = ""
    return stats


def consume_gating_drop_stats() -> dict[str, int]:
    """Return and clear the current gating drop statistics."""

    counts = gating_drop_stats(reset=True)
    gating_drop_source_stats(reset=True)
    return counts


KNOWN_AXIS_KEYS: tuple[str, ...] = (
    "completeness",
    "scope",
    "method",
    "form",
    "channel",
    "directional",
)

_PERSONA_SNAPSHOT_KEYS: tuple[str, ...] = (
    "persona_preset_key",
    "persona_preset_label",
    "persona_preset_spoken",
    "persona_voice",
    "persona_audience",
    "persona_tone",
    "intent_preset_key",
    "intent_preset_label",
    "intent_display",
    "intent_purpose",
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
    raw_axis_catalog = catalog.get("axes", {}) if isinstance(catalog, dict) else {}
    axis_tokens: dict[str, set[str]] = {}
    if isinstance(raw_axis_catalog, Mapping):
        for axis, tokens in raw_axis_catalog.items():
            try:
                axis_tokens[str(axis)] = set((tokens or {}).keys())  # type: ignore[attr-defined]
            except AttributeError:
                axis_tokens[str(axis)] = set()
    raw_axis_lists = (
        catalog.get("axis_list_tokens", {}) if isinstance(catalog, dict) else {}
    )
    axis_list_tokens: dict[str, set[str]] = {}
    if isinstance(raw_axis_lists, Mapping):
        for axis, tokens in raw_axis_lists.items():
            values: set[str] = set()
            if isinstance(tokens, (list, tuple, set)):
                values = {str(token) for token in tokens if str(token)}
            axis_list_tokens[str(axis)] = values

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


def _normalise_persona_snapshot(
    snapshot: Optional[dict[str, object]],
) -> dict[str, str]:
    if not snapshot:
        return {}
    payload: dict[str, str] = {}
    for key in _PERSONA_SNAPSHOT_KEYS:
        value = snapshot.get(key) if isinstance(snapshot, dict) else None
        if value is None:
            continue
        if isinstance(value, str):
            trimmed = value.strip()
            if trimmed:
                payload[key] = trimmed
            continue
        text = str(value).strip()
        if text:
            payload[key] = text

    try:
        orchestrator = get_persona_intent_orchestrator()
    except Exception:
        orchestrator = None

    if orchestrator is not None:
        persona_key = payload.get("persona_preset_key", "")
        persona_label = payload.get("persona_preset_label", "")
        persona_spoken = payload.get("persona_preset_spoken", "")

        if not persona_key:
            persona_key = orchestrator.canonical_persona_key(persona_spoken)
        if not persona_key:
            persona_key = orchestrator.canonical_persona_key(persona_label)

        if persona_key:
            payload["persona_preset_key"] = persona_key
            preset = orchestrator.persona_presets.get(persona_key)
            if preset is not None:
                if not persona_label:
                    label_value = getattr(preset, "label", "") or getattr(
                        preset, "key", ""
                    )
                    if label_value:
                        payload["persona_preset_label"] = label_value
                        persona_label = label_value
                spoken_value = (
                    getattr(preset, "spoken", "")
                    or persona_label
                    or getattr(preset, "key", "")
                )
                if spoken_value:
                    payload["persona_preset_spoken"] = spoken_value
                if getattr(preset, "voice", None) and not payload.get("persona_voice"):
                    payload["persona_voice"] = preset.voice or ""
                if getattr(preset, "audience", None) and not payload.get(
                    "persona_audience"
                ):
                    payload["persona_audience"] = preset.audience or ""
                if getattr(preset, "tone", None) and not payload.get("persona_tone"):
                    payload["persona_tone"] = preset.tone or ""

        intent_key = payload.get("intent_preset_key", "")
        intent_label = payload.get("intent_preset_label", "")
        intent_display = payload.get("intent_display", "")
        intent_purpose = payload.get("intent_purpose", "")

        if not intent_key:
            for alias in (intent_display, intent_label, intent_purpose):
                canonical = orchestrator.canonical_intent_key(alias)
                if canonical:
                    intent_key = canonical
                    payload["intent_preset_key"] = canonical
                    break

        if intent_key:
            canonical_candidate = canonical_persona_token("intent", intent_key)
            if canonical_candidate:
                if canonical_candidate != intent_key:
                    intent_key = canonical_candidate
                    payload["intent_preset_key"] = canonical_candidate
            else:
                payload["_invalid_intent_token"] = intent_key
                payload.pop("intent_preset_key", None)
                payload.pop("intent_preset_label", None)
                payload.pop("intent_display", None)
                payload.pop("intent_purpose", None)
                intent_key = ""
                intent_label = ""
                intent_display = ""
                intent_purpose = ""

        if intent_key:
            preset_intent = orchestrator.intent_presets.get(intent_key)
            if preset_intent is not None:
                if not intent_label:
                    label_value = getattr(preset_intent, "label", "") or getattr(
                        preset_intent, "key", ""
                    )
                    if label_value:
                        payload["intent_preset_label"] = label_value
                        intent_label = label_value
                if not intent_purpose:
                    purpose_value = getattr(preset_intent, "intent", "") or getattr(
                        preset_intent, "key", ""
                    )
                    if purpose_value:
                        payload["intent_purpose"] = purpose_value
                        intent_purpose = purpose_value
            display_value = orchestrator.intent_display_map.get(intent_key)
            if not display_value and intent_key:
                preset_intent = orchestrator.intent_presets.get(intent_key)
                if preset_intent is not None:
                    display_value = orchestrator.intent_display_map.get(
                        getattr(preset_intent, "intent", "")
                    )
            if display_value and not intent_display:
                payload["intent_display"] = display_value

        return payload

    try:
        maps = persona_intent_maps()

    except Exception:
        maps = None

    if maps is not None:
        persona_aliases = getattr(maps, "persona_preset_aliases", {}) or {}
        persona_presets = getattr(maps, "persona_presets", {}) or {}
        intent_aliases = getattr(maps, "intent_preset_aliases", {}) or {}
        intent_synonyms = getattr(maps, "intent_synonyms", {}) or {}
        intent_presets = getattr(maps, "intent_presets", {}) or {}
        intent_display_map = getattr(maps, "intent_display_map", {}) or {}

        persona_key = payload.get("persona_preset_key", "")
        persona_label = payload.get("persona_preset_label", "")
        persona_spoken = payload.get("persona_preset_spoken", "")

        if not persona_key:
            for alias in (persona_spoken, persona_label):
                alias_l = (alias or "").strip().lower()
                if alias_l:
                    canonical = persona_aliases.get(alias_l)
                    if canonical:
                        persona_key = canonical.strip()
                        if persona_key:
                            payload["persona_preset_key"] = persona_key
                            break

        preset = persona_presets.get(persona_key) if persona_key else None
        if preset is not None:
            if not persona_label:
                label_value = getattr(preset, "label", "") or preset.key
                if label_value:
                    payload["persona_preset_label"] = label_value
                    persona_label = label_value
            if not persona_spoken:
                spoken_value = (
                    getattr(preset, "spoken", "") or persona_label or preset.key
                )
                if spoken_value:
                    payload["persona_preset_spoken"] = spoken_value
            if not payload.get("persona_voice") and getattr(preset, "voice", None):
                payload["persona_voice"] = preset.voice or ""
            if not payload.get("persona_audience") and getattr(
                preset, "audience", None
            ):
                payload["persona_audience"] = preset.audience or ""
            if not payload.get("persona_tone") and getattr(preset, "tone", None):
                payload["persona_tone"] = preset.tone or ""

        intent_key = payload.get("intent_preset_key", "")
        intent_label = payload.get("intent_preset_label", "")
        intent_display = payload.get("intent_display", "")
        intent_purpose = payload.get("intent_purpose", "")

        if not intent_key:
            for alias in (intent_display, intent_label, intent_purpose):
                alias_l = (alias or "").strip().lower()
                if not alias_l:
                    continue
                canonical = intent_aliases.get(alias_l) or intent_synonyms.get(alias_l)
                if canonical:
                    intent_key = canonical.strip()
                    if intent_key:
                        payload["intent_preset_key"] = intent_key
                        break

        if intent_key:
            canonical_candidate = canonical_persona_token("intent", intent_key)
            if canonical_candidate:
                if canonical_candidate != intent_key:
                    intent_key = canonical_candidate
                    payload["intent_preset_key"] = canonical_candidate
            else:
                payload["_invalid_intent_token"] = intent_key
                payload.pop("intent_preset_key", None)
                payload.pop("intent_preset_label", None)
                payload.pop("intent_display", None)
                payload.pop("intent_purpose", None)
                intent_key = ""
                intent_label = ""
                intent_display = ""
                intent_purpose = ""

        preset_intent = intent_presets.get(intent_key) if intent_key else None
        if preset_intent is not None:
            if not intent_label:
                label_value = getattr(preset_intent, "label", "") or preset_intent.key
                if label_value:
                    payload["intent_preset_label"] = label_value
                    intent_label = label_value
            if not intent_purpose:
                purpose_value = (
                    getattr(preset_intent, "intent", "") or preset_intent.key
                )
                if purpose_value:
                    payload["intent_purpose"] = purpose_value
                    intent_purpose = purpose_value
            if not intent_display:
                display_value = intent_display_map.get(
                    preset_intent.key
                ) or intent_display_map.get(getattr(preset_intent, "intent", ""))
                if display_value:
                    payload["intent_display"] = display_value
        elif intent_key and not intent_display:
            display_value = intent_display_map.get(intent_key)
            if display_value:
                payload["intent_display"] = display_value

    return payload


def _current_persona_snapshot() -> dict[str, object]:
    try:
        from .suggestionCoordinator import (
            last_recipe_snapshot,
        )  # local import to avoid cycles

        return last_recipe_snapshot()
    except Exception:
        return {}


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
    persona: Optional[dict[str, object]] = None,
) -> None:
    """Append a request entry to the bounded history ring.

    Entries missing a directional lens are dropped immediately in line with
    ADR-048/ADR-0056 concordance requirements.
    """
    if persona is None:
        persona = _current_persona_snapshot()
    persona_payload = _normalise_persona_snapshot(persona)

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
    try:
        pending_message = last_drop_reason()
    except Exception:
        pending_message = ""
    if not pending_message or pending_message.strip().lower() != "pending":
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
            persona=persona_payload,
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

    persona_snapshot: dict[str, object] = _current_persona_snapshot()

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
        persona=persona_snapshot,
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

    if not reason:
        return ""
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
    reason_text = str(reason).strip() or "unknown"
    return f"GPT: Request blocked; reason={reason_text}."


def render_drop_reason(reason: RequestDropReason) -> str:
    """Return a rendered drop message, falling back to the canonical template."""

    try:
        message = drop_reason_message(reason)
    except Exception:
        message = ""
    if message and message.strip():
        return message
    reason_text = str(reason).strip() or "unknown"
    return f"GPT: Request blocked; reason={reason_text}."


def _scan_history_entries(raise_on_failure: bool) -> dict[str, int]:
    from .historyLifecycle import (
        coerce_history_snapshot_entry,
        parse_persona_summary_line,
        persona_header_lines,
    )

    stats = {
        "total_entries": 0,
        "entries_missing_directional": 0,
        "entries_with_unsupported_axes": 0,
        "entries_with_persona_snapshot": 0,
        "entries_missing_persona_headers": 0,
        "persona_preset_missing_say_hint": 0,
        "persona_preset_missing_descriptor": 0,
        "intent_preset_missing_say_hint": 0,
        "intent_preset_missing_descriptor": 0,
        "intent_invalid_tokens": 0,
        "unexpected_persona_header": 0,
        "persona_alias_pairs": {},
        "intent_display_pairs": {},
    }

    persona_alias_pairs = stats["persona_alias_pairs"]
    intent_display_pairs = stats["intent_display_pairs"]

    for entry in _history.all():
        stats["total_entries"] += 1

        persona_snapshot = entry.persona or {}
        invalid_intent = persona_snapshot.get("_invalid_intent_token")
        if invalid_intent:
            stats["intent_invalid_tokens"] += 1
            stats["intent_preset_missing_descriptor"] += 1

        axes = entry.axes or {}
        if not isinstance(axes, dict):
            try:
                axes = dict(axes)
            except Exception:
                axes = {}

        unknown = sorted(key for key in axes.keys() if key not in KNOWN_AXIS_KEYS)
        if unknown:
            stats["entries_with_unsupported_axes"] += 1
            if raise_on_failure:
                keys = ", ".join(unknown)
                request_id = entry.request_id or "?"
                raise ValueError(
                    f"History entry {request_id!r} includes unsupported axis keys: {keys}"
                )

        normalized_entry = coerce_history_snapshot_entry(entry)
        axes = normalized_entry.axes or {}

        directional_tokens = axes.get("directional", []) or []
        if not directional_tokens:
            stats["entries_missing_directional"] += 1
            if raise_on_failure:
                request_id = normalized_entry.request_id or entry.request_id or "?"
                raise ValueError(
                    f"History entry {request_id!r} is missing a directional lens; Concordance requires one."
                )

        persona_snapshot = normalized_entry.persona or {}
        if persona_snapshot:
            stats["entries_with_persona_snapshot"] += 1
            persona_lines = persona_header_lines(normalized_entry)
            request_id = normalized_entry.request_id or entry.request_id or "?"
            if not persona_lines:
                stats["entries_missing_persona_headers"] += 1
                if raise_on_failure:
                    raise ValueError(
                        "History persona metadata missing required catalog-backed header lines; "
                        f"entry {request_id!r} has persona snapshot without persona/intent headers."
                    )
                else:
                    continue
            for line in persona_lines:
                lower = line.lower()
                if line.startswith("persona_preset: "):
                    descriptor, details = parse_persona_summary_line(
                        line, "persona_preset: "
                    )
                    canonical = descriptor.strip()
                    if not canonical:
                        stats["persona_preset_missing_descriptor"] += 1
                        if raise_on_failure:
                            raise ValueError(
                                "History persona preset entry missing descriptor; "
                                f"entry {request_id!r} header: {line}"
                            )
                    alias = ""
                    for part in details:
                        part_lower = part.lower()
                        if part_lower.startswith("say: persona "):
                            alias = part[len("say: persona ") :].strip()
                            break
                    if not alias:
                        stats["persona_preset_missing_say_hint"] += 1
                        if raise_on_failure:
                            raise ValueError(
                                "History persona preset entry missing say hint; "
                                f"entry {request_id!r} header: {line}"
                            )
                    if canonical and alias:
                        canon_map = persona_alias_pairs.setdefault(canonical, {})
                        canon_map[alias] = canon_map.get(alias, 0) + 1
                elif line.startswith("intent_preset: "):
                    descriptor, details = parse_persona_summary_line(
                        line, "intent_preset: "
                    )
                    canonical_intent = descriptor.strip()
                    if not canonical_intent:
                        stats["intent_preset_missing_descriptor"] += 1
                        if raise_on_failure:
                            raise ValueError(
                                "History intent preset entry missing descriptor; "
                                f"entry {request_id!r} header: {line}"
                            )
                    display_value = ""
                    spoken_alias = ""
                    for part in details:
                        part_lower = part.lower()
                        if part_lower.startswith("display="):
                            display_value = part.split("=", 1)[1].strip()
                        elif part_lower.startswith("say: intent "):
                            spoken_alias = part[len("say: intent ") :].strip()
                        elif part_lower.startswith("label=") and not display_value:
                            display_value = part.split("=", 1)[1].strip()
                    if "say: intent " not in lower:
                        stats["intent_preset_missing_say_hint"] += 1
                        if raise_on_failure:
                            raise ValueError(
                                "History intent preset entry missing say hint; "
                                f"entry {request_id!r} header: {line}"
                            )
                    alias_value = display_value or spoken_alias
                    if canonical_intent and alias_value:
                        canon_map = intent_display_pairs.setdefault(
                            canonical_intent, {}
                        )
                        canon_map[alias_value] = canon_map.get(alias_value, 0) + 1
                else:
                    stats["unexpected_persona_header"] += 1
                    if raise_on_failure:
                        raise ValueError(
                            "History persona metadata included unexpected header line; "
                            f"entry {request_id!r} header: {line}"
                        )
    return stats


def validate_history_axes() -> None:
    """Ensure stored history entries use Concordance-recognised axes with directional lenses."""

    _ = _scan_history_entries(raise_on_failure=True)


def history_validation_stats() -> dict[str, object]:
    """Return validation statistics without raising on failures.

    Includes request gating drop counts so Concordance summaries can
    contextualise how often in-flight guards rejected new requests.
    """

    stats = _scan_history_entries(raise_on_failure=False)
    gating_counts = gating_drop_stats()
    gating_sources = gating_drop_source_stats()
    stats_obj = cast(dict[str, object], dict(stats))
    stats_obj["gating_drop_total"] = sum(gating_counts.values())
    stats_obj["gating_drop_counts"] = dict(gating_counts)
    stats_obj["gating_drop_sources"] = dict(gating_sources)

    def _convert_to_int(candidate: object) -> Optional[int]:
        if isinstance(candidate, bool):
            return int(candidate)
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, float):
            return int(candidate)
        if isinstance(candidate, str):
            value = candidate.strip()
            if not value:
                return None
            try:
                return int(value)
            except ValueError:
                return None
        return None

    normalized_counts: dict[str, int] = {}
    normalized_sources: dict[str, int] = {}
    streaming_last: dict[str, object] = {}
    streaming_last_source: dict[str, object] = {}
    status_value = ""
    total_int = 0
    counts_sorted_pairs: list[Tuple[str, int]] = []
    sources_sorted_pairs: list[Tuple[str, int]] = []

    summary_data: Mapping[str, object] | None = None
    try:
        from .historyLifecycle import current_streaming_gating_summary

        candidate = current_streaming_gating_summary()
    except Exception:
        candidate = None
    if isinstance(candidate, Mapping):
        summary_data = candidate

    if summary_data is not None:
        counts_obj = summary_data.get("counts")
        if isinstance(counts_obj, Mapping):
            for reason, value in counts_obj.items():
                count_value = _convert_to_int(value)
                if count_value is None or count_value < 0:
                    continue
                normalized_counts[str(reason)] = count_value
        counts_sorted_obj = summary_data.get("counts_sorted")
        if isinstance(counts_sorted_obj, list):
            for item in counts_sorted_obj:
                if not isinstance(item, Mapping):
                    continue
                reason_text = str(item.get("reason") or "")
                count_value = _convert_to_int(item.get("count"))
                if not reason_text or count_value is None or count_value < 0:
                    continue
                counts_sorted_pairs.append((reason_text, count_value))
                normalized_counts.setdefault(reason_text, count_value)
        sources_obj = summary_data.get("sources")
        if isinstance(sources_obj, Mapping):
            for source_name, value in sources_obj.items():
                count_value = _convert_to_int(value)
                if count_value is None or count_value < 0:
                    continue
                normalized_sources[str(source_name)] = count_value
        sources_sorted_obj = summary_data.get("sources_sorted")
        if isinstance(sources_sorted_obj, list):
            for item in sources_sorted_obj:
                if not isinstance(item, Mapping):
                    continue
                source_text = str(item.get("source") or "")
                count_value = _convert_to_int(item.get("count"))
                if not source_text or count_value is None or count_value < 0:
                    continue
                sources_sorted_pairs.append((source_text, count_value))
                normalized_sources.setdefault(source_text, count_value)
        total_candidate = _convert_to_int(summary_data.get("total"))
        if total_candidate is not None and total_candidate >= 0:
            total_int = total_candidate
        last_obj = summary_data.get("last")
        if isinstance(last_obj, Mapping):
            reason_text = str(last_obj.get("reason") or "")
            reason_count = _convert_to_int(last_obj.get("reason_count"))
            if reason_text:
                streaming_last["reason"] = reason_text
            if reason_count is None:
                if reason_text:
                    streaming_last["reason_count"] = normalized_counts.get(
                        reason_text, 0
                    )
            else:
                streaming_last["reason_count"] = reason_count
            if (
                not streaming_last.get("reason")
                and streaming_last.get("reason_count") is None
            ):
                streaming_last = {}
        last_source_obj = summary_data.get("last_source")
        if isinstance(last_source_obj, Mapping):
            source_text = str(last_source_obj.get("source") or "")
            source_count = _convert_to_int(last_source_obj.get("count"))
            if source_text:
                streaming_last_source["source"] = source_text
            if source_count is None:
                if source_text:
                    streaming_last_source["count"] = normalized_sources.get(
                        source_text, 0
                    )
            else:
                streaming_last_source["count"] = source_count
            if (
                not streaming_last_source.get("source")
                and streaming_last_source.get("count") is None
            ):
                streaming_last_source = {}

        status_candidate = summary_data.get("status")
        if isinstance(status_candidate, str):
            candidate_text = status_candidate.strip()
            if candidate_text:
                status_value = candidate_text

    if not normalized_sources and gating_sources:
        normalized_sources = dict(gating_sources)
    if not sources_sorted_pairs and normalized_sources:
        sources_sorted_pairs = sorted(
            normalized_sources.items(), key=lambda item: (-item[1], item[0])
        )
    if (
        not streaming_last_source
        and _last_gating_drop_source
        and normalized_sources.get(_last_gating_drop_source) is not None
    ):
        streaming_last_source = {
            "source": _last_gating_drop_source,
            "count": normalized_sources.get(_last_gating_drop_source, 0),
        }

    if not normalized_counts and gating_counts:
        normalized_counts = dict(gating_counts)
    if not counts_sorted_pairs and normalized_counts:
        counts_sorted_pairs = sorted(
            normalized_counts.items(), key=lambda item: (-item[1], item[0])
        )

    if not status_value:
        status_value = "unknown"

    counts_total = sum(normalized_counts.values())
    if counts_total and (total_int < counts_total):
        total_int = counts_total
    if not streaming_last:
        streaming_last = {}

    stats_obj["streaming_gating_summary"] = {
        "counts": normalized_counts,
        "counts_sorted": [
            {"reason": reason, "count": count} for reason, count in counts_sorted_pairs
        ],
        "sources": normalized_sources,
        "sources_sorted": [
            {"source": source, "count": count} for source, count in sources_sorted_pairs
        ],
        "last": streaming_last,
        "last_source": streaming_last_source,
        "total": total_int,
        "status": status_value,
        "last_message": _last_drop_reason.message,
        "last_code": _last_drop_reason.code,
    }
    stats_obj["gating_drop_last_message"] = _last_drop_reason.message
    stats_obj["gating_drop_last_code"] = _last_drop_reason.code
    return stats_obj


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
    "record_gating_drop",
    "gating_drop_stats",
    "consume_gating_drop_stats",
    "axis_snapshot_from_axes",
    "AxisSnapshot",
]
