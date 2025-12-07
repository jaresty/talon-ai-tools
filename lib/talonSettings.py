import os
from dataclasses import dataclass
from typing import Literal, Optional, TypedDict

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


def _read_axis_default_from_list(filename: str, key: str, fallback: str) -> str:
    """Return the list value for a given key from a GPT axis .talon-list file.

    Falls back to the provided fallback if the file or key is not found.
    """
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
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
                k, value = line.split(":", 1)
                if k.strip() == key:
                    return value.strip()
    except FileNotFoundError:
        return fallback
    return fallback


def _read_axis_value_to_key_map(filename: str) -> dict[str, str]:
    """Build a mapping from axis value/description back to its short key.

    We normalise both the key and value so that:
    - Spoken modifiers that expand to long, instruction-style text can be
      mapped back to their concise grammar token (for example, the long
      "Important: Provide a thorough answer..." string -> "full").
    - Code paths that already use the short token (for example, tests or
      static prompt profiles) map idempotently to themselves.
    """
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
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
                short = key.strip()
                desc = value.strip()
                # Map both the key and its description back to the short token.
                mapping[short] = short
                mapping[desc] = short
                # Some axis descriptions are wrapped in quotes in the Talon
                # list files so they can contain colons and other punctuation.
                # Talon normalises these when exposing the list value to
                # Python, so we also record an unquoted variant to ensure
                # lookups (for example, "dynamics" scope) still resolve to the
                # concise token for last_recipe.
                if (desc.startswith('"') and desc.endswith('"')) or (
                    desc.startswith("'") and desc.endswith("'")
                ):
                    unquoted = desc[1:-1].strip()
                    if unquoted:
                        mapping[unquoted] = short
    except FileNotFoundError:
        return {}
    return mapping


DEFAULT_COMPLETENESS_VALUE = _read_axis_default_from_list(
    "completenessModifier.talon-list",
    "full",
    "full",
)

_COMPLETENESS_VALUE_TO_KEY = _read_axis_value_to_key_map(
    "completenessModifier.talon-list"
)
_SCOPE_VALUE_TO_KEY = _read_axis_value_to_key_map("scopeModifier.talon-list")
_METHOD_VALUE_TO_KEY = _read_axis_value_to_key_map("methodModifier.talon-list")
_STYLE_VALUE_TO_KEY = _read_axis_value_to_key_map("styleModifier.talon-list")
_DIRECTIONAL_VALUE_TO_KEY = _read_axis_value_to_key_map(
    "directionalModifier.talon-list"
)

_AXIS_VALUE_TO_KEY_MAPS: dict[str, dict[str, str]] = {
    "completeness": _COMPLETENESS_VALUE_TO_KEY,
    "scope": _SCOPE_VALUE_TO_KEY,
    "method": _METHOD_VALUE_TO_KEY,
    "style": _STYLE_VALUE_TO_KEY,
    "directional": _DIRECTIONAL_VALUE_TO_KEY,
}


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
    return _AXIS_VALUE_TO_KEY_MAPS.get(axis, {})


def _axis_recipe_token(axis: str, raw_value: str) -> str:
    """Return the short token to use in last_recipe for a given axis value.

    This keeps the system prompt free to use rich, instruction-style axis
    descriptions while the confirmation GUI and recipe recap stay concise and
    grammar-shaped (for example, `shell · full · bound · steps · plain`). If
    we cannot resolve a mapping, fall back to the raw value.
    """
    if not raw_value:
        return raw_value
    axis_map = _axis_value_to_key_map_for(axis)
    if not axis_map:
        return raw_value
    return axis_map.get(raw_value, raw_value)


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
    "modelVoice", desc="The voice for the LLM to use. For example, 'as programmer'"
)
mod.list("modelTone", desc="The tone for the LLM to use. For example, 'casually'")
mod.list(
    "modelPurpose",
    desc="The purpose for the LLM to write. For example, 'for information'",
)
mod.list(
    "modelAudience",
    desc="The audience to whom the LLM is writing. For example, 'to business'",
)


