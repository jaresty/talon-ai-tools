from __future__ import annotations

import threading
from importlib import reload
from pathlib import Path
from typing import Dict, List

from . import axisConfig
from .staticPromptConfig import (
    STATIC_PROMPT_CONFIG,
    get_static_prompt_axes as _get_static_prompt_axes,
    get_static_prompt_profile as _get_static_prompt_profile,
    static_prompt_catalog as _static_prompt_catalog,
    static_prompt_description_overrides as _static_prompt_description_overrides,
    static_prompt_guidance_overrides as _static_prompt_guidance_overrides,
    static_prompt_label_overrides as _static_prompt_label_overrides,
    static_prompt_use_when_overrides as _static_prompt_use_when_overrides,
)

# Map axis names to their Talon list filenames (optional/auxiliary) so we can
# validate drift between axisConfig and list tokens without re-implementing
# file parsing. Catalog remains the SSOT; lists are used only when present.
_AXIS_LIST_FILES: Dict[str, str] = {
    "completeness": "completenessModifier.talon-list",
    "scope": "scopeModifier.talon-list",
    "method": "methodModifier.talon-list",
    "form": "formModifier.talon-list",
    "channel": "channelModifier.talon-list",
    "directional": "directionalModifier.talon-list",
}

_LEGACY_STYLE_LIST = "styleModifier.talon-list"


_axis_config_cache: Dict[str, Dict[str, str]] | None = None
_axis_config_source: str | None = None
_axis_config_mtime: float | None = None
_axis_config_lock = threading.Lock()


def _axis_config_map() -> Dict[str, Dict[str, str]]:
    """Return the latest axis config map, reloading axisConfig when it changes."""

    global _axis_config_cache, _axis_config_source, _axis_config_mtime

    module_file = getattr(axisConfig, "__file__", None)
    resolved_path: str | None = None
    mtime: float | None = None
    if module_file:
        try:
            resolved_path = str(Path(module_file).resolve())
        except Exception:
            resolved_path = str(module_file)
        try:
            mtime = Path(module_file).stat().st_mtime
        except OSError:
            mtime = None

    with _axis_config_lock:
        needs_reload = _axis_config_cache is None
        if not needs_reload and resolved_path and resolved_path != _axis_config_source:
            needs_reload = True
        if not needs_reload and mtime is not None and mtime != _axis_config_mtime:
            needs_reload = True

        if needs_reload:
            try:
                reload(axisConfig)
            except Exception:
                if _axis_config_cache is None:
                    return getattr(axisConfig, "AXIS_KEY_TO_VALUE", {}) or {}
            else:
                _axis_config_cache = getattr(axisConfig, "AXIS_KEY_TO_VALUE", {}) or {}
                _axis_config_source = resolved_path
                _axis_config_mtime = mtime

        cache = _axis_config_cache

    return cache or getattr(axisConfig, "AXIS_KEY_TO_VALUE", {}) or {}


def _read_list_tokens(path: Path) -> List[str]:
    """Parse Talon list tokens from a list file, ignoring comments and headers."""

    tokens: List[str] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#") or s.startswith("list:") or s == "-":
                    continue
                if ":" not in s:
                    continue
                key, _ = s.split(":", 1)
                key = key.strip()
                if key:
                    tokens.append(key)
    except FileNotFoundError:
        return []
    return tokens


def axis_list_tokens(axis_name: str, lists_dir: str | Path | None = None) -> List[str]:
    """Return tokens for a given axis name, preferring Talon lists when present.

    - Primary source: AXIS_KEY_TO_VALUE (catalog/SSOT).
    - Optional: if a matching Talon list file exists, use its tokens so local
      overrides or pending edits are visible; otherwise fall back to SSOT keys.
    """

    filename = _AXIS_LIST_FILES.get(axis_name)
    ssot_tokens = list((_axis_config_map().get(axis_name) or {}).keys())
    if not filename:
        return ssot_tokens
    # When lists_dir is falsy/None, skip on-disk list reads (catalog-only).
    if not lists_dir:
        return ssot_tokens
    base_dir = (
        Path(lists_dir)
        if lists_dir
        else Path(__file__).resolve().parent.parent / "GPT" / "lists"
    )
    tokens = _read_list_tokens(base_dir / filename)
    if not tokens:
        return ssot_tokens
    # Merge list tokens with SSOT tokens so missing entries do not disappear
    # when a list file is partial. Preserve list order, then append any missing
    # SSOT tokens to keep drift visible in validators.
    merged: list[str] = []
    seen: set[str] = set()
    for token in tokens + ssot_tokens:
        if token and token not in seen:
            merged.append(token)
            seen.add(token)
    return merged


