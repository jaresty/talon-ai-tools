from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple

from talon import actions


@dataclass(frozen=True)
class HelpIndexEntry:
    label: str
    description: str
    handler: Callable[[], None]
    voice_hint: str = ""


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
    ) -> None:
        entries.append(
            HelpIndexEntry(
                label=label,
                description=desc,
                handler=handler,
                voice_hint=voice_hint,
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
    axis_sources = {
        "Completeness": "completenessModifier.talon-list",
        "Scope": "scopeModifier.talon-list",
        "Method": "methodModifier.talon-list",
        "Form": "formModifier.talon-list",
        "Channel": "channelModifier.talon-list",
        "Directional": "directionalModifier.talon-list",
    }
    for axis_label, axis_file in axis_sources.items():
        tokens: List[str] = []
        if catalog:
            axis_key = axis_label.lower()
            axis_tokens = list((catalog.get("axes", {}).get(axis_key) or {}).keys())
            list_tokens = catalog.get("axis_list_tokens", {}).get(axis_key, []) if catalog else []
            tokens = [t for t in list_tokens or axis_tokens if t]
        if not tokens:
            tokens = read_list_items(axis_file)
        for token in tokens:
            _add(
                f"Axis ({axis_label}): {token}",
                "Open quick help",
                lambda _a=axis_label.lower(): actions.user.model_help_canvas_open()  # type: ignore[attr-defined]
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

    return entries


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
