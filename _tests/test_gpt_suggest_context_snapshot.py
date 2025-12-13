try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.GPT.gpt import (
        _suggest_context_snapshot,
        _suggest_prompt_recipes_core_impl,
    )
    from talon_user.lib.modelTypes import GPTSystemPrompt
    from talon_user.lib.modelState import GPTState
else:  # Fallback for direct import paths
    from GPT.gpt import (  # type: ignore
        _suggest_context_snapshot,
        _suggest_prompt_recipes_core_impl,
    )
    from lib.modelTypes import GPTSystemPrompt  # type: ignore
    from lib.modelState import GPTState  # type: ignore

from unittest.mock import patch


def test_suggest_context_snapshot_uses_canonical_tokens():
    sys_prompt = GPTSystemPrompt(
        voice="as programmer",
        audience="to stakeholders",
        tone="directly",
        purpose="for appreciation",
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
        "purpose": "for appreciation",
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
        purpose="",
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
    class DummySource:
        modelSimpleSource = "clipboard"

        def get_text(self):
            return "dummy source text"

    sys_prompt = GPTSystemPrompt(
        voice="as programmer",
        audience="to stakeholders",
        tone="directly",
        purpose="for appreciation",
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

    mod_path = _suggest_context_snapshot.__module__
    pipeline_path = f"{mod_path}._prompt_pipeline"
    actions_path = f"{mod_path}.actions"

    with patch(f"{pipeline_path}.complete_async", return_value=DummyHandle(dummy_json)), patch(
        f"{pipeline_path}.complete", return_value=DummyHandle(dummy_json).result
    ), patch(f"{actions_path}.user.model_prompt_recipe_suggestions_gui_open"), patch(
        f"{actions_path}.user.gpt_insert_response"
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

    # Voice (prefer hydrated description; fall back to token)
    assert _contains_any(
        ["Voice: Act as a programmer", "Voice: as programmer"]
    ), content
    # Audience (hydrated or token)
    assert _contains_any(
        [
            "Audience: The audience for this is the stakeholders",
            "Audience: to stakeholders",
        ]
    ), content
    # Tone (hydrated or token)
    assert _contains_any(
        [
            "Tone: Use a direct, straightforward tone while remaining respectful.",
            "Tone: directly",
        ]
    ), content
    # Intent purpose (hydrated or token)
    assert _contains_any(
        [
            "Purpose: The goal is to express appreciation or thanks.",
            "Purpose: for appreciation",
        ]
    ), content
    # Contract axes (hydrated or token)
    assert _contains_any(
        [
            "Completeness: Important: Provide a thorough answer",
            "Completeness: full",
        ]
    ), content
    assert _contains_any(
        [
            "Scope: Important: Within the selected target, focus only on concrete actions",
            "Scope: actions",
        ]
    ), content
    assert _contains_any(
        [
            "Method: Important: Give a short plan first, then carry it out",
            "Method: plan",
        ]
    ), content
    assert _contains_any(
        [
            "Form: Important: Format the main answer as concise bullet points only",
            "Form: bullets",
        ]
    ), content
    assert _contains_any(
        [
            "Channel: Important: Format the answer for Slack",
            "Channel: slack",
        ]
    ), content
