from __future__ import annotations

from talon import settings
from .axisMappings import axis_hydrate_tokens, axis_value_to_key_map_for

from .metaPromptConfig import META_INTERPRETATION_GUIDANCE
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
    # Directional lenses are kept as a separate axis.
    directional: str = field(default="")

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

    def get_directional(self) -> str:
        # Directional lenses default to empty; callers set this per prompt.
        return self.directional

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
    def _coerce_tokens(raw) -> list[str]:
        """Normalise list/tuple settings without splitting strings."""
        if isinstance(raw, (list, tuple)):
            return [str(v).strip() for v in raw if str(v).strip()]
        if not raw:
            return []
        return [t for t in str(raw).split() if t]

    @staticmethod
    def default_completeness() -> str:
        # Default completeness level falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_completeness")
        )
        token = raw_tokens[0] if raw_tokens else ""
        axis_map = axis_value_to_key_map_for("completeness")
        return axis_map.get(token, token)

    @staticmethod
    def default_scope() -> str:
        # Default scope level falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_scope")
        )
        axis_map = axis_value_to_key_map_for("scope")
        mapped = [axis_map.get(token, token) for token in raw_tokens]
        return " ".join(mapped)

    @staticmethod
    def default_method() -> str:
        # Default method falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_method")
        )
        axis_map = axis_value_to_key_map_for("method")
        mapped = [axis_map.get(token, token) for token in raw_tokens]
        return " ".join(mapped)

    @staticmethod
    def default_style() -> str:
        # Default style falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_style")
        )
        axis_map = axis_value_to_key_map_for("style")
        mapped = [axis_map.get(token, token) for token in raw_tokens]
        return " ".join(mapped)

    def format_as_array(self) -> list[str]:
        # Formats the instance variables as an array of strings
        def _tokens_for_axis(axis: str, value) -> list[str]:
            if isinstance(value, (list, tuple)):
                return [str(t).strip() for t in value if str(t).strip()]
            normalized = str(value or "").strip()
            if not normalized:
                return []
            if axis == "directional":
                # Directional tokens can contain spaces; keep them intact.
                return [normalized]
            return [t for t in normalized.split() if t]

        def hydrate(axis: str, value) -> str:
            tokens = _tokens_for_axis(axis, value)
            if not tokens:
                return ""
            hydrated = axis_hydrate_tokens(axis, tokens)
            if not hydrated:
                return " ".join(tokens)
            if axis == "completeness":
                return hydrated[0]
            return " ".join(hydrated)

        lines = [
            f"Voice: {self.get_voice()}",
            f"Tone: {self.get_tone()}",
            f"Audience: {self.get_audience()}",
            f"Purpose: {self.get_purpose()}",
            f"Completeness: {hydrate('completeness', self.get_completeness())}",
            f"Scope: {hydrate('scope', self.get_scope())}",
            f"Method: {hydrate('method', self.get_method())}",
            f"Style: {hydrate('style', self.get_style())}",
        ]

        directional_text = hydrate("directional", self.get_directional())
        if directional_text:
            lines.append(f"Directional: {directional_text}")

        lines.append(
            "Answer fully and accurately, prioritizing clarity by rewriting or simplifying anything the audience may not understand with inline definitions (max 5 top-level list items with up to 5 sub-items; summarize extras), and politely decline if a request would not be meaningful. "
            + META_INTERPRETATION_GUIDANCE
        )

        return lines
