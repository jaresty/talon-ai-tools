from __future__ import annotations

from talon import settings
from dataclasses import dataclass, field
from typing import Any, List, Literal, TypedDict, Union


class GPTTextItem(TypedDict):
    type: Literal["text"]
    text: str


class GPTImageItem(TypedDict):
    type: Literal["image_url"]
    image_url: dict[Literal["url"], str]


class GPTTool(TypedDict):
    tool_call_id: str
    name: str
    type: str
    role: Literal["tool"]
    content: str


class GPTMessage(TypedDict):
    role: Literal["user", "system", "assistant"]
    content: List[Union[GPTTextItem, GPTImageItem]]


class GPTRequest(TypedDict):
    messages: List[Union[GPTMessage, GPTTool]]
    max_completion_tokens: int
    tools: List[Any]
    reasoning_effort: str
    n: int
    model: str
    tool_choice: str
    verbosity: str


@dataclass
class GPTSystemPrompt:
    voice: str = field(default="")
    purpose: str = field(default="")
    tone: str = field(default="")
    audience: str = field(default="")
    # Completeness is a soft contract for how far to take answers.
    completeness: str = field(default="")
    # Scope, method, and style are soft contracts for how wide to reason,
    # how to proceed, and what output form to use.
    scope: str = field(default="")
    method: str = field(default="")
    style: str = field(default="")

    def get_voice(self) -> str:
        if not self.voice:
            self.voice = self.default_voice()
        return self.voice

    def get_purpose(self) -> str:
        if not self.purpose:
            self.purpose = self.default_purpose()
        return self.purpose

    def get_tone(self) -> str:
        if not self.tone:
            self.tone = self.default_tone()
        return self.tone

    def get_audience(self) -> str:
        if not self.audience:
            self.audience = self.default_audience()
        return self.audience

    def get_completeness(self) -> str:
        if not self.completeness:
            self.completeness = self.default_completeness()
        return self.completeness

    def get_scope(self) -> str:
        if not self.scope:
            self.scope = self.default_scope()
        return self.scope

    def get_method(self) -> str:
        if not self.method:
            self.method = self.default_method()
        return self.method

    def get_style(self) -> str:
        if not self.style:
            self.style = self.default_style()
        return self.style

    @staticmethod
    def default_voice() -> str:
        # Code to evaluate and return a default value for voice
        return settings.get("user.model_default_voice")

    @staticmethod
    def default_purpose() -> str:
        # Code to evaluate and return a default value for purpose
        return settings.get("user.model_default_purpose")

    @staticmethod
    def default_tone() -> str:
        # Code to evaluate and return a default value for tone
        return settings.get("user.model_default_tone")

    @staticmethod
    def default_audience() -> str:
        # Code to evaluate and return a default value for audience
        return settings.get("user.model_default_audience")

    @staticmethod
    def default_completeness() -> str:
        # Default completeness level falls back to the configured setting.
        return settings.get("user.model_default_completeness")

    @staticmethod
    def default_scope() -> str:
        # Default scope level falls back to the configured setting.
        return settings.get("user.model_default_scope")

    @staticmethod
    def default_method() -> str:
        # Default method falls back to the configured setting.
        return settings.get("user.model_default_method")

    @staticmethod
    def default_style() -> str:
        # Default style falls back to the configured setting.
        return settings.get("user.model_default_style")

    def format_as_array(self) -> list[str]:
        # Formats the instance variables as an array of strings
        return [
            f"Voice: {self.get_voice()}",
            f"Tone: {self.get_tone()}",
            f"Audience: {self.get_audience()}",
            f"Purpose: {self.get_purpose()}",
            f"Completeness: {self.get_completeness()}",
            f"Scope: {self.get_scope()}",
            f"Method: {self.get_method()}",
            f"Style: {self.get_style()}",
            "Answer fully and accurately, prioritizing clarity by rewriting or simplifying anything the audience may not understand with inline definitions (max 5 top-level list items with up to 5 sub-items; summarize extras), and politely decline if a request would not be meaningful. At the end of your answer, after a separator, state how you understood the request, the intended audience, the voice you used, the tone you used, and the purpose of your response (define any unclear terms). Start this metadata section with a single line: “(For humans only; LLMs should ignore this part.)"
        ]      
