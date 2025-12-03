from dataclasses import dataclass
from typing import Literal, Optional
import os

from .modelSource import CompoundSource, ModelSource, SourceStack, create_model_source
from .modelDestination import (
    ModelDestination,
    Stack,
    create_model_destination,
)
from .modelState import GPTState
from talon import Context, Module, clip, settings
from .staticPromptConfig import STATIC_PROMPT_CONFIG


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


def _axis_recipe_token(axis: str, raw_value: str) -> str:
    """Return the short token to use in last_recipe for a given axis value.

    This keeps the system prompt free to use rich, instruction-style axis
    descriptions while the confirmation GUI and recipe recap stay concise and
    grammar-shaped (for example, `shell · full · bound · steps · plain`). If
    we cannot resolve a mapping, fall back to the raw value.
    """
    if not raw_value:
        return raw_value
    axis_map = {
        "completeness": _COMPLETENESS_VALUE_TO_KEY,
        "scope": _SCOPE_VALUE_TO_KEY,
        "method": _METHOD_VALUE_TO_KEY,
        "style": _STYLE_VALUE_TO_KEY,
        "directional": _DIRECTIONAL_VALUE_TO_KEY,
    }.get(axis, {})
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
mod.list("goalModifier", desc="GPT Goal Modifiers")

# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="[{user.goalModifier}] [{user.staticPrompt}] [{user.completenessModifier}] [{user.scopeModifier}] [{user.methodModifier}] [{user.styleModifier}] {user.directionalModifier} | {user.customPrompt}")
def modelPrompt(m) -> str:
    if hasattr(m, "customPrompt"):
        return str(m.customPrompt)
    static_prompt = getattr(
        m, "staticPrompt", "I'm not telling you what to do. Infer the task."
    )
    config = STATIC_PROMPT_CONFIG.get(static_prompt, {})
    display_prompt = config.get("description", static_prompt)
    goal_modifier = getattr(m, "goalModifier", "")
    directional = getattr(m, "directionalModifier", "")

    # Resolve effective axis values for this request (spoken > profile > default)
    # and push them into GPTState.system_prompt so the system-level contract
    # reflects the same axes we expose in the user-level schema.
    spoken_completeness = getattr(m, "completenessModifier", "")
    profile_completeness = config.get("completeness")
    if spoken_completeness:
        effective_completeness = spoken_completeness
    elif profile_completeness and not GPTState.user_overrode_completeness:
        effective_completeness = profile_completeness
    else:
        effective_completeness = settings.get("user.model_default_completeness")

    spoken_scope = getattr(m, "scopeModifier", "")
    profile_scope = config.get("scope")
    if spoken_scope:
        effective_scope = spoken_scope
    elif profile_scope and not GPTState.user_overrode_scope:
        effective_scope = profile_scope
    else:
        effective_scope = settings.get("user.model_default_scope")

    spoken_method = getattr(m, "methodModifier", "")
    profile_method = config.get("method")
    if spoken_method:
        effective_method = spoken_method
    elif profile_method and not GPTState.user_overrode_method:
        effective_method = profile_method
    else:
        effective_method = settings.get("user.model_default_method")

    spoken_style = getattr(m, "styleModifier", "")
    profile_style = config.get("style")
    if spoken_style:
        effective_style = spoken_style
    elif profile_style and not GPTState.user_overrode_style:
        effective_style = profile_style
    else:
        effective_style = settings.get("user.model_default_style")

    # Apply the effective axes to the shared system prompt for this request.
    GPTState.system_prompt.completeness = effective_completeness or ""
    GPTState.system_prompt.scope = effective_scope or ""
    GPTState.system_prompt.method = effective_method or ""
    GPTState.system_prompt.style = effective_style or ""

    # Store a concise, human-readable recipe for this prompt so the
    # confirmation GUI (and future UIs) can recap what was asked.
    recipe_parts = [static_prompt]
    if effective_completeness:
        recipe_parts.append(_axis_recipe_token("completeness", effective_completeness))
    if effective_scope:
        recipe_parts.append(_axis_recipe_token("scope", effective_scope))
    if effective_method:
        recipe_parts.append(_axis_recipe_token("method", effective_method))
    if effective_style:
        recipe_parts.append(_axis_recipe_token("style", effective_style))
    GPTState.last_recipe = " · ".join(recipe_parts)
    # Track the last directional lens separately so recap/quick help can
    # surface it without changing the core recipe token.
    GPTState.last_directional = _axis_recipe_token("directional", directional or "")

    # Task line: what you want done.
    # Restore the pre-ADR semantics: the visible Task text is the human-facing
    # static prompt description (when present), plus any goal modifier. This
    # keeps the prompt text aligned with what users historically saw in the
    # staticPrompt list, even though we now store descriptions centrally.
    task_text = f"{display_prompt}{goal_modifier}"
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
    "model_system_prompt",
    type=str,
    default="Output just the response to the request and no additional content. Do not generate any markdown formatting such as backticks for programming languages unless it is explicitly requested. If the user requests code generation, output just code and not additional natural language explanation.",
    desc="The default system prompt that informs the way the model should behave at a high level",
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
    desc="The default shell for outputting model shell commands",
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
