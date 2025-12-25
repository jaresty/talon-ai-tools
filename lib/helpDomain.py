from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from talon import actions

from .historyLifecycle import axes_snapshot_from_axes as axis_snapshot_from_axes
from .personaConfig import persona_intent_maps
from .personaOrchestrator import get_persona_intent_orchestrator


@dataclass(frozen=True)
class HelpIndexEntry:
    label: str
    description: str
    handler: Callable[[], None]
    voice_hint: str = ""
    metadata: Dict[str, Any] | None = None


@dataclass(frozen=True)
class HelpPersonaMetadata:
    key: str
    display_label: str
    spoken_display: str
    spoken_alias: str
    axes_summary: str
    axes_tokens: tuple[str, ...]
    voice_hint: str


@dataclass(frozen=True)
class HelpIntentMetadata:
    key: str
    display_label: str
    canonical_intent: str
    spoken_display: str
    spoken_alias: str
    voice_hint: str


@dataclass(frozen=True)
class HelpMetadataSnapshot:
    personas: tuple[HelpPersonaMetadata, ...]
    intents: tuple[HelpIntentMetadata, ...]


def help_index(
    buttons: Sequence[Any],
    patterns: Sequence[Any],
    presets: Sequence[Any],
    read_list_items: Callable[[str], List[str]],
    catalog: Optional[dict] = None,
) -> List[HelpIndexEntry]:
    """HelpDomain façade: build the help search index.

    This constructs the logical help index over hub buttons, static prompts,
    axis modifiers, patterns, and prompt presets. Callers such as Help Hub can
    wrap the resulting entries in UI-specific types (for example ``HubButton``)
    without re-encoding the indexing semantics. When a catalog is provided, it
    is treated as the SSOT for tokens; list file reads are only used as a
    fallback when catalog data is missing.
    """

    entries: List[HelpIndexEntry] = []

    def _add(
        label: str,
        desc: str,
        handler: Callable[[], None],
        voice_hint: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        entries.append(
            HelpIndexEntry(
                label=label,
                description=desc,
                handler=handler,
                voice_hint=voice_hint,
                metadata=metadata,
            )
        )

    # Existing hub buttons as entries.
    for btn in buttons:
        _add(
            f"Hub: {getattr(btn, 'label', '')}",
            getattr(btn, "description", ""),
            getattr(btn, "handler", lambda: None),
            getattr(btn, "voice_hint", ""),
        )

    # Static prompts (prefer catalog if provided).
    static_prompts: List[str] = []
    if catalog:
        catalog_static = catalog.get("static_prompts", {}) or {}
        profiled = [
            entry.get("name", "")
            for entry in catalog_static.get("profiled", [])
            if entry.get("name")
        ]
        list_tokens = catalog_static.get("talon_list_tokens") or []
        static_prompts = [p for p in profiled + list_tokens if p]
    if not static_prompts:
        static_prompts = read_list_items("staticPrompt.talon-list")
    for prompt in static_prompts:
        _add(
            f"Prompt: {prompt}",
            "Open quick help for prompt",
            lambda p=prompt: actions.user.model_help_canvas_open_for_static_prompt(  # type: ignore[attr-defined]
                p
            ),
            voice_hint=f"Say: model run {prompt}",
        )

    # Axes (prefer catalog axis tokens).
    def _canonical_axis_tokens(axis_key: str, axis_file: str) -> List[str]:
        token_candidates: List[str] = []
        if catalog:
            axis_tokens = list((catalog.get("axes", {}).get(axis_key) or {}).keys())
            list_tokens = catalog.get("axis_list_tokens", {}).get(axis_key, []) or []
            token_candidates.extend(axis_tokens)
            token_candidates.extend(list_tokens)
        if not token_candidates:
            token_candidates = read_list_items(axis_file)
        seen: set[str] = set()
        for token in token_candidates:
            snapshot = axis_snapshot_from_axes({axis_key: [token]})
            canonical = snapshot.get(axis_key, []) or []
            if canonical:
                for value in canonical:
                    if value not in seen:
                        seen.add(value)
                continue
            cleaned = str(token).strip()
            if not cleaned or cleaned.lower().startswith("important:"):
                continue
            lowered = cleaned.lower()
            if lowered not in seen:
                seen.add(lowered)
        if not seen and token_candidates:
            for token in token_candidates:
                cleaned = str(token).strip()
                if not cleaned or cleaned.lower().startswith("important:"):
                    continue
                seen.add(cleaned.lower())
        return sorted(seen)

    axis_sources = {
        "Completeness": "completenessModifier.talon-list",
        "Scope": "scopeModifier.talon-list",
        "Method": "methodModifier.talon-list",
        "Form": "formModifier.talon-list",
        "Channel": "channelModifier.talon-list",
        "Directional": "directionalModifier.talon-list",
    }
    for axis_label, axis_file in axis_sources.items():
        axis_key = axis_label.lower()
        tokens = _canonical_axis_tokens(axis_key, axis_file)
        for token in tokens:
            _add(
                f"Axis ({axis_label}): {token}",
                "Open quick help",
                lambda _a=axis_key: actions.user.model_help_canvas_open()  # type: ignore[attr-defined]
                or None,
                voice_hint=f"Say: model run … {token}",
            )

    # Patterns and prompt presets.
    for pat in patterns:
        name = getattr(pat, "name", "")
        desc = getattr(pat, "description", "")
        _add(
            f"Pattern: {name}",
            desc,
            lambda n=name: actions.user.model_pattern_run_name(n),  # type: ignore[attr-defined]
            voice_hint=(
                f"Open patterns (model patterns), then say '{name.lower()}'"
                if name
                else ""
            ),
        )

    for preset in presets:
        name = getattr(preset, "name", "")
        desc = getattr(preset, "description", "")
        _add(
            f"Preset: {name}",
            desc,
            lambda n=name: actions.user.prompt_pattern_run_preset(n),  # type: ignore[attr-defined]
            voice_hint=(
                "Open prompt pattern menu (model pattern menu <prompt>), then "
                "choose this preset"
            ),
        )

    # Surface persona and intent presets so Help Hub search can jump directly to
    # the underlying stance commands. Prefer the orchestrator to keep aliases in
    # sync with GPT actions and canvases, with persona maps as a fallback.
    try:
        orchestrator = get_persona_intent_orchestrator()
    except Exception:
        orchestrator = None

    try:
        maps = persona_intent_maps()
    except Exception:
        maps = None

    persona_alias_map: Dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "persona_aliases", None):
        for alias, canonical in dict(orchestrator.persona_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                persona_alias_map[alias_key] = canonical_key
    if maps is not None and getattr(maps, "persona_preset_aliases", None):
        for alias, canonical in dict(maps.persona_preset_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                persona_alias_map.setdefault(alias_key, canonical_key)

    persona_axis_aliases: Dict[str, Dict[str, str]] = {}
    if maps is not None and getattr(maps, "persona_axis_tokens", None):
        for axis_key, alias_map in dict(maps.persona_axis_tokens or {}).items():
            axis_norm = str(axis_key or "").strip().lower()
            if not axis_norm:
                continue
            persona_axis_aliases[axis_norm] = {
                str(alias or "").strip().lower(): str(token or "").strip()
                for alias, token in dict(alias_map or {}).items()
                if str(alias or "").strip() and str(token or "").strip()
            }

    persona_items: List[tuple[str, object]] = []
    if orchestrator and getattr(orchestrator, "persona_presets", None):
        for key, preset in (orchestrator.persona_presets or {}).items():
            key_str = str(key or "").strip()
            if key_str:
                persona_items.append((key_str, preset))
    elif maps is not None and getattr(maps, "persona_presets", None):
        for key, preset in (maps.persona_presets or {}).items():
            key_str = str(key or "").strip()
            if key_str:
                persona_items.append((key_str, preset))

    def _persona_spoken(key: str, preset: object) -> str:
        spoken = (getattr(preset, "spoken", "") or "").strip()
        if spoken:
            return spoken
        for alias, canonical in persona_alias_map.items():
            if canonical == key and alias != key.lower():
                return alias.replace("_", " ")
        label_candidate = (getattr(preset, "label", "") or "").strip()
        if label_candidate:
            return label_candidate
        return key

    def _canonical_persona_axis(axis: str, raw_value: str) -> str:
        token = str(raw_value or "").strip()
        if not token:
            return ""
        if orchestrator:
            try:
                canonical = orchestrator.canonical_axis_token(axis, token)
            except Exception:
                canonical = ""
            if canonical:
                return canonical
        axis_key = (axis or "").strip().lower()
        if axis_key and axis_key in persona_axis_aliases:
            canonical = persona_axis_aliases[axis_key].get(token.lower())
            if canonical:
                return canonical
        return token

    for key, preset in persona_items:
        label = (getattr(preset, "label", "") or key).strip()
        spoken = _persona_spoken(key, preset)
        spoken_display = (spoken or "").strip() or label or key
        spoken_alias = spoken_display.strip().lower() or key.strip().lower()
        voice_hint = f"Say: persona {spoken_display}".strip()
        axis_tokens_map = {
            "voice": _canonical_persona_axis("voice", getattr(preset, "voice", "")),
            "audience": _canonical_persona_axis(
                "audience", getattr(preset, "audience", "")
            ),
            "tone": _canonical_persona_axis("tone", getattr(preset, "tone", "")),
        }
        axes_parts = [value for value in axis_tokens_map.values() if value]
        axes_desc = " · ".join(axes_parts) if axes_parts else "No explicit axes"
        entry_label = f"Persona preset: {label} (say: persona {spoken_display})"
        metadata = {
            "kind": "persona",
            "persona_key": key,
            "display_label": label,
            "spoken_alias": spoken_alias,
            "spoken_display": spoken_display,
            "axes_tokens": axes_parts,
            "axes_map": {
                axis: value for axis, value in axis_tokens_map.items() if value
            },
            "axes_summary": axes_desc,
            "voice_hint": voice_hint,
        }

        _add(
            entry_label,
            f"Apply persona stance ({axes_desc})",
            lambda preset_key=key: actions.user.persona_set_preset(preset_key),  # type: ignore[attr-defined]
            voice_hint=voice_hint,
            metadata=metadata,
        )

    intent_alias_map: Dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_aliases", None):
        for alias, canonical in dict(orchestrator.intent_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                intent_alias_map[alias_key] = canonical_key
    if maps is not None and getattr(maps, "intent_preset_aliases", None):
        for alias, canonical in dict(maps.intent_preset_aliases or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                intent_alias_map.setdefault(alias_key, canonical_key)

    intent_alias_display: Dict[str, str] = {}
    if maps is not None and getattr(maps, "intent_preset_aliases", None):
        for alias, canonical in dict(maps.intent_preset_aliases or {}).items():
            alias_original = str(alias or "").strip()
            canonical_key = str(canonical or "").strip()
            if alias_original and canonical_key:
                if alias_original.lower() != canonical_key.lower():
                    intent_alias_display.setdefault(canonical_key, alias_original)

    intent_synonyms: Dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_synonyms", None):
        for alias, canonical in dict(orchestrator.intent_synonyms or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                intent_synonyms[alias_key] = canonical_key
    if maps is not None and getattr(maps, "intent_synonyms", None):
        for alias, canonical in dict(maps.intent_synonyms or {}).items():
            alias_key = str(alias or "").strip().lower()
            canonical_key = str(canonical or "").strip()
            if alias_key and canonical_key:
                intent_synonyms.setdefault(alias_key, canonical_key)

    intent_display_lookup: Dict[str, str] = {}
    if orchestrator and getattr(orchestrator, "intent_display_map", None):
        for canonical, display in dict(orchestrator.intent_display_map or {}).items():
            canonical_key = str(canonical or "").strip()
            value = str(display or "").strip()
            if canonical_key and value:
                intent_display_lookup.setdefault(canonical_key, value)
                intent_display_lookup.setdefault(canonical_key.lower(), value)
    if maps is not None and getattr(maps, "intent_display_map", None):
        for canonical, display in dict(maps.intent_display_map or {}).items():
            canonical_key = str(canonical or "").strip()
            value = str(display or "").strip()
            if canonical_key and value:
                intent_display_lookup.setdefault(canonical_key, value)
                intent_display_lookup.setdefault(canonical_key.lower(), value)

    intent_items: List[tuple[str, object]] = []
    if orchestrator and getattr(orchestrator, "intent_presets", None):
        for key, preset in (orchestrator.intent_presets or {}).items():
            key_str = str(key or "").strip()
            if key_str:
                intent_items.append((key_str, preset))
    elif maps is not None and getattr(maps, "intent_presets", None):
        for key, preset in (maps.intent_presets or {}).items():
            key_str = str(key or "").strip()
            if key_str:
                intent_items.append((key_str, preset))

    def _canonical_intent_key(*aliases: str) -> str:
        for alias in aliases:
            candidate = str(alias or "").strip()
            if not candidate:
                continue
            lower = candidate.lower()
            canonical = intent_alias_map.get(lower)
            if canonical:
                return canonical
            synonym = intent_synonyms.get(lower)
            if synonym:
                return synonym
        return ""

    def _intent_spoken(
        key: str, preset: object, display: str, canonical_intent: str
    ) -> str:
        alias = next(
            (
                alias_key
                for alias_key, canonical in intent_alias_map.items()
                if canonical == key and alias_key != key.lower()
            ),
            "",
        )
        if alias:
            display_value = intent_display_lookup.get(key) or intent_display_lookup.get(
                key.lower()
            )
            if display_value and alias == display_value.lower():
                return display_value
            spoken_alias = intent_alias_display.get(key, alias)
            return spoken_alias.replace("_", " ")
        candidates = [getattr(preset, "spoken", "")]
        if maps is not None:
            candidates.extend([display, canonical_intent])
        else:
            candidates.extend([canonical_intent, display])
        candidates.append(key)
        for candidate in candidates:
            candidate_str = str(candidate or "").strip()
            if candidate_str:
                return candidate_str
        return key

    for key, preset in intent_items:
        canonical_key = (key or "").strip()
        display = (
            intent_display_lookup.get(canonical_key)
            or intent_display_lookup.get(canonical_key.lower())
            or (getattr(preset, "label", "") or "").strip()
            or canonical_key
        )
        canonical_intent = (
            _canonical_intent_key(getattr(preset, "intent", ""), canonical_key, display)
            or (getattr(preset, "intent", "") or canonical_key).strip()
        )
        spoken = _intent_spoken(canonical_key, preset, display, canonical_intent)
        spoken_display = (spoken or "").strip() or display or canonical_intent
        spoken_alias = spoken_display.strip().lower() or canonical_intent.lower()
        voice_hint = f"Say: intent {spoken_display}".strip()
        description = (
            f"Apply intent stance ({canonical_intent})"
            if canonical_intent
            else "Apply intent stance"
        )
        entry_label = f"Intent preset: {display} (say: intent {spoken_display})"
        metadata = {
            "kind": "intent",
            "intent_key": canonical_key,
            "canonical_intent": canonical_intent,
            "display_label": display,
            "spoken_alias": spoken_alias,
            "spoken_display": spoken_display,
            "voice_hint": voice_hint,
        }
        _add(
            entry_label,
            description,
            lambda preset_key=key: actions.user.intent_set_preset(preset_key),  # type: ignore[attr-defined]
            voice_hint=voice_hint,
            metadata=metadata,
        )

    return entries


def help_metadata_snapshot(entries: Sequence[HelpIndexEntry]) -> HelpMetadataSnapshot:
    persona_snapshots: list[HelpPersonaMetadata] = []
    intent_snapshots: list[HelpIntentMetadata] = []
    seen_persona_keys: set[str] = set()
    seen_intent_keys: set[str] = set()

    for entry in entries:
        metadata = entry.metadata or {}
        kind = str(metadata.get("kind") or "").strip().lower()
        if kind == "persona":
            key = str(metadata.get("persona_key") or "").strip()
            display_label = str(metadata.get("display_label") or "").strip() or key
            spoken_display = (
                str(metadata.get("spoken_display") or "").strip() or display_label
            )
            spoken_alias = (
                str(metadata.get("spoken_alias") or spoken_display).strip().lower()
            )
            axes_tokens = tuple(
                str(token or "").strip()
                for token in (metadata.get("axes_tokens") or [])
                if str(token or "").strip()
            )
            axes_summary = str(metadata.get("axes_summary") or "").strip()
            if not axes_summary and axes_tokens:
                axes_summary = " · ".join(axes_tokens)
            voice_hint = str(
                metadata.get("voice_hint") or entry.voice_hint or ""
            ).strip()
            if not voice_hint and spoken_display:
                voice_hint = f"Say: persona {spoken_display}".strip()
            if not key:
                key = spoken_alias or spoken_display.lower()
            if not key or key in seen_persona_keys:
                continue
            persona_snapshots.append(
                HelpPersonaMetadata(
                    key=key,
                    display_label=display_label or key,
                    spoken_display=spoken_display or display_label or key,
                    spoken_alias=spoken_alias
                    or (spoken_display or display_label or key).lower(),
                    axes_summary=axes_summary or "No explicit axes",
                    axes_tokens=axes_tokens,
                    voice_hint=voice_hint,
                )
            )
            seen_persona_keys.add(key)
        elif kind == "intent":
            key = str(metadata.get("intent_key") or "").strip()
            display_label = str(metadata.get("display_label") or "").strip() or key
            canonical_intent = (
                str(metadata.get("canonical_intent") or "").strip() or key
            )
            spoken_display = (
                str(metadata.get("spoken_display") or "").strip() or display_label
            )
            spoken_alias = (
                str(metadata.get("spoken_alias") or spoken_display).strip().lower()
            )
            voice_hint = str(
                metadata.get("voice_hint") or entry.voice_hint or ""
            ).strip()
            if not voice_hint and spoken_display:
                voice_hint = f"Say: intent {spoken_display}".strip()
            if not key:
                key = canonical_intent or spoken_alias
            if not key or key in seen_intent_keys:
                continue
            intent_snapshots.append(
                HelpIntentMetadata(
                    key=key,
                    display_label=display_label or key,
                    canonical_intent=canonical_intent or key,
                    spoken_display=spoken_display
                    or display_label
                    or canonical_intent
                    or key,
                    spoken_alias=spoken_alias
                    or (
                        spoken_display or display_label or canonical_intent or key
                    ).lower(),
                    voice_hint=voice_hint,
                )
            )
            seen_intent_keys.add(key)

    return HelpMetadataSnapshot(
        personas=tuple(persona_snapshots),
        intents=tuple(intent_snapshots),
    )


def help_search(query: str, index: Sequence[Any]) -> List[Any]:
    """HelpDomain façade: derive search results from a query and index.

    Current semantics mirror the legacy Help Hub behaviour: a case-insensitive
    substring match against item labels. Callers are expected to pass
    objects with a ``label`` attribute (for example ``HubButton``).
    """

    norm = (query or "").strip().lower()
    if not norm:
        return []
    results: List[Any] = []
    for item in index:
        label = getattr(item, "label", "")
        if norm in str(label).lower():
            results.append(item)
    return results


def help_focusable_items(
    filter_text: str,
    buttons: Sequence[Any],
    results: Sequence[Any],
) -> List[Tuple[str, str]]:
    """HelpDomain façade: compute ordered (kind,label) focus targets.

    This mirrors the existing Help Hub behaviour used by keyboard navigation:
    - When a non-empty filter is present, only results are focusable.
    - When no filter is present, hub buttons come first, then results.
    """

    items: List[Tuple[str, str]] = []
    if (filter_text or "").strip():
        for res in results:
            items.append(("res", getattr(res, "label", "")))
    else:
        for btn in buttons:
            items.append(("btn", getattr(btn, "label", "")))
        for res in results:
            items.append(("res", getattr(res, "label", "")))
    return items


def help_next_focus_label(
    current: str, delta: int, items: List[Tuple[str, str]]
) -> str:
    """HelpDomain façade: navigation step over focusable items.

    Computes the next ``"kind:label"`` identifier given the current focus
    label, a step delta, and the ordered focusable items. Behaviour matches the
    legacy ``_next_focus_label`` helper in ``helpHub``.
    """

    if not items:
        return ""
    try:
        idx = next(
            i for i, (kind, label) in enumerate(items) if f"{kind}:{label}" == current
        )
    except StopIteration:
        # If nothing focused yet, start before the first item when moving
        # forward, or just past the last item when moving backward.
        idx = -1 if delta > 0 else len(items)
    idx = (idx + delta) % len(items)
    kind, label = items[idx]
    return f"{kind}:{label}"


def help_activation_target(
    current: str,
    buttons: Sequence[Any],
    results: Sequence[Any],
) -> Any | None:
    """HelpDomain façade: resolve the activation target for a focus label.

    Given the current ``"kind:label"`` focus identifier and the available hub
    buttons and search results, return the underlying object whose handler
    should be invoked, or ``None`` if there is no matching target.
    """

    if not current:
        return None
    if current.startswith("btn:"):
        target = current[len("btn:") :]
        for btn in buttons:
            if getattr(btn, "label", "") == target:
                return btn
        return None
    if current.startswith("res:"):
        target = current[len("res:") :]
        for res in results:
            if getattr(res, "label", "") == target:
                return res
        return None
    return None


def help_edit_filter_text(text: str, key: str, *, alt: bool, cmd: bool) -> str:
    """HelpDomain façade: apply a key edit to the filter text.

    This mirrors the Help Hub semantics for editing the filter field:

    - ``backspace``/``back`` without modifiers delete a single character.
    - ``delete``/``backspace`` with ``alt`` delete the last word.
    - ``delete``/``backspace`` with ``cmd`` clear the entire filter.
    - Printable single-character keys append to the filter.

    Modifiers are provided explicitly so callers can normalise Talon-specific
    event shapes before invoking this helper.
    """

    norm_key = (key or "").lower()

    # Word or full clear based on modifiers.
    if norm_key in ("delete", "backspace") and alt:
        text = (text or "").rstrip()
        stripped = text.rstrip()
        parts = stripped.rsplit(" ", 1)
        return parts[0] if len(parts) == 2 else ""

    if norm_key in ("delete", "backspace") and cmd:
        return ""

    # Single-character delete without modifiers.
    if norm_key in ("backspace", "back") and not alt and not cmd:
        return (text or "")[:-1]

    # Printable single-character append.
    if len(norm_key) == 1 and 32 <= ord(norm_key) <= 126:
        return (text or "") + norm_key

    return text