def _spoken_axis_value(m, axis_name: str) -> str:
    """Return the spoken modifier(s) for a given axis as a single string.

    For completeness we expect at most one value and return the bare
    `completenessModifier` when present. For scope/method/style we allow
    Talon to provide `axisModifier_list` (multiple values); we map each
    spoken value back to its short axis token and join them with spaces so
    multi-tag semantics are preserved in a concise, token-based form.
    """
    # Completeness remains single-valued.
    if axis_name == "completeness":
        return getattr(m, "completenessModifier", "")

    axis_map = _axis_value_to_key_map_for(axis_name)

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
    directional = getattr(m, "directionalModifier", "")

    profile_axes = get_static_prompt_axes(static_prompt)

    # Resolve effective axis values for this request (spoken > profile > default)
    # and push them into GPTState.system_prompt so the system-level contract
    # reflects the same axes we expose in the user-level schema.
    spoken_completeness = _spoken_axis_value(m, "completeness")
    profile_completeness = profile_axes.get("completeness")
    if spoken_completeness:
        effective_completeness = spoken_completeness
    elif profile_completeness and not GPTState.user_overrode_completeness:
        effective_completeness = profile_completeness
    else:
        effective_completeness = settings.get("user.model_default_completeness")

    spoken_scope = _spoken_axis_value(m, "scope")
    raw_profile_scope = profile_axes.get("scope")
    if isinstance(raw_profile_scope, list):
        profile_scope = " ".join(str(v) for v in raw_profile_scope)
    else:
        profile_scope = raw_profile_scope
    if spoken_scope:
        effective_scope = spoken_scope
    elif profile_scope and not GPTState.user_overrode_scope:
        effective_scope = profile_scope
    else:
        # Normalise any persisted default back to short tokens so that
        # last_recipe and GPTState.last_* remain concise.
        effective_scope = _axis_recipe_token(
            "scope", settings.get("user.model_default_scope")
        )

    spoken_method = _spoken_axis_value(m, "method")
    raw_profile_method = profile_axes.get("method")
    if isinstance(raw_profile_method, list):
        profile_method = " ".join(str(v) for v in raw_profile_method)
    else:
        profile_method = raw_profile_method
    if spoken_method:
        effective_method = spoken_method
    elif profile_method and not GPTState.user_overrode_method:
        effective_method = profile_method
    else:
        effective_method = _axis_recipe_token(
            "method", settings.get("user.model_default_method")
        )

    spoken_style = _spoken_axis_value(m, "style")
    raw_profile_style = profile_axes.get("style")
    if isinstance(raw_profile_style, list):
        profile_style = " ".join(str(v) for v in raw_profile_style)
    else:
        profile_style = raw_profile_style
    if spoken_style:
        effective_style = spoken_style
    elif profile_style and not GPTState.user_overrode_style:
        effective_style = profile_style
    else:
        effective_style = _axis_recipe_token(
            "style", settings.get("user.model_default_style")
        )

    # Apply the effective axes to the shared system prompt for this request.
    GPTState.system_prompt.completeness = effective_completeness or ""
    GPTState.system_prompt.scope = effective_scope or ""
    GPTState.system_prompt.method = effective_method or ""
    GPTState.system_prompt.style = effective_style or ""

    # Store a concise, human-readable recipe for this prompt so the
    # confirmation GUI (and future UIs) can recap what was asked, and keep a
    # structured view of the same tokens for shorthand grammars.
    recipe_parts = [static_prompt]

    # Map effective axis descriptions back to concise axis tokens for
    # last_recipe / GPTState.last_* storage. For this slice, we still have
    # at most one token per axis; later slices will extend this to multiple
    # tokens via the canonicalisation helpers above.
    completeness_token = (
        _axis_recipe_token("completeness", effective_completeness)
        if effective_completeness
        else ""
    )
    scope_token = (
        _axis_recipe_token("scope", effective_scope) if effective_scope else ""
    )
    method_token = (
        _axis_recipe_token("method", effective_method) if effective_method else ""
    )
    style_token = (
        _axis_recipe_token("style", effective_style) if effective_style else ""
    )

    # Prepare canonical, per-axis token sets so that future multi-tag axes
    # can reuse the same helpers without changing storage formats.
    scope_tokens = _canonicalise_axis_tokens(
        "scope", _axis_string_to_tokens(scope_token)
    )
    method_tokens = _canonicalise_axis_tokens(
        "method", _axis_string_to_tokens(method_token)
    )
    style_tokens = _canonicalise_axis_tokens(
        "style", _axis_string_to_tokens(style_token)
    )

    scope_serialised = _axis_tokens_to_string(scope_tokens)
    method_serialised = _axis_tokens_to_string(method_tokens)
    style_serialised = _axis_tokens_to_string(style_tokens)

    if completeness_token:
        recipe_parts.append(completeness_token)
    if scope_serialised:
        recipe_parts.append(scope_serialised)
    if method_serialised:
        recipe_parts.append(method_serialised)
    if style_serialised:
        recipe_parts.append(style_serialised)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = completeness_token
    GPTState.last_scope = scope_serialised
    GPTState.last_method = method_serialised
    GPTState.last_style = style_serialised
    # Track the last directional lens separately (as a short token) so
    # recap/quick help and shorthand grammars can include it.
    GPTState.last_directional = _axis_recipe_token("directional", directional or "")

    # Task line: what you want done.
    # The visible Task text is the human-facing static prompt description
    # (when present); legacy goal modifiers are no longer appended here.
    task_text = display_prompt
    task_line = f"Task:\n  {task_text}"

    # Constraints block: map each spoken/profile axis into typed lines when we
    # have something meaningful to say. We deliberately do not restate plain
    # global defaults here; those already live in the system prompt.
    constraints: list[str] = ["Constraints:"]

    # Completeness: show spoken or profile-level hints.
    if spoken_completeness:
        constraints.append(f"  Completeness: {spoken_completeness}")
    elif profile_completeness and not GPTState.user_overrode_completeness:
        constraints.append(f"  Completeness: {profile_completeness}")

    # Scope: purely conceptual, relative to the voice-selected target.
    if spoken_scope:
        constraints.append(f"  Scope: {spoken_scope}")
    elif profile_scope and not GPTState.user_overrode_scope:
        constraints.append(f"  Scope: {profile_scope}")

    # Method: spoken modifier or short profile keyword.
    if spoken_method:
        constraints.append(f"  Method: {spoken_method}")
    elif profile_method and not GPTState.user_overrode_method:
        constraints.append(f"  Method: {profile_method}")

    # Style: spoken style modifier or short profile keyword.
    if spoken_style:
        constraints.append(f"  Style: {spoken_style}")
    elif profile_style and not GPTState.user_overrode_style:
        constraints.append(f"  Style: {profile_style}")

    # If we only have the "Constraints:" header and nothing else, drop it to
    # avoid cluttering very simple prompts.
    constraints_block = ""
    if len(constraints) > 1:
        constraints_block = "\n" + "\n".join(constraints)

    # Directional lens remains a separate, lens-like instruction appended after
    # the Task / Constraints schema.
    if directional:
        return task_line + constraints_block + "\n\n" + directional
    else:
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
    type=Literal["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini", "gpt-5"],  # type: ignore
    default="gpt-5",
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
    desc="The default voice to use. Who should the LLM be acting as.",
)
mod.setting(
    "model_default_purpose",
    type=str,
    default="Infer a relevant purpose based on the context or the user's request.",
    desc="The default purpose of the communication. This informs how the LLM should respond. For example you could say to inform.",
)
mod.setting(
    "model_default_tone",
    type=str,
    default="Infer a relevant tone based on the context or the user's request.",
    desc="Is the default tone to use. For example speak kindly or formally.",
)
mod.setting(
    "model_default_audience",
    type=str,
    default="Infer a relevant audience based on the context or the user's request.",
    desc="This is the audience that the LLM should format for. For example a programmer or a toddler.m",
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
    "gpt_max_total_calls",
    type=int,
    default=3,
    desc="The maximum number of tool calls allowed per GPT request. Increase if you want to allow more recursive or chained tool calls.",
)
