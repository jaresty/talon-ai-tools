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
        "description": "The response changes the form or presentation of given content while keeping its intended meaning.",
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


# Short CLI-facing labels for task token selection (ADR-0109).
_STATIC_PROMPT_LABELS: dict[str, str] = {
    "check": "Evaluate or verify against criteria",
    "diff": "Compare and contrast subjects",
    "fix": "Reformat existing content",
    "make": "Create new content",
    "pick": "Select from a set of alternatives",
    "plan": "Propose steps, structure, or strategy",
    "probe": "Surface assumptions and implications",
    "pull": "Extract a subset of information",
    "show": "Explain or describe for an audience",
    "sim": "Play out a scenario over time",
    "sort": "Arrange items into categories or order",
}

# Selection guidance for task tokens where the description alone is ambiguous
# or where naming traps exist (ADR-0110, ADR-0128).
_STATIC_PROMPT_GUIDANCE: dict[str, str] = {
    "fix": (
        "In bar's grammar, fix means reformat — not debug. "
        "To analyze/debug: use probe with diagnose, inversion, or adversarial. "
        "To implement the fix: use fix (reformat) or make (create new)."
    ),
    "diff": "Works well with: jira (comparison tables), log (structured diff), "
    "codetour (code comparison). "
    "Distinct from pick: diff = structured comparison for the reader to decide; "
    "pick = LLM makes the selection. When narrowing to a recommendation, pair "
    "diff with converge or branch method.",
    "make": "Works well with: svg, adr, diagram, codetour. "
    "For test plans: use make, not check ('make' = create artifact; 'check' = evaluate existing).",
    "check": "Works well with: log, gherkin, test. "
    "For test coverage gaps: use check, not make ('check' = evaluate existing; 'make' = create new).",
    "plan": "Works well with: adr (architecture decisions), diagram (flowcharts), "
    "jira (backlog items).",
    "sim": "Temporal scenario walkthrough: use when the user wants to trace what "
    "unfolds over time if a condition occurs. Heuristic: 'what would happen "
    "if', 'play out the scenario where', 'simulate what happens when', "
    "'walk me through what would occur if', 'hypothetically if we did X then "
    "what' → sim. Distinct from plan (plan = steps to take; sim = what plays "
    "out if a condition is met), probe (probe = surface implications "
    "analytically; sim = narrate the scenario unfolding over time), and "
    "simulation method (simulation = enriches probe/plan/etc with "
    "thought-experiment reasoning about feedback loops; sim = the scenario "
    "narrative is the primary task). "
    "Works well with: diagram (Mermaid scenarios), slack (session format), "
    "sync (agenda format).",
    "probe": "For extraction tasks ('what are the risks?', 'list the issues'), prefer 'pull' over 'probe'. "
    "probe = analyze broadly; pull = extract subset. "
    "For debugging/troubleshooting: use probe + diagnose method (not fix — fix is content reformatting, not bug-fixing). "
    "Heuristic: 'debug', 'troubleshoot', 'diagnose', 'root cause', 'why is this happening', 'investigate the error' → probe + diagnose.",
    "show": "For summarisation of long documents, prefer 'pull' (extraction). "
    "show = explain a concept; pull = compress source material.",
    "pull": "For summarisation: extract the conceptual core from source material with gist scope. "
    "For risk extraction: works well with fail scope.",
    "pick": "Use when the task asks the LLM to make a selection, not just compare. "
    "Distinct from diff: diff = structured comparison for the reader to decide; "
    "pick = LLM chooses. Heuristic: 'which should I use', 'choose between X/Y/Z', "
    "'recommend one' → pick; 'compare X vs Y' → diff. "
    "Pair with branch method when comparison is needed before selecting.",
}

