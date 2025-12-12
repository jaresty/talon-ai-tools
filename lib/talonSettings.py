import os
from dataclasses import dataclass
from typing import Literal, Optional, Sequence, Tuple, TypedDict

from .axisMappings import (
    AXIS_VALUE_TO_KEY_MAPS,
    DEFAULT_COMPLETENESS_TOKEN,
    axis_key_to_value_map_for,
    axis_hydrate_tokens,
    axis_value_to_key_map_for,
)
from .axisCatalog import axis_catalog
from .modelSource import CompoundSource, ModelSource, SourceStack, create_model_source
from .modelDestination import (
    ModelDestination,
    Stack,
    create_model_destination,
)
from .modelState import GPTState
from .metaPromptConfig import META_INTERPRETATION_GUIDANCE
from talon import Context, Module, settings
from .staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile

# Backward-compatible alias for existing callers.
DEFAULT_COMPLETENESS_VALUE = DEFAULT_COMPLETENESS_TOKEN


def _lists_dir() -> str:
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))


def _read_axis_default_from_list(filename: str, key: str, fallback: str) -> str:
    """Return the configured token for a given key from a GPT axis .talon-list file.

    Falls back to the provided fallback if the file or key is not found.
    """
    axis_for_file = {
        "completenessModifier.talon-list": "completeness",
        "scopeModifier.talon-list": "scope",
        "methodModifier.talon-list": "method",
        "styleModifier.talon-list": "style",
        "directionalModifier.talon-list": "directional",
    }.get(filename)
    if axis_for_file:
        mapping = axis_key_to_value_map_for(axis_for_file)
        return key if key in mapping else fallback
    # Fallback for tests/unknown files: parse directly.
    path = os.path.join(_lists_dir(), filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" not in line:
                    continue
                k, _value = line.split(":", 1)
                if k.strip() == key:
                    return key
    except FileNotFoundError:
        return fallback
    return fallback


def _read_axis_value_to_key_map(filename: str) -> dict[str, str]:
    """Build a mapping from axis value back to its short key (tokens only)."""
    axis_for_file = {
        "completenessModifier.talon-list": "completeness",
        "scopeModifier.talon-list": "scope",
        "methodModifier.talon-list": "method",
        "styleModifier.talon-list": "style",
        "directionalModifier.talon-list": "directional",
    }.get(filename)
    if axis_for_file:
        return axis_value_to_key_map_for(axis_for_file)
    # Fallback for tests/unknown files: parse directly.
    path = os.path.join(_lists_dir(), filename)
    mapping: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                token = key.strip()
                mapping[token] = token
    except FileNotFoundError:
        return {}
    return mapping


_METHOD_VALUE_TO_KEY = AXIS_VALUE_TO_KEY_MAPS.get("method", {})
if "samples" in _METHOD_VALUE_TO_KEY:
    # Tolerate truncated variants of the samples prompt so last_recipe stays concise.
    _METHOD_VALUE_TO_KEY.setdefault("avoid near-duplicate options.", "samples")
    _METHOD_VALUE_TO_KEY.setdefault("avoid near duplicate options.", "samples")
    _METHOD_VALUE_TO_KEY.setdefault(
        "approximately sum to 1; avoid near-duplicate options.", "samples"
    )
    _METHOD_VALUE_TO_KEY.setdefault(
        "approximately sum to 1; avoid near duplicate options.", "samples"
    )
    _METHOD_VALUE_TO_KEY.setdefault(
        "sum to 1; avoid near-duplicate options.", "samples"
    )
    _METHOD_VALUE_TO_KEY.setdefault(
        "sum to 1; avoid near duplicate options.", "samples"
    )
    _METHOD_VALUE_TO_KEY.setdefault("sum to 1", "samples")
    _METHOD_VALUE_TO_KEY.setdefault("approximately sum to 1", "samples")


class AxisValues(TypedDict):
    """Internal representation of axis values for a single request.

    Completeness stays scalar; scope/method/style are sets represented as
    canonicalised lists. This does not change the external system prompt
    schema yet but provides a shared shape for normalisation and tests.
    """

    completeness: Optional[str]
    scope: list[str]
    method: list[str]
    style: list[str]


_AXIS_SOFT_CAPS: dict[str, int] = {
    # Completeness remains scalar and is capped by construction.
    "scope": 2,
    "method": 3,
    "style": 3,
}

# Incompatibilities are expressed as axis -> token -> set of tokens that
# cannot co-exist with that token. This table starts mostly empty; ADR-0026
# populates it incrementally as we identify genuinely incompatible pairs.
_AXIS_INCOMPATIBILITIES: dict[str, dict[str, set[str]]] = {
    "scope": {},
    "method": {},
    "style": {
        # Jira-style issue containers and long-form ADR records are treated
        # as mutually exclusive primary output containers.
        "jira": {"adr"},
        "adr": {"jira"},
        # Synchronous session plans are a distinct container; currently no
        # explicit conflicts with other containers.
        "sync": set(),
    },
}


def _canonicalise_axis_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Normalise a sequence of axis tokens into a canonical set.

    Behaviour:
    - Trims blanks.
    - Applies last-wins semantics with respect to per-axis incompatibilities:
      when a new token arrives, any incompatible existing tokens are dropped.
    - Deduplicates tokens.
    - Applies per-axis soft caps (keeping the most recent tokens when over).
    - Returns tokens sorted by a stable key (currently the short token string)
      so equivalent sets have identical serialised forms.
    """
    raw = [t.strip() for t in tokens if t and t.strip()]
    if not raw:
        return []

    incompat_for_axis = _AXIS_INCOMPATIBILITIES.get(axis, {})
    seen: set[str] = set()
    ordered: list[str] = []

    for token in raw:
        conflicts = incompat_for_axis.get(token, set())
        if conflicts:
            # Drop any conflicting tokens that were accepted earlier.
            ordered = [t for t in ordered if t not in conflicts]
            seen -= conflicts
        if token in seen:
            continue
        ordered.append(token)
        seen.add(token)

    cap = _AXIS_SOFT_CAPS.get(axis)
    if cap is not None and cap > 0 and len(ordered) > cap:
        # Enforce soft cap with last-wins semantics: keep the most recent.
        ordered = ordered[-cap:]

    # Canonicalise order so equivalent sets serialise identically.
    return sorted(ordered)


def _axis_tokens_to_string(tokens: list[str]) -> str:
    """Serialise a canonical list of axis tokens into a string.

    Tokens are joined by a single space; callers are expected to pass in
    already-canonicalised token lists (for example, from
    `_canonicalise_axis_tokens`).
    """
    if not tokens:
        return ""
    return " ".join(tokens)


def _axis_string_to_tokens(value: str) -> list[str]:
    """Parse a serialised axis string back into tokens.

    This is the inverse of `_axis_tokens_to_string` for well-formed inputs:
    it splits on ASCII whitespace and drops empty segments.
    """
    if not value:
        return []
    return [segment for segment in value.split() if segment]


def _axis_value_to_key_map_for(axis: str) -> dict[str, str]:
    """Return the value→key map for a given axis, if available."""
    return axis_value_to_key_map_for(axis)


def _tokens_list(value) -> list[str]:
    """Coerce raw axis input (string or sequence) into a list of tokens."""
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    if not value:
        return []
    return _axis_string_to_tokens(str(value).strip())


def _normalise_directional(raw_value) -> str:
    """Keep directional tokens intact, allowing space-containing lens keys."""
    if isinstance(raw_value, (list, tuple)):
        tokens = [str(v).strip() for v in raw_value if str(v).strip()]
        return " ".join(tokens)
    return str(raw_value).strip() if raw_value else ""


_AXIS_PRIORITY: tuple[str, ...] = ("completeness", "method", "scope", "style")


def _axis_prefix(token: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (axis, stripped_value) if the token uses an explicit prefix."""
    if ":" not in token:
        return None, None
    prefix, remainder = token.split(":", 1)
    axis = prefix.strip().lower()
    if axis in _AXIS_PRIORITY:
        return axis, remainder.strip()
    return None, None


def _resolve_axis_for_token(
    token: str, hint_axis: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Determine which axis a token belongs to, applying hierarchy rules.

    - Prefixed tokens (for example, 'Completeness:full') are assigned to the
      named axis after stripping the prefix.
    - Otherwise, we look for matches across all axis value→key maps and pick
      the highest-priority axis when multiple matches exist.
    - If no matches are found, fall back to the hint axis so user-provided
      tokens are not dropped silently.
    """
    raw = token.strip()
    if not raw:
        return None, None

    pref_axis, pref_value = _axis_prefix(raw)
    if pref_axis:
        axis_map = _axis_value_to_key_map_for(pref_axis)
        mapped = axis_map.get(pref_value, pref_value)
        return pref_axis, mapped

    matches: list[tuple[str, str]] = []
    for axis in _AXIS_PRIORITY:
        axis_map = _axis_value_to_key_map_for(axis)
        mapped = axis_map.get(raw)
        if mapped:
            matches.append((axis, mapped))
    if matches:
        # Highest-priority axis wins when multiple are possible.
        matches.sort(key=lambda pair: _AXIS_PRIORITY.index(pair[0]))
        return matches[0]

    # Preserve the token on its hinted axis when unmapped.
    if hint_axis:
        return hint_axis, raw
    return None, None


def _apply_constraint_hierarchy(
    axis_values: AxisValues,
) -> tuple[AxisValues, AxisValues]:
    """Reassign and normalise axis tokens using the completeness>method>scope>style hierarchy.

    Returns a pair: (resolved_axes_preserving_order, canonical_axes) where:
    - Resolved axes keep ingestion order while applying caps/conflicts.
    - Canonical axes apply the same caps/conflicts but return sorted tokens for recipe serialisation.
    """
    buckets: dict[str, list[str]] = {axis: [] for axis in _AXIS_PRIORITY}

    def _ingest(tokens: list[str], hint: str) -> None:
        for token in tokens:
            target_axis, mapped = _resolve_axis_for_token(token, hint_axis=hint)
            if target_axis and mapped:
                buckets[target_axis].append(mapped)

    completeness_tokens = (
        [axis_values["completeness"]] if axis_values.get("completeness") else []
    )
    _ingest(completeness_tokens, "completeness")
    _ingest(axis_values.get("method", []), "method")
    _ingest(axis_values.get("scope", []), "scope")
    _ingest(axis_values.get("style", []), "style")

    def _preserve_order(axis: str, tokens: list[str]) -> list[str]:
        """Apply conflicts while keeping ingestion order (no caps)."""
        raw = [t.strip() for t in tokens if t and t.strip()]
        if not raw:
            return []
        incompat_for_axis = _AXIS_INCOMPATIBILITIES.get(axis, {})
        seen: set[str] = set()
        ordered: list[str] = []
        for token in raw:
            conflicts = incompat_for_axis.get(token, set())
            if conflicts:
                ordered = [t for t in ordered if t not in conflicts]
                seen -= conflicts
            if token in seen:
                continue
            ordered.append(token)
            seen.add(token)
        return ordered

    resolved_scope = _preserve_order("scope", buckets["scope"])
    resolved_method = _preserve_order("method", buckets["method"])
    resolved_style = _preserve_order("style", buckets["style"])

    canonical_scope = _canonicalise_axis_tokens("scope", buckets["scope"])
    canonical_method = _canonicalise_axis_tokens("method", buckets["method"])
    canonical_style = _canonicalise_axis_tokens("style", buckets["style"])

    completeness_value = (
        buckets["completeness"][-1] if buckets["completeness"] else None
    )

    resolved: AxisValues = {
        "completeness": completeness_value,
        "scope": resolved_scope,
        "method": resolved_method,
        "style": resolved_style,
    }
    canonical: AxisValues = {
        "completeness": completeness_value,
        "scope": canonical_scope,
        "method": canonical_method,
        "style": canonical_style,
    }
    return resolved, canonical


def _filter_axis_tokens(
    axis_values: AxisValues, allow_unknown: bool = False
) -> AxisValues:
    """Filter axis tokens against axisConfig to keep token-only state.

    For live prompt runs we allow unknown short tokens (for example, custom
    sentinel values used in tests) but drop obviously hydrated values such
    as long instruction strings that start with 'Important:'.
    """

    catalog = axis_catalog()
    catalog_tokens = {
        axis: set((tokens or {}).keys())
        for axis, tokens in (catalog.get("axes") or {}).items()
    }

    def _filter(axis: str, tokens: list[str]) -> list[str]:
        valid = axis_value_to_key_map_for(axis)
        valid_tokens = set(valid.keys())
        valid_tokens |= catalog_tokens.get(axis, set())
        filtered: list[str] = []
        for t in tokens:
            if t in valid:
                filtered.append(t)
                continue
            if str(t).strip().lower().startswith("important:"):
                continue
            if t in valid_tokens:
                filtered.append(t)
                continue
            # Keep short/unknown tokens (for example, test sentinels) so spoken
            # modifiers still flow through even when they are not in axisConfig.
            if allow_unknown:
                filtered.append(t)
        return filtered

    filtered: AxisValues = {
        "completeness": axis_values.get("completeness"),
        "scope": _filter("scope", axis_values.get("scope", [])),
        "method": _filter("method", axis_values.get("method", [])),
        "style": _filter("style", axis_values.get("style", [])),
        "directional": _filter("directional", axis_values.get("directional", [])),  # type: ignore[dict-item]
    }
    comp = filtered["completeness"]
    if comp and str(comp).strip().lower().startswith("important:"):
        filtered["completeness"] = None
    return filtered


def _axis_recipe_token(axis: str, raw_value: str) -> str:
    """Return the short token to use in last_recipe for a given axis value.

    This keeps the system prompt free to use rich, instruction-style axis
    descriptions while the confirmation GUI and recipe recap stay concise and
    grammar-shaped (for example, `shell · full · bound · steps · plain`). If
    we cannot resolve a mapping, fall back to the raw value.
    """
    if not raw_value:
        return raw_value
    normalized = str(raw_value).strip()
    if not normalized:
        return ""
    # In token-only mode, just return the token string.
    return normalized


def _map_axis_tokens(axis: str, raw_tokens: Sequence[str]) -> list[str]:
    """Map raw axis tokens to their short tokens, preserving order."""
    if not raw_tokens:
        return []
    tokens: list[str] = []
    for token in raw_tokens:
        normalized = str(token).strip()
        if normalized:
            tokens.append(normalized)
    return tokens


mod = Module()
ctx = Context()
mod.tag("gpt_beta", desc="Tag for enabling beta GPT commands")
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
mod.list("directionalModifier", desc="GPT Directional Modifiers")
mod.list("completenessModifier", desc="GPT Completeness Modifiers")
mod.list("scopeModifier", desc="GPT Scope Modifiers")
mod.list("methodModifier", desc="GPT Method Modifiers")
mod.list("styleModifier", desc="GPT Style Modifiers")
mod.list("customPrompt", desc="Custom user-defined GPT prompts")
mod.list("modelPrompt", desc="GPT Prompts")
mod.list("model", desc="The name of the model")
mod.list("modelDestination", desc="What to do after returning the model response")
mod.list("modelSource", desc="Where to get the text from for the GPT")
mod.list(
    "modelVoice", desc="Persona voice: who is speaking. For example, 'as programmer'."
)
mod.list(
    "modelTone",
    desc="Persona tone: emotional register (for example, 'kindly', 'formally').",
)
mod.list(
    "modelPurpose",
    desc="Intent: why you're talking. For example, 'for teaching'.",
)
mod.list(
    "modelAudience",
    desc="Persona audience: who this is for. For example, 'to programmer'.",
)


def _spoken_axis_value(m, axis_name: str) -> str:
    """Return the spoken modifier(s) for a given axis as a single string.

    For completeness we expect at most one value and return the
    normalised `completenessModifier` when present. For scope/method/style we allow
    Talon to provide `axisModifier_list` (multiple values); we map each
    spoken value back to its short axis token and join them with spaces so
    multi-tag semantics are preserved in a concise, token-based form.
    """
    axis_map = _axis_value_to_key_map_for(axis_name)

    # Completeness remains single-valued.
    if axis_name == "completeness":
        value = getattr(m, "completenessModifier", "")
        if not value:
            return ""
        return axis_map.get(value, value) if axis_map else value

    def _normalise(raw: object) -> str:
        value = str(raw).strip()
        if not value:
            return ""
        if not axis_map:
            return value
        # Map both short tokens and full "Important: …" descriptions back
        # to the concise axis token when possible.
        return axis_map.get(value, value)

    list_attr = f"{axis_name}Modifier_list"
    single_attr = f"{axis_name}Modifier"
    if hasattr(m, list_attr):
        values = getattr(m, list_attr) or []
        parts = [_normalise(v) for v in values if _normalise(v)]
        if parts:
            return " ".join(parts)
    single = getattr(m, single_attr, "")
    return _normalise(single)


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(
    rule="[{user.staticPrompt}] "
    "[{user.completenessModifier}] "
    "[{user.scopeModifier}+] "
    "[{user.methodModifier}+] "
    "[{user.styleModifier}+] "
    "{user.directionalModifier} "
    "| {user.customPrompt}"
)
def modelPrompt(m) -> str:
    if hasattr(m, "customPrompt"):
        return str(m.customPrompt)
    # When no explicit staticPrompt is spoken, fall back to the canonical
    # "infer" key so that recipes remain concise and grammar-shaped while the
    # Task line still uses the historic human-facing description.
    static_prompt = getattr(m, "staticPrompt", "infer")
    profile = get_static_prompt_profile(static_prompt)
    if profile is not None:
        display_prompt = profile["description"]
    else:
        # Preserve the previous human-facing fallback text when we have no
        # profile metadata (for example, custom prompts defined outside this
        # repo).
        display_prompt = (
            "I'm not telling you what to do. Infer the task."
            if static_prompt == "infer"
            else static_prompt
        )
    directional = _normalise_directional(getattr(m, "directionalModifier", ""))

    profile_axes = get_static_prompt_axes(static_prompt)

    # Resolve effective axis values for this request (spoken > profile > default)
    # and push them into GPTState.system_prompt so the system-level contract
    # reflects the same axes we expose in the user-level schema.
    spoken_completeness = _spoken_axis_value(m, "completeness")
    profile_completeness = profile_axes.get("completeness")
    if spoken_completeness:
        effective_completeness_raw = spoken_completeness
    elif profile_completeness and not GPTState.user_overrode_completeness:
        effective_completeness_raw = profile_completeness
    else:
        effective_completeness_raw = settings.get("user.model_default_completeness")

    spoken_scope = _spoken_axis_value(m, "scope")
    raw_profile_scope = profile_axes.get("scope")
    if isinstance(raw_profile_scope, list):
        profile_scope = " ".join(str(v) for v in raw_profile_scope)
    else:
        profile_scope = raw_profile_scope
    if spoken_scope:
        effective_scope_raw = spoken_scope
    elif profile_scope and not GPTState.user_overrode_scope:
        effective_scope_raw = profile_scope
    else:
        effective_scope_raw = settings.get("user.model_default_scope")

    spoken_method = _spoken_axis_value(m, "method")
    raw_profile_method = profile_axes.get("method")
    if isinstance(raw_profile_method, list):
        profile_method = " ".join(str(v) for v in raw_profile_method)
    else:
        profile_method = raw_profile_method
    if spoken_method:
        effective_method_raw = spoken_method
    elif profile_method and not GPTState.user_overrode_method:
        effective_method_raw = profile_method
    else:
        effective_method_raw = settings.get("user.model_default_method")

    spoken_style = _spoken_axis_value(m, "style")
    raw_profile_style = profile_axes.get("style")
    if isinstance(raw_profile_style, list):
        profile_style = " ".join(str(v) for v in raw_profile_style)
    else:
        profile_style = raw_profile_style
    if spoken_style:
        effective_style_raw = spoken_style
    elif profile_style and not GPTState.user_overrode_style:
        effective_style_raw = profile_style
    else:
        effective_style_raw = settings.get("user.model_default_style")

    # Map all axes to token-based storage, keeping a canonical form for recap/rerun.
    raw_completeness_tokens = _map_axis_tokens(
        "completeness", _tokens_list(effective_completeness_raw)
    )
    raw_scope_tokens = _map_axis_tokens("scope", _tokens_list(effective_scope_raw))
    raw_method_tokens = _map_axis_tokens("method", _tokens_list(effective_method_raw))
    raw_style_tokens = _map_axis_tokens("style", _tokens_list(effective_style_raw))

    resolved_axes, canonical_axes = _apply_constraint_hierarchy(
        {
            "completeness": raw_completeness_tokens[0]
            if raw_completeness_tokens
            else None,
            "scope": raw_scope_tokens,
            "method": raw_method_tokens,
            "style": raw_style_tokens,
        }
    )
    # Filter out any tokens not present in axisConfig to keep token-only state.
    resolved_axes = _filter_axis_tokens(resolved_axes, allow_unknown=True)
    canonical_axes = _filter_axis_tokens(canonical_axes, allow_unknown=True)

    completeness_token = resolved_axes.get("completeness") or ""
    completeness_tokens = [completeness_token] if completeness_token else []

    scope_tokens = resolved_axes.get("scope", [])
    scope_canonical_serialised = _axis_tokens_to_string(canonical_axes.get("scope", []))

    method_tokens = resolved_axes.get("method", [])
    method_canonical_serialised = _axis_tokens_to_string(
        canonical_axes.get("method", [])
    )

    style_tokens = resolved_axes.get("style", [])
    style_canonical_serialised = _axis_tokens_to_string(canonical_axes.get("style", []))

    scope_serialised = _axis_tokens_to_string(scope_tokens)
    method_serialised = _axis_tokens_to_string(method_tokens)
    style_serialised = _axis_tokens_to_string(style_tokens)

    # Apply the effective axes to the shared system prompt for this request.
    GPTState.system_prompt.completeness = completeness_token or ""
    GPTState.system_prompt.scope = scope_serialised or ""
    GPTState.system_prompt.method = method_serialised or ""
    GPTState.system_prompt.style = style_serialised or ""
    GPTState.system_prompt.directional = directional or ""

    # Store a concise, human-readable recipe for this prompt so the
    # confirmation GUI (and future UIs) can recap what was asked, and keep a
    # structured view of the same tokens for shorthand grammars.
    recipe_parts = [static_prompt]

    if completeness_token:
        recipe_parts.append(completeness_token)
    if scope_canonical_serialised:
        recipe_parts.append(scope_canonical_serialised)
    if method_canonical_serialised:
        recipe_parts.append(method_canonical_serialised)
    if style_canonical_serialised:
        recipe_parts.append(style_canonical_serialised)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = completeness_token
    GPTState.last_scope = scope_canonical_serialised
    GPTState.last_method = method_canonical_serialised
    GPTState.last_style = style_canonical_serialised
    GPTState.last_axes = {
        "completeness": [completeness_token] if completeness_token else [],
        "scope": canonical_axes.get("scope", []),
        "method": canonical_axes.get("method", []),
        "style": canonical_axes.get("style", []),
    }
    # Track the last directional lens separately (as a short token) so
    # recap/quick help and shorthand grammars can include it.
    GPTState.last_directional = _axis_recipe_token("directional", directional or "")

    completeness_from_cross_axis = bool(
        completeness_token and not raw_completeness_tokens
    )
    scope_from_cross_axis = bool(scope_tokens and not raw_scope_tokens)
    method_from_cross_axis = bool(method_tokens and not raw_method_tokens)
    style_from_cross_axis = bool(style_tokens and not raw_style_tokens)

    # Task line: what you want done.
    # The visible Task text is the human-facing static prompt description
    # (when present); legacy goal modifiers are no longer appended here.
    task_text = display_prompt
    task_line = f"Task:\n  {task_text}"

    # Constraints block: map each spoken/profile axis into typed lines when we
    # have something meaningful to say. We deliberately do not restate plain
    # global defaults here; those already live in the system prompt.
    constraints: list[str] = ["Constraints:"]

    def _hydrate(axis: str, tokens: list[str]) -> str:
        hydrated = axis_hydrate_tokens(axis, tokens)
        return " ".join(hydrated) if hydrated else " ".join(tokens)

    # Completeness: show spoken or profile-level hints (hydrate for readability).
    if completeness_tokens and (spoken_completeness or completeness_from_cross_axis):
        constraints.append(
            f"  Completeness: {_hydrate('completeness', completeness_tokens)}"
        )
    elif profile_completeness and not GPTState.user_overrode_completeness:
        prof_tokens = _map_axis_tokens(
            "completeness", _tokens_list(profile_completeness)
        )
        constraints.append(f"  Completeness: {_hydrate('completeness', prof_tokens)}")

    # Scope: purely conceptual, relative to the voice-selected target.
    if scope_tokens and (spoken_scope or scope_from_cross_axis):
        constraints.append(f"  Scope: {_hydrate('scope', scope_tokens)}")
    elif profile_scope and not GPTState.user_overrode_scope:
        prof_tokens = _map_axis_tokens("scope", _tokens_list(profile_scope))
        constraints.append(f"  Scope: {_hydrate('scope', prof_tokens)}")

    # Method: spoken modifier or short profile keyword.
    if method_tokens and (spoken_method or method_from_cross_axis):
        constraints.append(f"  Method: {_hydrate('method', method_tokens)}")
    elif profile_method and not GPTState.user_overrode_method:
        prof_tokens = _map_axis_tokens("method", _tokens_list(profile_method))
        constraints.append(f"  Method: {_hydrate('method', prof_tokens)}")

    # Style: spoken style modifier or short profile keyword.
    if style_tokens and (spoken_style or style_from_cross_axis):
        constraints.append(f"  Style: {_hydrate('style', style_tokens)}")
    elif profile_style and not GPTState.user_overrode_style:
        prof_tokens = _map_axis_tokens("style", _tokens_list(profile_style))
        constraints.append(f"  Style: {_hydrate('style', prof_tokens)}")

    # If we only have the "Constraints:" header and nothing else, drop it to
    # avoid cluttering very simple prompts.
    constraints_block = ""
    if len(constraints) > 1:
        constraints_block = "\n" + "\n".join(constraints)

    # Directional lens is sent via the system prompt; avoid appending raw
    # tokens to the user-facing prompt text.
    return task_line + constraints_block


@mod.capture(rule="[<user.modelPrompt>] prompt <user.text>")
def pleasePrompt(m) -> str:
    additional_prompt = ""
    # Check if m has the property modelPrompt

    if hasattr(m, "modelPrompt"):
        additional_prompt = m.modelPrompt
    return additional_prompt + "\n" + str(m.text)


@mod.capture(rule="{user.modelDestination} | <user.modelDestinationStack>")
def modelDestination(m) -> ModelDestination:
    if hasattr(m, "modelDestinationStack"):
        return m.modelDestinationStack

    return create_model_destination(m.modelDestination)


@mod.capture(rule="<user.modelSimpleSource> [and <user.modelSimpleSource>]+")
def modelCompoundSource(m) -> ModelSource:
    if len(m.modelSimpleSource_list) == 1:
        return m.modelSimpleSource_list[0]
    return CompoundSource(m.modelSimpleSource_list)


@mod.capture(rule="{user.modelSource} | <user.modelSourceStack>")
def modelSimpleSource(m) -> ModelSource:
    if hasattr(m, "modelSourceStack"):
        return m.modelSourceStack

    return create_model_source(m.modelSource)


@mod.capture(rule="to stack <user.letter>")
def modelDestinationStack(m) -> ModelDestination:
    return Stack(m.letter)


@mod.capture(rule="stack <user.letter>")
def modelSourceStack(match_rule) -> ModelSource:
    return SourceStack(match_rule.letter)


@dataclass
class ApplyPromptConfiguration:
    please_prompt: str
    model_source: ModelSource
    additional_model_source: Optional[ModelSource]
    model_destination: ModelDestination


@dataclass
class PassConfiguration:
    model_source: ModelSource
    model_destination: ModelDestination


@mod.capture(rule="<user.modelSimpleSource>")
def additionalModelSource(model_source) -> str:
    return model_source.modelSimpleSource


@mod.capture(
    rule="^[<user.modelCompoundSource>] [using <user.additionalModelSource>] [<user.modelDestination>] <user.pleasePrompt>$"
)
def pleasePromptConfiguration(matched_prompt) -> ApplyPromptConfiguration:
    return ApplyPromptConfiguration(
        getattr(matched_prompt, "pleasePrompt", ""),
        getattr(
            matched_prompt,
            "modelCompoundSource",
            create_model_source(settings.get("user.model_default_source")),
        ),
        getattr(
            matched_prompt,
            "additionalModelSource",
            None,
        ),
        getattr(
            matched_prompt,
            "modelDestination",
            create_model_destination(settings.get("user.model_default_destination")),
        ),
    )


@mod.capture(
    rule="[<user.modelCompoundSource>] [using <user.additionalModelSource>] [<user.modelDestination>] <user.modelPrompt>"
)
def applyPromptConfiguration(matched_prompt) -> ApplyPromptConfiguration:
    return ApplyPromptConfiguration(
        getattr(matched_prompt, "modelPrompt", ""),
        getattr(
            matched_prompt,
            "modelCompoundSource",
            create_model_source(settings.get("user.model_default_source")),
        ),
        getattr(matched_prompt, "additionalModelSource", None),
        getattr(
            matched_prompt,
            "modelDestination",
            create_model_destination(settings.get("user.model_default_destination")),
        ),
    )


@mod.capture(
    rule="(<user.modelSimpleSource> | <user.modelDestination> | <user.modelSimpleSource> <user.modelDestination>)$"
)
def passConfiguration(matched_prompt) -> PassConfiguration:
    return PassConfiguration(
        getattr(
            matched_prompt,
            "modelSimpleSource",
            create_model_source(settings.get("user.model_default_source")),
        ),
        getattr(
            matched_prompt,
            "modelDestination",
            create_model_destination(settings.get("user.model_default_destination")),
        ),
    )


mod.setting(
    "openai_model",
    type=Literal[
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4.1",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-5",
    ],  # type: ignore
    default="gpt-5",
)

mod.setting(
    "model_provider_current",
    type=str,
    default="openai",
    desc="Current active model provider id (for example, 'openai' or 'gemini').",
)

mod.setting(
    "model_provider_default",
    type=str,
    default="openai",
    desc="Default provider id to use when none is set.",
)

mod.setting(
    "model_provider_token_openai",
    type=str,
    default="",
    desc="Optional token for the built-in openai provider when env vars are unavailable.",
)

mod.setting(
    "model_provider_token_gemini",
    type=str,
    default="",
    desc="Optional token for the built-in gemini provider when env vars are unavailable.",
)

mod.setting(
    "model_provider_model_gemini",
    type=str,
    default="",
    desc="Optional default model for the built-in gemini provider.",
)

mod.setting(
    "model_provider_model_aliases_gemini",
    type=str,
    default="",
    desc="Optional comma-separated model aliases for gemini (format: 'spoken:modelid', e.g. 'one five pro:gemini-1.5-pro').",
)

mod.setting(
    "model_provider_model_aliases_openai",
    type=str,
    default="",
    desc="Optional comma-separated model aliases for openai (format: 'spoken:modelid', e.g. 'four o:gpt-4o').",
)

mod.setting(
    "model_provider_extra",
    type=dict,
    default={},
    desc="Optional extra provider definitions; accepts a dict or list of provider config objects.",
)

mod.setting(
    "model_provider_probe",
    type=int,
    default=0,
    desc="When set to 1, provider list/status will attempt a quick reachability probe of the provider endpoint.",
)

mod.setting(
    "model_default_destination",
    type=str,
    default="paste",
    desc="The default insertion destination. This can be overridden contextually to provide application level defaults.",
)

mod.setting(
    "model_endpoint",
    type=str,
    default="https://api.openai.com/v1/chat/completions",
    desc="The endpoint to send the model requests to",
)

mod.setting(
    "model_request_timeout_seconds",
    type=int,
    default=120,
    desc="Maximum time in seconds to wait for a single model HTTP request before timing out.",
)

mod.setting(
    "model_system_prompt",
    type=str,
    default=(
        "Output just the main answer to the user's request as the primary response. "
        "Do not generate markdown formatting such as backticks for programming languages unless it is explicitly requested or implied by a style/method axis (for example, 'code', 'table', 'presenterm'). "
        "If the user requests code generation, output just code in the main answer and not additional natural-language explanation. "
    )
    + META_INTERPRETATION_GUIDANCE,
    desc="The default system prompt that informs the way the model should behave at a high level, including instructions for an optional structured meta-interpretation section.",
)

mod.setting(
    "model_default_voice",
    type=str,
    default="Infer a relevant voice based on the context or the user's request.",
    desc="Default voice (who is speaking). For example, 'as programmer'.",
)
mod.setting(
    "model_default_purpose",
    type=str,
    default="Infer a relevant purpose based on the context or the user's request.",
    desc="Default intent (why you're talking). For example, 'for teaching'.",
)
mod.setting(
    "model_default_tone",
    type=str,
    default="Infer a relevant tone based on the context or the user's request.",
    desc="Default tone (emotional register). For example, 'kindly' or 'formally'.",
)
mod.setting(
    "model_default_audience",
    type=str,
    default="Infer a relevant audience based on the context or the user's request.",
    desc="Default audience (who this is for). For example, 'to programmer' or 'to junior engineer'.",
)

mod.setting(
    "model_default_completeness",
    type=str,
    default=DEFAULT_COMPLETENESS_VALUE,
    desc=(
        "Default completeness level when no spoken completeness modifier is provided. "
        "Suggested values align with the completenessModifier list (for example, 'skim', 'gist', 'full', 'max')."
    ),
)

mod.setting(
    "model_default_scope",
    type=str,
    default="",
    desc=(
        "Default conceptual scope when no spoken scope modifier is provided. "
        "Suggested values align with the scopeModifier list (for example, 'narrow', 'focus', 'bound'). "
        "Leave empty to avoid adding an implicit scope bias."
    ),
)

mod.setting(
    "model_default_method",
    type=str,
    default="",
    desc=(
        "Default method or process when no spoken method modifier is provided. "
        "Suggested values align with the methodModifier list (for example, 'steps', 'plan', 'rigor')."
    ),
)

mod.setting(
    "model_default_style",
    type=str,
    default="",
    desc=(
        "Default output style when no spoken style modifier is provided. "
        "Suggested values align with the styleModifier list (for example, 'plain', 'tight', 'bullets', 'table', 'code')."
    ),
)


mod.setting(
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands (for example, when using the shellscript style).",
)

mod.setting(
    "model_window_char_width",
    type=int,
    default=200,
    desc="The default window width (in characters) for showing model output",
)

mod.setting(
    "model_source_save_directory",
    type=str,
    default="",
    desc=(
        "Optional directory where 'model source save file' and 'model history save source' "
        "write markdown files. When empty, Talon defaults to a 'talon-ai-model-sources' "
        "folder under the Talon user directory."
    ),
)

mod.setting(
    "gpt_max_total_calls",
    type=int,
    default=3,
    desc="The maximum number of tool calls allowed per GPT request. Increase if you want to allow more recursive or chained tool calls.",
)
