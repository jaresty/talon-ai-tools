from talon import settings
from dataclasses import dataclass, field
from typing import Literal, TypedDict


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
    content: list[GPTTextItem | GPTImageItem] | list[GPTTextItem]


class GPTRequest(TypedDict):
    messages: list[GPTMessage | GPTTool]
    max_completion_tokens: int
    tools: list[any]
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

    def format_as_array(self) -> list[str]:
        # Formats the instance variables as an array of strings
        return [
            f"Voice: {self.get_voice()}",
            f"Tone: {self.get_tone()}",
            f"Audience: {self.get_audience()}",
            f"Purpose: {self.get_purpose()}",
            "For each of voice, tone, audience, and purpose, if it is not empty, introduce it. Define any terms you use that would not be understood by the audience. Additionally, introduce how you understood the prompt. If you are listing items, break things down into easily scanned chunks with no more children at any level than the human short term memory limit. If you are asked to respond in a way that would not be meaningful, decline the request and explain why."
        ]