def get_static_prompt_profile(name: str):
    """Facade: static prompt profile lookup."""

    return _get_static_prompt_profile(name)


def get_static_prompt_axes(name: str) -> dict[str, object]:
    """Facade: static prompt axis lookup."""

    return _get_static_prompt_axes(name)


def static_prompt_catalog(static_prompt_list_path: str | Path | None = None):
    """Facade: static prompt catalog view (profiles + Talon list tokens)."""

    return _static_prompt_catalog(static_prompt_list_path)


def static_prompt_description_overrides() -> dict[str, str]:
    """Facade: description overrides for static prompts."""

    return _static_prompt_description_overrides()


def axis_catalog(
    lists_dir: str | Path | None = None,
    static_prompt_list_path: str | Path | None = None,
) -> dict[str, object]:
    """Return a consolidated view of axis tokens, Talon lists, and static prompts.

    - axes: raw axis token map from axisConfig.
    - axis_list_tokens: Talon list tokens for axes with mapped list files (SSOT
      when lists are absent).
    - static_prompts: catalog view from staticPromptConfig.
    - static_prompt_descriptions: description overrides for docs/help consumers.
    - static_prompt_profiles: raw profiles for callers that need direct access.
    """

    axis_map = _axis_config_map()
    if "style" in axis_map:
        raise ValueError(
            "style axis is removed; drop legacy style before building the axis catalog."
        )

    axis_lists: Dict[str, List[str]] = {}
    for axis_name in _AXIS_LIST_FILES:
        axis_lists[axis_name] = axis_list_tokens(axis_name, lists_dir=lists_dir)

    # Guard against accidental reintroduction of the legacy style list.
    if lists_dir:
        base_dir = Path(lists_dir)
        style_list_path = base_dir / _LEGACY_STYLE_LIST
        if style_list_path.exists():
            style_tokens = _read_list_tokens(style_list_path)
            if style_tokens:
                raise ValueError(
                    f"styleModifier list is removed after form/channel split (found tokens: {style_tokens})"
                )

    return {
        "axes": axis_map,
        "axis_list_tokens": axis_lists,
        "axis_labels": {
            axis: axisConfig.axis_key_to_label_map(axis)
            for axis in axis_map
        },
        "axis_guidance": {
            axis: axisConfig.axis_key_to_guidance_map(axis)
            for axis in axis_map
        },
        "axis_use_when": {
            axis: axisConfig.axis_key_to_use_when_map(axis)
            for axis in axis_map
        },
        "static_prompts": static_prompt_catalog(
            static_prompt_list_path if lists_dir else ""
        ),
        "static_prompt_descriptions": static_prompt_description_overrides(),
        "static_prompt_labels": _static_prompt_label_overrides(),
        "static_prompt_guidance": _static_prompt_guidance_overrides(),
        "static_prompt_use_when": _static_prompt_use_when_overrides(),
        "static_prompt_profiles": STATIC_PROMPT_CONFIG,
        "usage_patterns": axisConfig.get_usage_patterns(),
    }


def serialize_axis_config(
    lists_dir: str | Path | None = None,
    include_axis_lists: bool = True,
    include_static_prompts: bool = True,
) -> dict[str, object]:
    """Produce a canonical axis config payload for regen/exports.

    - axes: SSOT axis tokens from AXIS_KEY_TO_VALUE (style excluded).
    - axis_list_tokens: optional Talon list token view (merged with SSOT).
    - static prompt catalog: optional static prompt payloads from the SSOT.
    """

    catalog = axis_catalog(lists_dir=lists_dir)
    payload: dict[str, object] = {
        "axes": catalog["axes"],
        "axis_labels": catalog["axis_labels"],
        "axis_guidance": catalog["axis_guidance"],
        "axis_use_when": catalog["axis_use_when"],
    }
    if include_axis_lists:
        payload["axis_list_tokens"] = catalog["axis_list_tokens"]
    if include_static_prompts:
        payload["static_prompts"] = catalog["static_prompts"]
        payload["static_prompt_descriptions"] = catalog["static_prompt_descriptions"]
        payload["static_prompt_profiles"] = catalog["static_prompt_profiles"]
    payload["usage_patterns"] = catalog["usage_patterns"]
    return payload
