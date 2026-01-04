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
    # Default "infer the task" prompt used when no explicit staticPrompt
    # is provided. This keeps the visible Task description consistent with
    # the historical fallback while giving it a concise recipe token.
    "infer": {
        "description": "The response infers the task without being told what to do.",
    },
    # Analysis, structure, and perspective prompts (description-only profiles).
    "describe": {
        "description": "The response describes the subject objectively.",
    },
    "undefined": {
        "description": "The response lists only the undefined terms.",
    },
    "who": {
        "description": "The response explains who is involved.",
    },
    "what": {
        "description": "The response explains what is happening.",
    },
    "when": {
        "description": "The response explains when it occurs.",
    },
    "where": {
        "description": "The response explains where it takes place.",
    },
    "why": {
        "description": "The response explains why it matters.",
    },
    "how": {
        "description": "The response explains how it works.",
    },
    "assumption": {
        "description": "The response identifies and explains the assumptions behind the subject.",
    },
    "objectivity": {
        "description": "The response assesses objectivity and includes relevant examples.",
    },
    "knowledge": {
        "description": "The response cites relevant academic or industry fields of knowledge, explaining why each applies and what perspective it offers.",
    },
    "taste": {
        "description": (
            "The response evaluates the subject's taste by analysing harmony, proportion, restraint, authenticity, and cultural or historical appropriateness, explaining strengths, weaknesses, and contextual fit."
        ),
    },
    "tao": {
        "description": (
            "The response classifies the subject through Taoist philosophy by relating it to Dao, De, Yin/Yang, Wu Wei, Ziran, Pu, Qi, and Li, noting which apply and why."
        ),
    },
    # Planning, product, and execution prompts (description-only profiles).
    "product": {
        "description": "The response frames the subject through a product lens.",
        "completeness": "gist",
        "method": "steps",
        "form": "bullets",
        "scope": "focus",
    },
    "metrics": {
        "description": "The response lists metrics that drive the outcomes and includes concrete examples.",
        "completeness": "gist",
        "method": "steps",
        "form": "bullets",
        "scope": "focus",
    },
    "operations": {
        "description": "The response identifies an Operations Research or management science concept that appropriately applies.",
        "completeness": "gist",
        "method": "rigor",
        "scope": "focus",
    },
    "jobs": {
        "description": "The response highlights the key Jobs To Be Done, desired outcomes, and forces shaping them.",
        "completeness": "gist",
        "method": "analysis",
        "form": "bullets",
        "scope": "focus",
    },
    "value": {
        "description": "The response describes user or customer value and impact in a concise narrative.",
        "completeness": "gist",
        "method": "analysis",
        "form": "bullets",
        "scope": "focus",
    },
    "pain": {
        "description": "The response lists pain points and obstacles, noting brief prioritisation or severity.",
        "completeness": "gist",
        "method": "filter",
        "form": "bullets",
        "scope": "focus",
    },
    "done": {
        "description": "The response provides a clear Definition of Done or acceptance criteria as a checklist.",
        "completeness": "full",
        "method": "structure",
        "form": "checklist",
        "scope": "actions",
    },
    "team": {
        "description": "The response maps team roles, responsibilities, and handoffs needed for the work.",
        "completeness": "gist",
        "method": "mapping",
        "form": "table",
        "scope": "system",
    },
    # Exploration, critique, and reflection prompts (description-only profiles).
    "challenge": {
        "description": "The response challenges the subject with questions aimed at improvement.",
    },
    "critique": {
        "description": "The response explains what is wrong with the subject and why it fails.",
    },
    "retro": {
        "description": "The response guides introspection or reflection on the subject.",
    },
    "easier": {
        "description": "The response proposes an approach that accomplishes the goal on a smaller timescale.",
    },
    "true": {
        "description": "The response evaluates whether the statement is true using the available information.",
    },
    "relevant": {
        "description": "The response identifies the relevant elements of the situation.",
        "completeness": "gist",
        "method": "filter",
        "form": "bullets",
        "scope": "focus",
    },
    "misunderstood": {
        "description": "The response surfaces what is misunderstood in this situation.",
        "completeness": "gist",
        "method": "filter",
        "form": "bullets",
        "scope": "focus",
    },
    "risky": {
        "description": "The response highlights the risks and explains why they matter.",
        "completeness": "gist",
        "method": "filter",
        "form": "bullets",
        "scope": "focus",
    },
    # Transformation and reformatting prompts (description-only profiles).
    "split": {
        "description": "The response separates topics into clear sections and returns only reformatted text.",
    },
    "match": {
        "description": "The response rewrites the content to match the provided style and returns only the modified text.",
    },
    "blend": {
        "description": (
            "The response combines source and destination texts coherently, follows the destination’s structure while reordering and renaming as needed, and returns only the integrated text, treating additional_source as the destination."
        ),
    },
    "join": {
        "description": "The response merges the content into a single coherent piece and removes redundancy.",
    },
    "context": {
        "description": "The response adds LLM-ready context without rewriting the main text.",
        "completeness": "gist",
        "method": "contextualise",
        "scope": "focus",
    },
    # Mathematical and abstract lenses (description-only profiles).
    "math": {
        "description": "The response considers mathematical fields that apply to the subject and specifies which ones are used.",
    },
    "orthogonal": {
        "description": "The response identifies what is orthogonal in this situation.",
    },
    "bud": {
        "description": "The response applies addition or subtraction style reasoning in a non-numerical way.",
    },
    "boom": {
        "description": "The response applies limit or continuity style reasoning in a non-numerical way.",
    },
    "meld": {
        "description": "The response applies set theory reasoning in a non-numerical way.",
    },
    "order": {
        "description": "The response applies order or lattice theory reasoning in a non-numerical way.",
    },
    "logic": {
        "description": "The response applies propositional or predicate logic reasoning in a non-numerical way.",
    },
    "probability": {
        "description": "The response applies probability or statistics reasoning in a non-numerical way.",
    },
    "recurrence": {
        "description": "The response derives the recurrence relation of the idea and explains its consequences in plain language.",
    },
    "map": {
        "description": (
            "The response uses data mapping and transformation concepts: it identifies source and target schemas, specifies transformation rules, and describes information flow, including loss, duplication, or enrichment."
        ),
    },
    "mod": {
        "description": "The response treats the second idea as a modulus for the first in a non-numerical analogy.",
    },
    "dimension": {
        "description": "The response expands the metaphorical dimensions of the subject and describes each axis.",
    },
    "rotation": {
        "description": "The response presents the 90-degree metaphorical rotation of the concept.",
    },
    "reflection": {
        "description": "The response presents the metaphorical reflection of the concept.",
    },
    "invert": {
        "description": "The response inverts the concept to reveal its negative space.",
    },
    "graph": {
        "description": (
            "The response applies graph or tree theory reasoning non-numerically by identifying nodes and edges, describing direction, weight, and centrality, and explaining how structure shapes flow or dependency."
        ),
    },
    "grove": {
        "description": "The response applies integral or derivative concepts in a non-numerical way.",
    },
    "dub": {
        "description": "The response applies power or root concepts in a non-numerical way.",
    },
    "drum": {
        "description": "The response applies multiplication or division concepts in a non-numerical way.",
    },
    "document": {
        "description": "The response lists document or writing formats, explains why each fits, and states what perspective each reveals.",
    },
    "com b": {
        "description": (
            "The response analyses the subject using the COM-B model (Capability, Opportunity, Motivation, Behavior), identifies key enablers and barriers across those dimensions, maps them to Behavior Change Wheel intervention functions and behaviour change techniques, and outlines a minimal, testable implementation and evaluation plan."
        ),
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    # Strategy, mapping, and dependency prompts (description-only profiles).
    "wardley": {
        "description": (
            "The response produces a Wardley Map by identifying users, needs, and components, expressing it as a Markdown table (rows as visibility levels, columns as evolution stages) with a concise summary of dependencies and key strategic insights."
        ),
        "completeness": "full",
        "method": "steps",
        "form": "table",
        "scope": "focus",
    },
    "dependency": {
        "description": "The response lists dependencies and the items they rely on.",
        "scope": "relations",
    },
    "cochange": {
        "description": "The response shows how each subject directly cochanges with the others.",
        "scope": "relations",
    },
    "interact": {
        "description": "The response explains how the elements interact.",
        "scope": "relations",
    },
    "dependent": {
        "description": "The response explains how the elements depend on one another.",
        "scope": "relations",
    },
    "independent": {
        "description": "The response explains how the elements remain independent.",
        "scope": "relations",
    },
    "parallel": {
        "description": "The response describes problems that could arise if the items are parallelized.",
        "scope": "relations",
    },
    "unknown": {
        "description": "The response imagines critical unknown unknowns and explains how they might impact the outcome.",
    },
    "jim": {
        "description": (
            "The response analyses the subject for connascence (Strength, Degree, Locality), identifies its type, computes Severity = Strength × Degree ÷ Locality, and proposes remedies to reduce harmful connascence."
        ),
    },
    "domain": {
        "description": (
            "The response performs a connascence-driven discovery of business domains by grouping elements where multiple forms of connascence converge, describing obligations and change scenarios, and recommending boundary-strengthening remedies."
        ),
    },
    "tune": {
        "description": "The response evaluates the design through the Concordance Frame, focusing on visibility, scope, and dependency volatility that must stay aligned.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "melody": {
        "description": (
            "The response analyses the system for clusters that share coordination patterns in visibility, scope, and volatility, infers the shared intent or 'tune', and recommends ways to clarify or strengthen domains by reducing coordination cost."
        ),
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "constraints": {
        "description": "The response identifies the system's key constraint, describes behaviours it promotes and discourages, and discusses how to balance it for long-term health.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "effects": {
        "description": "The response describes the second- and third-order effects of the situation or change.",
        "completeness": "full",
        "method": "steps",
        "scope": "dynamics",
    },
    "fix": {
        "description": "The response corrects grammar, spelling, and minor style issues while preserving meaning and tone, returning only the modified text.",
        "completeness": "full",
        "scope": "narrow",
    },
    "todo": {
        "description": "The response formats the content as a todo list.",
        "completeness": "gist",
        "method": "steps",
        "form": "checklist",
        "scope": "actions",
    },
    "bridge": {
        "description": "The response outlines a path from the current state to the desired situation described in the additional source.",
        "completeness": "path",
        "method": "steps",
        "scope": "focus",
    },
    "dependency": {
        "description": "The response lists dependencies and the items they rely on.",
        "scope": "relations",
    },
    "cochange": {
        "description": "The response shows how each subject directly cochanges with the others.",
        "scope": "relations",
    },
    "interact": {
        "description": "The response explains how the elements interact.",
        "scope": "relations",
    },
    "dependent": {
        "description": "The response explains how the elements depend on one another.",
        "scope": "relations",
    },
    "independent": {
        "description": "The response explains how the elements remain independent.",
        "scope": "relations",
    },
    "parallel": {
        "description": "The response describes problems that could arise if the items are parallelized.",
        "scope": "relations",
    },
    "unknown": {
        "description": "The response imagines critical unknown unknowns and explains how they might impact the outcome.",
    },
    "jim": {
        "description": (
            "The response analyses the subject for connascence (Strength, Degree, Locality), identifies its type, computes Severity = Strength × Degree ÷ Locality, and proposes remedies to reduce harmful connascence."
        ),
    },
    "domain": {
        "description": (
            "The response performs a connascence-driven discovery of business domains by grouping elements where multiple forms of connascence converge, describing obligations and change scenarios, and recommending boundary-strengthening remedies."
        ),
    },
    "tune": {
        "description": "The response evaluates the design through the Concordance Frame, focusing on visibility, scope, and dependency volatility that must stay aligned.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "melody": {
        "description": (
            "The response analyses the system for clusters that share coordination patterns in visibility, scope, and volatility, infers the shared intent or 'tune', and recommends ways to clarify or strengthen domains by reducing coordination cost."
        ),
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "constraints": {
        "description": "The response identifies the system's key constraint, describes behaviours it promotes and discourages, and discusses how to balance it for long-term health.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "effects": {
        "description": "The response describes the second- and third-order effects of the situation or change.",
        "completeness": "full",
        "method": "steps",
        "scope": "dynamics",
    },
    "fix": {
        "description": "The response corrects grammar, spelling, and minor style issues while keeping meaning and tone, returning only the modified text.",
        "completeness": "full",
        "scope": "narrow",
    },
    "todo": {
        "description": "The response formats the material as a todo list.",
        "completeness": "gist",
        "method": "steps",
        "form": "checklist",
        "scope": "actions",
    },
    "bridge": {
        "description": "The response guides the reader from the current state to the desired situation described in the additional source.",
        "completeness": "path",
        "method": "steps",
        "scope": "focus",
    },
    "constraints": {
        "description": "Identify the key constraint in this system, describe behaviours it promotes and discourages, and discuss how to balance it for long-term health.",
        "completeness": "full",
        "method": "rigor",
        "scope": "focus",
    },
    "effects": {
        "description": "Describe the second- and third-order effects of this situation or change.",
        "completeness": "full",
        "method": "steps",
        "scope": "dynamics",
    },
    # Fix-style prompts tend to want solid, local, code-level edits.
    "fix": {
        "description": "Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text.",
        "completeness": "full",
        "scope": "narrow",
    },
    # TODO and planning prompts are usually concise, stepwise, and bullet-oriented.
    "todo": {
        "description": "Format this as a todo list.",
        "completeness": "gist",
        "method": "steps",
        "form": "checklist",
        "scope": "actions",
    },
    "bridge": {
        "description": "Guide me from the current state to the desired situation described in the additional source.",
        "completeness": "path",
        "method": "steps",
        "scope": "focus",
    },
    # Document-shaped and summary-style outputs.
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
