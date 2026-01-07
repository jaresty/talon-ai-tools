try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.axisMappings import axis_hydrate_tokens
    from talon_user.lib.personaConfig import persona_hydrate_tokens
    from talon_user.GPT.gpt import (
        _suggest_context_snapshot,
        _suggest_prompt_recipes_core_impl,
    )
    from talon_user.lib.modelTypes import GPTSystemPrompt
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelSource import ModelSource
else:  # Fallback for direct import paths
    from talon import settings  # type: ignore
    from lib.axisMappings import axis_hydrate_tokens  # type: ignore
    from lib.personaConfig import persona_hydrate_tokens  # type: ignore
    from GPT.gpt import (  # type: ignore
        _suggest_context_snapshot,
        _suggest_prompt_recipes_core_impl,
    )
    from lib.modelTypes import GPTSystemPrompt  # type: ignore
    from lib.modelState import GPTState  # type: ignore
    from lib.modelSource import ModelSource  # type: ignore

import sys
from typing import cast
from unittest.mock import patch


def test_suggest_context_snapshot_uses_canonical_tokens():
    sys_prompt = GPTSystemPrompt(
        voice="as programmer",
        audience="to stakeholders",
        tone="directly",
        intent="appreciate",
        completeness="full",
        scope="actions",
        method="plan",
        form="bullets",
        channel="slack",
    )

    snapshot = _suggest_context_snapshot(sys_prompt)

    assert snapshot == {
        "voice": "as programmer",
        "audience": "to stakeholders",
        "tone": "directly",
        "intent": "appreciate",
        "completeness": "full",
        "scope": "actions",
        "method": "plan",
        "form": "bullets",
        "channel": "slack",
    }


def test_suggest_context_snapshot_drops_hydrated_strings():
    sys_prompt = GPTSystemPrompt(
        voice="freeform voice description",
        audience="freeform audience description",
        tone="freeform tone description",
        intent="",
        completeness="",
        scope="",
        method="",
        form="",
        channel="",
    )

    snapshot = _suggest_context_snapshot(sys_prompt)

    # Hydrated/descriptive strings that are not known tokens should be dropped.
    assert snapshot["voice"] == ""
    assert snapshot["audience"] == ""
    assert snapshot["tone"] == ""


def test_suggest_uses_hydrated_system_prompt_for_llm():
    class DummySource(ModelSource):
        modelSimpleSource = "clipboard"

        def get_text(self):  # type: ignore[override]
            return "dummy source text"

    sys_prompt = GPTSystemPrompt(
        voice="as programmer",
        audience="to stakeholders",
        tone="directly",
        intent="appreciate",
        completeness="full",
        scope="actions",
        method="plan",
        form="bullets",
        channel="slack",
    )
    GPTState.system_prompt = sys_prompt

    # Stub pipeline to avoid real model calls.
    class DummyHandle:
        def __init__(self, text):
            self.result = type("R", (), {"text": text})

        def wait(self, timeout=None):
            return None

    dummy_json = '{"suggestions":[{"name":"demo","recipe":"infer · full · actions · plan · bullets · slack · fog"}]}'

    mod = sys.modules[_suggest_context_snapshot.__module__]

    with (
        patch.object(
            mod._prompt_pipeline, "complete_async", return_value=DummyHandle(dummy_json)
        ),
        patch.object(
            mod._prompt_pipeline,
            "complete",
            return_value=DummyHandle(dummy_json).result,
        ),
        patch.object(mod.actions.user, "model_prompt_recipe_suggestions_gui_open"),
        patch.object(mod.actions.user, "gpt_insert_response"),
    ):
        _suggest_prompt_recipes_core_impl(DummySource(), "")

    # Ensure system prompt was included and hydrated in the request sent to the LLM.
    system_messages = [
        m for m in GPTState.request.get("messages", []) if m.get("role") == "system"
    ]
    assert system_messages, "system prompt was not attached to suggest request"
    parts = []
    for msg in system_messages:
        content_raw = msg.get("content", "")
        if isinstance(content_raw, list):
            parts.append(" ".join(str(item.get("text", "")) for item in content_raw))
        else:
            parts.append(str(content_raw))
    content = " ".join(parts)

    def _contains_any(subs):
        return any(sub in content for sub in subs)

    # Voice
    assert _contains_any(["Voice: Act as a programmer"]), content
    # Audience
    assert _contains_any(["Audience: The audience for this is the stakeholders"]), (
        content
    )
    # Tone
    assert _contains_any(
        [
            "Tone: The response speaks directly and straightforwardly while remaining respectful."
        ]
    ), content
    # Intent intent
    assert _contains_any(["Intent: The response expresses appreciation or thanks."]), (
        content
    )
    # Contract axes
    assert _contains_any(
        [
            "Completeness: The response provides a thorough answer for normal use, covering all major aspects without needing every micro-detail.",
        ]
    ), content
    assert _contains_any(
        [
            "Scope: The response stays within the selected target and focuses only on concrete actions or tasks a user or team could take, leaving out background analysis or explanation.",
        ]
    ), content
    assert _contains_any(
        [
            "Method: The response offers a short plan first and then carries it out, clearly separating the plan from the execution.",
        ]
    ), content
    assert _contains_any(
        [
            "Form: The response presents the main answer as concise bullet points only, avoiding long paragraphs.",
        ]
    ), content
    assert _contains_any(
        [
            "Channel: The response formats the answer for Slack using appropriate Markdown, mentions, and code blocks while avoiding channel-irrelevant decoration.",
        ]
    ), content


