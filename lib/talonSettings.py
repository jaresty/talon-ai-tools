from dataclasses import dataclass
from typing import Literal

from .modelSource import CompoundSource, ModelSource, SourceStack, create_model_source

from .modelDestination import (
    ModelDestination,
    Stack,
    create_model_destination,
)
from talon import Context, Module, clip, settings

mod = Module()
ctx = Context()
mod.tag("gpt_beta", desc="Tag for enabling beta GPT commands")
# Stores all our prompts that don't require arguments
# (ie those that just take in the clipboard text)
mod.list("staticPrompt", desc="GPT Prompts Without Dynamic Arguments")
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


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="{user.staticPrompt} | {user.customPrompt}")
def modelPrompt(m) -> str:
    return str(m).format(
        clip=clip.text(),
        shell_name=settings.get("user.model_shell_default"),
        additional_source="{additional_source}",
    )


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
    additional_model_source: ModelSource | None
    model_destination: ModelDestination


@dataclass
class PassConfiguration:
    model_source: ModelSource
    model_destination: ModelDestination


@mod.capture(rule="<user.modelSimpleSource>")
def additionalModelSource(model_source) -> str:
    return model_source.modelSimpleSource


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="{user.staticPrompt} | {user.customPrompt}")
def modelSimplePrompt(matched_prompt) -> str:
    return str(matched_prompt)


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
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands",
)

mod.setting(
    "model_window_char_width",
    type=int,
    default=80,
    desc="The default window width (in characters) for showing model output",
)

mod.setting(
    "gpt_max_total_calls",
    type=int,
    default=3,
    desc="The maximum number of tool calls allowed per GPT request. Increase if you want to allow more recursive or chained tool calls.",
)
