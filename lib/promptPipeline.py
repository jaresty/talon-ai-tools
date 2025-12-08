"""High-level orchestration helpers for prompt execution and presentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, cast

from .modelPresentation import ResponsePresentation, render_for_destination
from .modelSource import GPTItem, ModelSource
from .modelTypes import GPTTextItem
from .promptSession import PromptSession
from .requestAsync import start_async


@dataclass
class PromptResult:
    """Structured result of a prompt run, including messages and presentation helpers."""

    messages: List[GPTItem]
    session: Optional[PromptSession] = None

    @classmethod
    def from_response(
        cls, response: GPTItem, session: Optional[PromptSession] = None
    ) -> "PromptResult":
        return cls(messages=[response], session=session)

    @classmethod
    def from_messages(
        cls, messages: Iterable[GPTItem], session: Optional[PromptSession] = None
    ) -> "PromptResult":
        return cls(messages=list(messages), session=session)

    @property
    def text(self) -> str:
        if not self.messages:
            return ""
        first = self.messages[0]
        if first["type"] == "text":
            return cast(str, first["text"])
        return ""

    def presentation_for(self, destination_kind: str) -> ResponsePresentation:
        return render_for_destination(self.messages, destination_kind)

    def append_thread(self) -> None:
        if self.session is None:
            return
        if not self.messages:
            return
        first = self.messages[0]
        if first["type"] == "text":
            self.session.append_thread(cast(GPTTextItem, first))


class PromptPipeline:
    """Facade for running prompts through PromptSession and packaging the results."""

    def __init__(self, session_cls=PromptSession):
        self._session_cls = session_cls

    def run(
        self,
        prompt: str,
        source: ModelSource,
        destination,
        additional_source: Optional[ModelSource] = None,
    ) -> PromptResult:
        session = self._session_cls(destination)
        session.prepare_prompt(prompt, source, additional_source)
        return self.complete(session)

    def run_async(
        self,
        prompt: str,
        source: ModelSource,
        destination,
        additional_source: Optional[ModelSource] = None,
    ):
        """Prepare and execute a prompt in a background thread; returns a handle."""
        return start_async(self.run, prompt, source, destination, additional_source)

    def complete(self, session: PromptSession) -> PromptResult:
        response = session.execute()
        session.append_thread(response)
        return PromptResult.from_response(response, session=session)

    def complete_async(self, session: PromptSession):
        """Run complete() in a background thread and return a handle."""
        return start_async(self.complete, session)