def test_suggest_hydrates_system_prompt_defaults_from_settings():
    class DummySource(ModelSource):
        modelSimpleSource = "clipboard"

        def get_text(self):  # type: ignore[override]
            return "defaults source text"

    defaults = {
        "user.model_default_voice": ["as programmer"],
        "user.model_default_audience": ["to stakeholders"],
        "user.model_default_tone": ["directly"],
        "user.model_default_intent": ["appreciate"],
        "user.model_default_completeness": "full",
        "user.model_default_scope": "actions",
        "user.model_default_method": "plan",
        "user.model_default_form": "bullets",
        "user.model_default_channel": "slack",
    }
    prior = {key: settings.get(key) for key in defaults}
    prior_prompt = getattr(GPTState, "system_prompt", None)
    try:
        for key, value in defaults.items():
            settings.set(key, value)
        GPTState.system_prompt = GPTSystemPrompt()

        class DummyHandle:
            def __init__(self, text):
                self.result = type("R", (), {"text": text})

            def wait(self, timeout=None):
                return None

        dummy_json = '{"suggestions":[{"name":"demo","recipe":"infer · full · actions · plan · bullets · slack · fog"}]}'

        mod = sys.modules[_suggest_context_snapshot.__module__]

        with (
            patch.object(
                mod._prompt_pipeline,
                "complete_async",
                return_value=DummyHandle(dummy_json),
            ),
            patch.object(
                mod._prompt_pipeline,
                "complete",
                return_value=DummyHandle(dummy_json).result,
            ),
            patch.object(mod.actions.user, "model_prompt_recipe_suggestions_gui_open"),
            patch.object(mod.actions.user, "gpt_insert_response"),
        ):
            _suggest_prompt_recipes_core_impl(DummySource(), "")

        system_messages = [
            m for m in GPTState.request.get("messages", []) if m.get("role") == "system"
        ]
        assert system_messages, "system prompt was not attached to suggest request"

        parts = []
        for msg in system_messages:
            content_raw = msg.get("content", "")
            if isinstance(content_raw, list):
                parts.append(
                    " ".join(str(item.get("text", "")) for item in content_raw)
                )
            else:
                parts.append(str(content_raw))
        content = " ".join(parts)

        persona_expected = {
            "Voice: Act as a programmer",
            "Audience: The audience for this is the stakeholders",
            "Tone: The response speaks directly and straightforwardly while remaining respectful.",
            "Intent: The response expresses appreciation or thanks.",
        }
        for needle in persona_expected:
            assert needle in content

        axis_expected = [
            "Completeness: " + axis_hydrate_tokens("completeness", ["full"])[0],
            "Scope: " + " ".join(axis_hydrate_tokens("scope", ["actions"])),
            "Method: " + " ".join(axis_hydrate_tokens("method", ["plan"])),
            "Form: " + " ".join(axis_hydrate_tokens("form", ["bullets"])),
            "Channel: " + " ".join(axis_hydrate_tokens("channel", ["slack"])),
        ]
        for needle in axis_expected:
            assert needle in content
    finally:
        for key, value in prior.items():
            settings.set(key, value)
        if isinstance(prior_prompt, GPTSystemPrompt):
            GPTState.system_prompt = cast(GPTSystemPrompt, prior_prompt)
        else:
            GPTState.system_prompt = GPTSystemPrompt()
