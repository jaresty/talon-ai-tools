from dataclasses import dataclass
from typing import Literal

from .modelSource import ModelSource, SourceRegister, create_model_source

from .modelDestination import (
    ModelDestination,
    Register,
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
def modelPrompt(matched_prompt) -> str:
    return str(matched_prompt).format(
        clip=clip.text(),
        shell_name=settings.get("user.model_shell_default"),
        additional_source="{additional_source}",
    )


@mod.capture(rule="[<user.modelPrompt>] please <user.text>")
def pleasePrompt(matched_prompt) -> str:
    additional_prompt = ""
    # Check if matched_prompt has the property modelPrompt

    if hasattr(matched_prompt, "modelPrompt"):
        additional_prompt = matched_prompt.modelPrompt
    return additional_prompt + "\n" + str(matched_prompt.text)


@mod.capture(rule="{user.modelDestination} | <user.modelDestinationRegister>")
def modelDestination(model_destination) -> ModelDestination:
    if hasattr(model_destination, "modelDestinationRegister"):
        return model_destination.modelDestinationRegister

    return create_model_destination(model_destination.modelDestination)


@mod.capture(rule="{user.modelSource} | <user.modelSourceRegister>")
def modelSource(model_source) -> ModelSource:
    if hasattr(model_source, "modelSourceRegister"):
        return model_source.modelSourceRegister

    return create_model_source(model_source.modelSource)


@mod.capture(rule="to register <user.letter>")
def modelDestinationRegister(match_rule) -> ModelDestination:
    return Register(match_rule.letter)


@mod.capture(rule="register <user.letter>")
def modelSourceRegister(match_rule) -> ModelSource:
    return SourceRegister(match_rule.letter)


@dataclass
class ApplyPromptConfiguration:
    please_prompt: str
    model_source: ModelSource
    additional_model_source: ModelSource
    model_destination: ModelDestination


@dataclass
class PassConfiguration:
    model_source: ModelSource
    model_destination: ModelDestination


@mod.capture(rule="<user.modelSource>")
def additionalModelSource(model_source) -> str:
    return model_source.modelSource


# model prompts can be either static and predefined by this repo or custom outside of it
@mod.capture(rule="{user.staticPrompt} | {user.customPrompt}")
def modelSimplePrompt(matched_prompt) -> str:
    return str(matched_prompt)


@mod.capture(
    rule="^<user.pleasePrompt> [<user.modelSource>] [using <user.additionalModelSource>] [<user.modelDestination>]$"
)
def pleasePromptConfiguration(matched_prompt) -> ApplyPromptConfiguration:
    destination_type: str = ""
    source_type: str = ""
    additional_source_type: str = ""
    if not hasattr(matched_prompt, "modelDestination"):
        destination_type = settings.get("user.model_default_destination")
    if not hasattr(matched_prompt, "modelSource"):
        source_type = settings.get("user.model_default_source")
    if not hasattr(matched_prompt, "additionalModelSource"):
        additional_source_type = settings.get("user.model_default_source")
    return ApplyPromptConfiguration(
        getattr(matched_prompt, "pleasePrompt", ""),
        getattr(matched_prompt, "modelSource", create_model_source(source_type)),
        getattr(
            matched_prompt,
            "additionalModelSource",
            create_model_source(additional_source_type),
        ),
        getattr(
            matched_prompt,
            "modelDestination",
            create_model_destination(destination_type),
        ),
    )


@mod.capture(
    rule="<user.modelPrompt> [<user.modelSource>] [using <user.additionalModelSource>] [<user.modelDestination>]"
)
def applyPromptConfiguration(matched_prompt) -> ApplyPromptConfiguration:
    return ApplyPromptConfiguration(
        getattr(matched_prompt, "modelPrompt", ""),
        create_model_source(
            getattr(
                matched_prompt, "modelSource", settings.get("user.model_default_source")
            ),
        ),
        create_model_source(
            getattr(
                matched_prompt,
                "additionalModelSource",
                settings.get("user.model_default_source"),
            ),
        ),
        create_model_destination(
            getattr(
                matched_prompt,
                "modelDestination",
                settings.get("user.model_default_destination"),
            ),
        ),
    )


@mod.capture(
    rule="(<user.modelSource> | <user.modelDestination> | <user.modelSource> <user.modelDestination>)$"
)
def passConfiguration(matched_prompt) -> PassConfiguration:
    return PassConfiguration(
        create_model_source(
            getattr(
                matched_prompt, "modelSource", settings.get("user.model_default_source")
            )
        ),
        create_model_destination(
            getattr(
                matched_prompt,
                "modelDestination",
                settings.get("user.model_default_destination"),
            )
        ),
    )


mod.setting(
    "openai_model",
    type=Literal["gpt-3.5-turbo", "gpt-4", "gpt-4o-mini"],  # type: ignore
    default="gpt-4o-mini",
)

mod.setting(
    "model_temperature",
    type=float,
    default=0.6,
    desc="The temperature of the model. Higher values make the model more creative.",
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
    default="You are an assistant helping an office worker to be more productive.",
    desc="The default voice to use. Who should the LLM be acting as.",
)
mod.setting(
    "model_default_purpose",
    type=str,
    default="Your purpose is to help accomplish a task.",
    desc="The default purpose of the communication. This informs how the LLM should respond. For example you could say to inform.",
)
mod.setting(
    "model_default_tone",
    type=str,
    default="You are casual and friendly and helpful.",
    desc="Is the default tone to use. For example speak kindly or formally.",
)
mod.setting(
    "model_default_audience",
    type=str,
    default="Your audience is just the person who is making this request.",
    desc="This is the audience that the LLM should format for. For example a programmer or a toddler.m",
)


mod.setting(
    "model_shell_default",
    type=str,
    default="bash",
    desc="The default shell for outputting model shell commands",
)
