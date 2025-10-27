"""High-level orchestration helpers for prompt execution and presentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from .modelPresentation import ResponsePresentation, render_for_destination
from .modelSource import ModelSource
from .modelTypes import GPTTextItem
from .promptSession import PromptSession


@dataclass
class PromptResult:
    """Structured result of a prompt run, including messages and presentation helpers."""

    messages: List[GPTTextItem]
    session: Optional[PromptSession] = None

    @classmethod
    def from_response(
        cls, response: GPTTextItem, session: Optional[PromptSession] = None
    ) -> "PromptResult":
        return cls(messages=[response], session=session)

    @classmethod
    def from_messages(
        cls, messages: Iterable[GPTTextItem], session: Optional[PromptSession] = None
    ) -> "PromptResult":
        return cls(messages=list(messages), session=session)

    @property
    def text(self) -> str:
        return self.messages[0].get("text", "") if self.messages else ""

    def presentation_for(self, destination_kind: str) -> ResponsePresentation:
        return render_for_destination(self.messages, destination_kind)

    def append_thread(self) -> None:
        if self.session is None:
            return
        if not self.messages:
            return
        self.session.append_thread(self.messages[0])


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

    def complete(self, session: PromptSession) -> PromptResult:
        response = session.execute()
        session.append_thread(response)
        return PromptResult.from_response(response, session=session)
