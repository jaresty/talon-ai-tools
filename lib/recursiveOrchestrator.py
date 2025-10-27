"""Recursive orchestration helpers built on top of PromptPipeline."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .promptPipeline import PromptPipeline, PromptResult
from .modelSource import ModelSource


_CODE_FENCE_PATTERN = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


@dataclass
class _DelegateDirective:
    prompt: str
    destination: Optional[str]


class RecursiveOrchestrator:
    """Interpret controller directives and spawn delegated PromptPipeline runs."""

    def __init__(self, pipeline: Optional[PromptPipeline] = None) -> None:
        self._pipeline = pipeline or PromptPipeline()

    def run(
        self,
        prompt: str,
        source: ModelSource,
        destination,
        additional_source: Optional[ModelSource] = None,
    ) -> PromptResult:
        controller_result = self._pipeline.run(
            prompt,
            source,
            destination,
            additional_source,
        )

        directive = self._parse_delegate_directive(controller_result.text)
        if directive is None:
            return controller_result

        delegate_destination = directive.destination or destination
        delegate_result = self._pipeline.run(
            directive.prompt,
            source,
            delegate_destination,
            additional_source,
        )

        return delegate_result

    def _parse_delegate_directive(
        self, text: str
    ) -> Optional[_DelegateDirective]:
        payload = self._extract_json_dict(text)
        if not payload:
            return None

        if payload.get("action") not in {"delegate", "call_self"}:
            return None

        delegate_prompt = payload.get("prompt")
        if not delegate_prompt:
            return None

        destination = payload.get("response_destination")
        return _DelegateDirective(prompt=delegate_prompt, destination=destination)

    def _extract_json_dict(self, text: str) -> Optional[Dict[str, Any]]:
        candidates = [text.strip()]
        candidates.extend(match.strip() for match in _CODE_FENCE_PATTERN.findall(text))

        for candidate in candidates:
            if not candidate:
                continue
            try:
                payload = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload
        return None

