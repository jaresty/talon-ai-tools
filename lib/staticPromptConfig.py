from __future__ import annotations

from pathlib import Path
from typing import Set, TypedDict, Union

# Central configuration for static prompts:
# - Each key is a canonical static prompt value (Talon list file is optional/auxiliary).
# - "description" provides the human-readable Task line and help text.
# - Optional completeness/scope/method/form/channel fields define per-prompt axis profiles.


class StaticPromptProfile(TypedDict, total=False):
    description: str
    completeness: str
    # Scope, method, form, and channel may be expressed as a single token or a
    # small list of tokens; callers are responsible for any further normalisation.
    scope: Union[str, list[str]]
    method: Union[str, list[str]]
    form: Union[str, list[str]]
    channel: Union[str, list[str]]


COMPLETENESS_FREEFORM_ALLOWLIST: Set[str] = {"path"}


def completeness_freeform_allowlist() -> Set[str]:
    """Return the allowed non-axis completeness hints for static prompts."""

    return set(COMPLETENESS_FREEFORM_ALLOWLIST)


STATIC_PROMPT_CONFIG: dict[str, StaticPromptProfile] = {
    # Per ADR 0088: Universal task taxonomy with 10 single-syllable success primitives.
    # All specialized tasks (46 total) retired in favor of composable universal tasks + axis values.
    # Migration guide: docs/adr/0088-adopt-universal-task-taxonomy.md
    # Universal task types (all single-syllable, pronounceable for voice workflows)
    "make": {
        "description": "The response creates new content that did not previously exist, based on the input and constraints.",
        "completeness": "full",
    },
    "fix": {
        "description": "The response changes the form or presentation of given content while keeping its intended meaning. Note: in bar's grammar, `fix` is a reformat task, not a debugging task. For work that involves correcting defects or errors, use `make` or `show` paired with diagnostic method tokens (`diagnose`, `inversion`, `adversarial`).",
        "completeness": "full",
    },
    "pull": {
        "description": "The response selects or extracts a subset of the given information without altering its substance.",
        "completeness": "gist",
    },
    "sort": {
        "description": "The response arranges items into categories or an order using a specified or inferred scheme.",
    },
    "diff": {
        "description": "The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.",
    },
    "show": {
        "description": "The response explains or describes the subject for the stated audience.",
    },
    "probe": {
        "description": "The response analyzes the subject to surface structure, assumptions, or implications beyond restatement.",
        "method": "analysis",
    },
    "pick": {
        "description": "The response chooses one or more options from a set of alternatives.",
        "method": "converge",
    },
    "plan": {
        "description": "The response proposes steps, structure, or strategy to move from the current state toward a stated goal.",
    },
    "sim": {
        "description": "The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.",
    },
    "check": {
        "description": "The response evaluates the subject against a condition and reports whether it passes or fails.",
    },
}

_AXES = ("completeness", "scope", "method", "form", "channel")


def get_static_prompt_profile(name: str) -> StaticPromptProfile | None:
    """Return the StaticPromptProfile for a given key, if present.

    This helper provides a single place to look up profile metadata so that
    callers (GUI, settings, docs) do not need to reach into STATIC_PROMPT_CONFIG
    directly.
    """
    return STATIC_PROMPT_CONFIG.get(name)


def get_static_prompt_axes(name: str) -> dict[str, object]:
    """Return the axis values defined for a static prompt profile.

    The result maps axis name -> configured value for the axes present in the
    profile (a subset of: completeness, scope, method, form, channel). Unknown prompts
    return an empty dict.

    - `completeness` remains a single short token.
    - `scope`, `method`, `form`, and `channel` may be configured as a single token or
      as a small list of tokens; callers that care about set semantics should
      normalise these values (for example, via helpers in the axis-mapping
      domain).
    """
    profile = STATIC_PROMPT_CONFIG.get(name)
    if profile is None:
        return {}
    axes: dict[str, object] = {}
    for axis in _AXES:
        value = profile.get(axis)
        if not value:
            continue
        # Completeness remains scalar; other axes may be a single token or a list.
        if axis == "completeness":
            axes[axis] = str(value)
        else:
            if isinstance(value, list):
                tokens = [str(v).strip() for v in value if str(v).strip()]
            else:
                tokens = [str(value).strip()]
            if tokens:
                axes[axis] = tokens
    return axes


