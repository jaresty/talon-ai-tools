from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from .axisConfig import AXIS_KEY_TO_VALUE
from .staticPromptConfig import (
    STATIC_PROMPT_CONFIG,
    get_static_prompt_axes as _get_static_prompt_axes,
    get_static_prompt_profile as _get_static_prompt_profile,
    static_prompt_catalog as _static_prompt_catalog,
    static_prompt_description_overrides as _static_prompt_description_overrides,
)

# Map axis names to their Talon list filenames so we can validate drift between
# axisConfig and list tokens without each consumer re-implementing file parsing.
_AXIS_LIST_FILES: Dict[str, str] = {
    "completeness": "completenessModifier.talon-list",
    "scope": "scopeModifier.talon-list",
    "method": "methodModifier.talon-list",
    "form": "formModifier.talon-list",
    "channel": "channelModifier.talon-list",
    "directional": "directionalModifier.talon-list",
}


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
    """Return Talon list tokens for a given axis name, if a mapped list exists."""

    filename = _AXIS_LIST_FILES.get(axis_name)
    if not filename:
        return []
    base_dir = Path(lists_dir) if lists_dir else Path(__file__).resolve().parent.parent / "GPT" / "lists"
    return _read_list_tokens(base_dir / filename)


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
    - axis_list_tokens: Talon list tokens for axes with mapped list files.
    - static_prompts: catalog view from staticPromptConfig.
    - static_prompt_descriptions: description overrides for docs/help consumers.
    - static_prompt_profiles: raw profiles for callers that need direct access.
    """

    axis_lists: Dict[str, List[str]] = {}
    for axis_name in _AXIS_LIST_FILES:
        axis_lists[axis_name] = axis_list_tokens(axis_name, lists_dir=lists_dir)

    return {
        "axes": AXIS_KEY_TO_VALUE,
        "axis_list_tokens": axis_lists,
        "static_prompts": static_prompt_catalog(static_prompt_list_path),
        "static_prompt_descriptions": static_prompt_description_overrides(),
        "static_prompt_profiles": STATIC_PROMPT_CONFIG,
    }