# Routing trigger phrases for task tokens — surfaced in the "When to use" column
# of the Token Catalog, the "Choosing Task" routing table, the SPA chip panel,
# and the TUI task stage. Parallel to axis use_when; SSOT for task routing hints.
# ADR-0142.
_STATIC_PROMPT_USE_WHEN: dict[str, str] = {
    "show": (
        "Explaining or describing something for an audience. "
        "Heuristic: 'explain', 'describe', 'walk me through', 'what is', 'tell me about', "
        "'how does X work', 'overview of' → show. "
        "Distinct from pull (pull = compress/extract source material; show = explain a concept)."
    ),
    "probe": (
        "Analyzing structure, surfacing assumptions, or diagnosing a problem. "
        "Heuristic: 'analyze', 'what assumptions', 'surface implications', "
        "'debug', 'troubleshoot', 'diagnose', 'root cause', 'why is this happening', "
        "'investigate the error' → probe (pair with diagnose method for debugging). "
        "Distinct from pull (pull = extract a subset; probe = analyze broadly)."
    ),
    "make": (
        "Creating new content or artifacts that did not previously exist. "
        "Heuristic: 'write', 'create', 'draft', 'generate', 'build', 'produce', "
        "'author', 'design' → make. "
        "Distinct from fix (fix = reformat existing content; make = create new)."
    ),
    "fix": (
        "Reformatting or restructuring existing content while keeping its meaning. "
        "Heuristic: 'reformat', 'restructure', 'convert to', 'clean up', "
        "'change format', 'transform into' → fix. "
        "In bar's grammar, fix means reformat — not bug-fix. "
        "For debugging: use probe + diagnose. For creating new: use make."
    ),
    "plan": (
        "Proposing steps, structure, or strategy to reach a goal. "
        "Heuristic: 'plan', 'roadmap', 'steps to', 'how do I get from X to Y', "
        "'migration plan', 'strategy for', 'sequence of actions' → plan. "
        "Distinct from sim (plan = steps to take; sim = what plays out if a condition is met)."
    ),
    "diff": (
        "Comparing or contrasting two or more subjects for the reader to decide. "
        "Heuristic: 'compare', 'contrast', 'X vs Y', 'similarities and differences', "
        "'tradeoffs between', 'how do X and Y differ' → diff. "
        "Distinct from pick (diff = reader decides; pick = LLM selects). "
        "Pair with converge or branch method when narrowing to a recommendation."
    ),
    "check": (
        "Verifying or auditing against criteria. "
        "Heuristic: 'verify', 'audit', 'validate', 'does this satisfy', "
        "'check for', 'evaluate against', 'review for compliance', "
        "'does X meet criteria Y' → check. "
        "Distinct from probe (probe = analyze broadly; check = evaluate against a condition)."
    ),
    "pull": (
        "Extracting a subset of information from source material. "
        "Heuristic: 'extract', 'list the', 'what are the risks', 'pull out', "
        "'summarize this document', 'give me just the', 'identify the' → pull. "
        "Distinct from show (show = explain a concept; pull = compress source material). "
        "For risk extraction: pair with fail scope."
    ),
    "sim": (
        "Playing out a scenario over time — what would happen if. "
        "Heuristic: 'what would happen if', 'play out the scenario where', "
        "'simulate what happens when', 'walk me through what would occur if', "
        "'hypothetically if we did X then what' → sim. "
        "Distinct from plan (plan = steps to take; sim = narrate the scenario unfolding over time), "
        "probe (probe = surface implications analytically; sim = temporal narration), "
        "and simulation method (simulation method = enriches probe/plan/etc with thought-experiment "
        "reasoning about feedback loops; sim = the scenario narrative is the primary task). "
        "They can compose: sim+simulation = scenario played out via explicit feedback-loop modeling."
    ),
    "pick": (
        "Selecting from alternatives — the LLM makes the choice. "
        "Heuristic: 'which should I use', 'choose between X/Y/Z', 'recommend one', "
        "'what would you pick', 'which is better for my situation' → pick. "
        "Distinct from diff (diff = structured comparison for the reader to decide; "
        "pick = LLM selects). Pair with branch method when comparison precedes selection."
    ),
    "sort": (
        "Arranging items into categories or order. "
        "Heuristic: 'group', 'categorize', 'cluster', 'rank', 'order by', "
        "'organize into themes', 'sort by', 'prioritize this list' → sort. "
        "Pair with cluster method for thematic grouping."
    ),
}

# Distilled routing concept phrases for task tokens (ADR-0146).
# Parallel to AXIS_KEY_TO_ROUTING_CONCEPT; SSOT for task routing labels in TUI2/SPA.
_STATIC_PROMPT_ROUTING_CONCEPT: dict[str, str] = {
    "check": "Evaluate pass/fail",
    "diff":  "Compare subjects",
    "fix":   "Reformat/edit",
    "make":  "Create new content",
    "pick":  "Choose from options",
    "plan":  "Propose strategy",
    "probe": "Analyse/surface structure",
    "pull":  "Extract/select subset",
    "show":  "Explain/describe",
    "sim":   "Play out scenario",
    "sort":  "Arrange/categorize",
}

# Kanji icons for task tokens (ADR-0143)
_STATIC_PROMPT_KANJI: dict[str, str] = {
    "check": "検",
    "diff": "較",
    "fix": "修",
    "make": "作",
    "pick": "選",
    "plan": "策",
    "probe": "探",
    "pull": "抜",
    "show": "示",
    "sim": "模",
    "sort": "整",
}


def static_prompt_label_overrides() -> dict[str, str]:
    """Return name->label map for static prompts (ADR-0109)."""
    return dict(_STATIC_PROMPT_LABELS)


def static_prompt_guidance_overrides() -> dict[str, str]:
    """Return name->guidance map for static prompts (ADR-0110)."""
    return dict(_STATIC_PROMPT_GUIDANCE)


def static_prompt_use_when_overrides() -> dict[str, str]:
    """Return name->use_when map for task tokens (ADR-0142)."""
    return dict(_STATIC_PROMPT_USE_WHEN)


def static_prompt_kanji_overrides() -> dict[str, str]:
    """Return name->kanji map for task tokens (ADR-0143)."""
    return dict(_STATIC_PROMPT_KANJI)


def static_prompt_routing_concept_overrides() -> dict[str, str]:
    """Return name->routing_concept map for task tokens (ADR-0146)."""
    return dict(_STATIC_PROMPT_ROUTING_CONCEPT)


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