class StaticPromptCatalogEntry(TypedDict):
    name: str
    description: str
    axes: dict[str, object]


class StaticPromptCatalog(TypedDict):
    profiled: list[StaticPromptCatalogEntry]
    talon_list_tokens: list[str]
    unprofiled_tokens: list[str]


def static_prompt_description_overrides() -> dict[str, str]:
    """Return name->description map for static prompts.

    Docs and README/help surfaces should use this helper rather than reaching
    into STATIC_PROMPT_CONFIG directly so that description semantics remain
    centralised in this module.
    """
    overrides: dict[str, str] = {}
    for name, profile in STATIC_PROMPT_CONFIG.items():
        description = str(profile.get("description", "")).strip()
        if description:
            overrides[name] = description
    return overrides


def _read_static_prompt_tokens(
    static_prompt_list_path: str | Path | None = None,
) -> list[str]:
    """Return the token names from staticPrompt.talon-list, if present."""
    if static_prompt_list_path is None:
        current_dir = Path(__file__).resolve().parent
        static_prompt_list_path = (
            current_dir.parent / "GPT" / "lists" / "staticPrompt.talon-list"
        )
    path = Path(static_prompt_list_path)
    tokens: list[str] = []
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


def static_prompt_catalog(
    static_prompt_list_path: str | Path | None = None,
) -> StaticPromptCatalog:
    """Return a catalog view that unifies profiles and Talon list tokens.

    The catalog is the SSOT for docs and drift checks:
    - profiled entries come from STATIC_PROMPT_CONFIG with axes resolved via
      `get_static_prompt_axes`.
    - talon_list_tokens reflects staticPrompt.talon-list entries when present,
      merged with SSOT tokens so missing files do not hide profiles.
    - unprofiled_tokens lists tokens present only in the Talon list (when present)
      but not in the profiled set (so docs can mention the token vocabulary).
    - If static_prompt_list_path is falsy (for example, ""), skip on-disk list
      reads and rely solely on the SSOT.
    """
    list_tokens: list[str] = []
    if static_prompt_list_path:
        list_tokens = _read_static_prompt_tokens(static_prompt_list_path)
    # Merge list tokens with SSOT tokens so partial lists do not hide config entries.
    talon_tokens: list[str] = []
    seen: set[str] = set()
    for token in list_tokens + list(STATIC_PROMPT_CONFIG.keys()):
        if token and token not in seen:
            talon_tokens.append(token)
            seen.add(token)
    profiled: list[StaticPromptCatalogEntry] = []
    for name in STATIC_PROMPT_CONFIG.keys():
        profile = get_static_prompt_profile(name)
        if profile is None:
            continue
        profiled.append(
            {
                "name": name,
                "description": profile.get("description", "").strip(),
                "axes": get_static_prompt_axes(name),
            }
        )
    profiled_names = {entry["name"] for entry in profiled}
    unprofiled_tokens = [token for token in talon_tokens if token not in profiled_names]
    return {
        "profiled": profiled,
        "talon_list_tokens": talon_tokens,
        "unprofiled_tokens": unprofiled_tokens,
    }


class StaticPromptSettingsEntry(TypedDict):
    """Settings/docs-facing view of a static prompt profile.

    This facade is intended for Talon settings GUIs and help surfaces that
    need a simple mapping from static prompt name to description and axes,
    reusing the same profile/cross-surface semantics as `static_prompt_catalog`.
    """

    description: str
    axes: dict[str, object]


def static_prompt_settings_catalog() -> dict[str, StaticPromptSettingsEntry]:
    """Return a settings-friendly catalog of static prompts.

    The result maps each profiled static prompt name to a small entry
    containing its human-readable description and axis profile as surfaced
    by `get_static_prompt_axes`.
    """

    catalog = static_prompt_catalog()
    result: dict[str, StaticPromptSettingsEntry] = {}
    for entry in catalog["profiled"]:
        name = entry["name"]
        result[name] = {
            "description": entry.get("description", "").strip(),
            "axes": entry.get("axes", {}),
        }
    return result
