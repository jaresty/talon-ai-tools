"""Prompt session orchestration utilities."""

from __future__ import annotations

from typing import List, Optional, Union

from ..lib.modelHelpers import (
    append_request_messages,
    build_request,
    format_message,
    format_messages,
    send_request,
)
from ..lib.modelSource import ModelSource, format_source_messages
from ..lib.modelState import GPTState
from ..lib.modelTypes import GPTMessage, GPTTextItem, GPTTool


class PromptSession:
    """Encapsulate preparation and execution of a single GPT request."""

    def __init__(self, destination: Union[str, object]):
        self._destination = destination
        self._prepared = False

    @property
    def destination(self) -> Union[str, object]:
        return self._destination

    def prepare_prompt(
        self,
        prompt: str,
        source: ModelSource,
        additional_source: Optional[ModelSource] = None,
    ) -> None:
        """Populate the request with system prompts, query backlog, and user input."""
        self.begin()

        current_messages = format_source_messages(prompt, source, additional_source)

        system_prompt_messages: List[GPTTextItem] = [
            format_message(message) for message in GPTState.system_prompt.format_as_array()
        ]
        if system_prompt_messages:
            append_request_messages([format_messages("system", system_prompt_messages)])

        if GPTState.query:
            append_request_messages(GPTState.query)

        current_request = format_messages("user", current_messages)
        if GPTState.thread_enabled:
            GPTState.push_thread(current_request)
        append_request_messages([current_request])

    def add_messages(self, messages: List[Union[GPTMessage, GPTTool]]) -> None:
        """Append additional messages or tool responses to the request."""
        self.begin()
        append_request_messages(messages)

    def append_thread(self, message: GPTTextItem) -> None:
        """Record an assistant response in the active thread when threading is enabled."""
        if not GPTState.thread_enabled:
            return
        thread_message = format_messages("assistant", [message])
        GPTState.push_thread(thread_message)

    def execute(self):
        """Send the request and return the assistant response."""
        self._ensure_prepared()
        return send_request()

    def begin(self, reuse_existing: bool = False) -> None:
        """Ensure the underlying request exists, optionally reusing the current one."""
        if reuse_existing and getattr(GPTState, "request", None):
            self._prepared = True
            return
        self._ensure_prepared()

    def _ensure_prepared(self) -> None:
        if not self._prepared:
            build_request(self._destination)
            self._prepared = True
