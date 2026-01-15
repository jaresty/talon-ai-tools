from __future__ import annotations

from talon import settings
from .axisMappings import axis_hydrate_tokens, axis_value_to_key_map_for
from .personaConfig import (
    normalize_intent_token,
    persona_docs_map,
    persona_hydrate_tokens,
)

from .metaPromptConfig import META_INTERPRETATION_GUIDANCE, PROMPT_REFERENCE_KEY
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
    intent: str = field(default="")
    tone: str = field(default="")
    audience: str = field(default="")
    # Completeness is a soft contract for how far to take answers.
    completeness: str = field(default="")
    # Scope, method, form, and channel are soft contracts for how wide to
    # reason, how to proceed, and what output container/medium to use.
    scope: str = field(default="")
    method: str = field(default="")
    form: str = field(default="")
    channel: str = field(default="")
    # Directional lenses are kept as a separate axis.
    directional: str = field(default="")

    def get_voice(self) -> str:
        if not self.voice:
            self.voice = self.default_voice()
        return self.voice

    def get_intent(self) -> str:
        if not self.intent:
            self.intent = self.default_intent()
        self.intent = normalize_intent_token(self.intent)
        return self.intent

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

    def get_form(self) -> str:
        if not self.form:
            self.form = self.default_form()
        return self.form

    def get_channel(self) -> str:
        if not self.channel:
            self.channel = self.default_channel()
        return self.channel

    def get_directional(self) -> str:
        # Directional lenses default to empty; callers set this per prompt.
        return self.directional

    @staticmethod
    def default_voice() -> str:
        # Resolve configured default to a known persona token; drop descriptive strings.
        raw = settings.get("user.model_default_voice")
        tokens = GPTSystemPrompt._coerce_tokens(raw)
        token = tokens[0] if tokens else str(raw or "").strip()
        docs = persona_docs_map("voice")
        token_l = token.lower()
        for key in docs.keys():
            if str(key).strip().lower() == token_l:
                return str(key).strip()
        return ""

    @staticmethod
    def default_intent() -> str:
        raw = settings.get("user.model_default_intent")
        tokens = GPTSystemPrompt._coerce_tokens(raw)
        token = tokens[0] if tokens else str(raw or "").strip()
        docs = persona_docs_map("intent")
        token = normalize_intent_token(token)
        token_l = token.lower()
        for key in docs.keys():
            if str(key).strip().lower() == token_l:
                return str(key).strip()
        return ""

    @staticmethod
    def default_tone() -> str:
        raw = settings.get("user.model_default_tone")
        tokens = GPTSystemPrompt._coerce_tokens(raw)
        token = tokens[0] if tokens else str(raw or "").strip()
        docs = persona_docs_map("tone")
        token_l = token.lower()
        for key in docs.keys():
            if str(key).strip().lower() == token_l:
                return str(key).strip()
        return ""

    @staticmethod
    def default_audience() -> str:
        raw = settings.get("user.model_default_audience")
        tokens = GPTSystemPrompt._coerce_tokens(raw)
        token = tokens[0] if tokens else str(raw or "").strip()
        docs = persona_docs_map("audience")
        token_l = token.lower()
        for key in docs.keys():
            if str(key).strip().lower() == token_l:
                return str(key).strip()
        return ""

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
    def default_form() -> str:
        # Default form falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_form")
        )
        axis_map = axis_value_to_key_map_for("form")
        mapped = [axis_map.get(token, token) for token in raw_tokens]
        return " ".join(mapped)

    @staticmethod
    def default_channel() -> str:
        # Default channel falls back to the configured setting (token-based).
        raw_tokens = GPTSystemPrompt._coerce_tokens(
            settings.get("user.model_default_channel")
        )
        axis_map = axis_value_to_key_map_for("channel")
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
            if axis in ("voice", "audience", "tone", "intent"):
                # Persona/intent axes use phrase tokens; do not split on spaces.
                return [normalized]
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

        def hydrate_persona(axis: str, value: str) -> str:
            tokens = _tokens_for_axis(axis, value)
            if not tokens:
                return ""
            hydrated = persona_hydrate_tokens(axis, tokens)
            return " ".join(hydrated) if hydrated else " ".join(tokens)

        def _voice_phrase() -> str:
            raw = " ".join(_tokens_for_axis("voice", self.get_voice()))
            if raw.startswith("as a") or raw.startswith("as an"):
                return raw
            if raw.startswith("as "):
                return "as a " + raw[len("as ") :]
            return raw

        def _tone_phrase() -> str:
            raw = " ".join(_tokens_for_axis("tone", self.get_tone()))
            desc = persona_docs_map("tone").get(raw, "")
            if desc.lower().startswith("important:"):
                desc = desc[len("important:") :].strip().lstrip()
            if desc.lower().startswith("be "):
                body = desc[len("be ") :].strip()
                if "tone" not in body.lower():
                    if "while" in body:
                        leading, trailing = body.split("while", 1)
                        leading = leading.replace(" and ", ", ").strip().rstrip(".")
                        body = f"{leading} tone while {trailing.strip()}"
                    else:
                        body = body.replace(" and ", ", ").strip().rstrip(".") + " tone"
                desc = "Use a " + body
            return desc or raw

        def _audience_phrase() -> str:
            raw = " ".join(_tokens_for_axis("audience", self.get_audience()))
            if raw.startswith("to "):
                raw = raw[len("to ") :]
            if not raw.startswith("the "):
                raw = f"the {raw}".strip()
            return f"The audience for this is {raw}".strip()

        def _intent_phrase() -> str:
            raw = " ".join(_tokens_for_axis("intent", self.get_intent()))
            desc = persona_docs_map("intent").get(raw, "")
            if desc.lower().startswith("important:"):
                desc = desc[len("important:") :].strip().lstrip()
            if desc.lower().startswith("aim to"):
                desc = "The goal is to " + desc[len("aim to") :].strip()
            return desc or raw

        lines = [
            # Reference key explains how to interpret the structured tokens
            PROMPT_REFERENCE_KEY.strip(),
            "",
            # Persona axes (who is speaking and to whom)
            f"Voice: Act {_voice_phrase()}",
            f"Tone: {_tone_phrase()}",
            f"Audience: {_audience_phrase()}",
            f"Intent: {_intent_phrase()}",
            # Constraint axes (how to complete the task)
            f"Completeness: {hydrate('completeness', self.get_completeness())}",
            f"Scope: {hydrate('scope', self.get_scope())}",
            f"Method: {hydrate('method', self.get_method())}",
            f"Form: {hydrate('form', self.get_form())}",
            f"Channel: {hydrate('channel', self.get_channel())}",
        ]

        directional_text = hydrate("directional", self.get_directional())
        if directional_text:
            lines.append(f"Directional: {directional_text}")

        lines.append(
            "Answer fully and accurately, prioritizing clarity by rewriting or simplifying anything the audience may not understand with inline definitions (max 5 top-level list items with up to 5 sub-items; summarize extras), and politely decline if a request would not be meaningful. "
            + META_INTERPRETATION_GUIDANCE
        )

        return lines
