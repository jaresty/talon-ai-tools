from __future__ import annotations

from talon_user.lib.suggestionCoordinator import (
    last_recipe_snapshot,
    recipe_header_lines_from_snapshot,
)
from talon_user.lib.modelState import GPTState


def test_recipe_header_lines_include_recipe_and_axes() -> None:
    snapshot = {
        "recipe": "describe · full · relations · cluster · bullets · fog",
        "completeness": "full",
        "scope_tokens": ["relations"],
        "method_tokens": ["cluster"],
        "form_tokens": ["bullets"],
        "channel_tokens": ["slack"],
        "directional": "fog",
        "source_kind": "clipboard",
        "destination_kind": "browser",
    }

    lines = recipe_header_lines_from_snapshot(snapshot)

    assert "recipe: describe · full · relations · cluster · bullets · fog" in lines
    assert "completeness: full" in lines
    assert "scope_tokens: relations" in lines
    assert "method_tokens: cluster" in lines
    assert "form_tokens: bullets" in lines
    assert "channel_tokens: slack" in lines
    assert "directional: fog" in lines
    assert "source: clipboard" in lines
    assert "destination: browser" in lines


def test_recipe_header_lines_include_persona_and_intent_metadata() -> None:
    snapshot = {
        "recipe": "describe \u00b7 full \u00b7 focus \u00b7 plan \u00b7 plain \u00b7 fog",
        "completeness": "full",
        "scope_tokens": ["focus"],
        "method_tokens": ["plan"],
        "form_tokens": ["plain"],
        "channel_tokens": ["slack"],
        "directional": "fog",
        "persona_preset_key": "teach_junior_dev",
        "persona_preset_label": "Teach junior dev",
        "persona_preset_spoken": "mentor",
        "persona_voice": "mentor voice",
        "persona_audience": "junior developers",
        "persona_tone": "encouraging",
        "intent_preset_key": "decide",
        "intent_preset_label": "Decision making",
        "intent_display": "Decide",
        "intent_purpose": "decide",
    }

    lines = recipe_header_lines_from_snapshot(snapshot)

    persona_line = next(line for line in lines if line.startswith("persona_preset:"))
    assert "label=Teach junior dev" in persona_line
    assert "say: persona mentor" in persona_line
    assert (
        "axes voice=mentor voice, audience=junior developers, tone=encouraging"
        in persona_line
    )

    intent_line = next(line for line in lines if line.startswith("intent_preset:"))
    assert "label=Decision making" in intent_line
    assert "display=Decide" in intent_line
    assert "say: intent decide" in intent_line
    assert "purpose=decide" in intent_line


def test_recipe_header_lines_skip_empty_axes() -> None:
    snapshot = {
        "recipe": "describe · full",
        "completeness": "full",
        "scope_tokens": [],
        "method_tokens": [],
        "form_tokens": [],
        "channel_tokens": [],
        "directional": "",
    }

    lines = recipe_header_lines_from_snapshot(snapshot)

    assert "recipe: describe · full" in lines
    assert "completeness: full" in lines
    # No scope/method/form/channel/directional lines when tokens are empty.
    assert all("scope_tokens:" not in line for line in lines)
    assert all("method_tokens:" not in line for line in lines)
    assert all("form_tokens:" not in line for line in lines)
    assert all("channel_tokens:" not in line for line in lines)
    assert all("directional:" not in line for line in lines)
    assert all("source:" not in line for line in lines)
    assert all("destination:" not in line for line in lines)


def test_last_recipe_snapshot_prefers_last_axes_tokens_over_legacy_fields() -> None:
    GPTState.reset_all()
    GPTState.last_recipe = "hydrated legacy string"
    GPTState.last_static_prompt = "infer"
    GPTState.last_completeness = "hydrated-completeness"
    GPTState.last_scope = "hydrated-scope"
    GPTState.last_method = "hydrated-method"
    GPTState.last_form = "hydrated-form"
    GPTState.last_channel = "hydrated-channel"
    GPTState.last_directional = "bog"  # should be overridden by last_axes
    GPTState.last_axes = {
        "completeness": ["full"],
        "scope": ["bound", "edges"],
        "method": ["rigor"],
        "form": ["bullets"],
        "channel": ["slack"],
        "directional": ["fog"],
    }

    snapshot = last_recipe_snapshot()

    assert snapshot["recipe"] == "hydrated legacy string"
    assert snapshot["static_prompt"] == "infer"
    assert snapshot["completeness"] == "full"
    assert snapshot["scope_tokens"] == ["bound", "edges"]
    assert snapshot["method_tokens"] == ["rigor"]
    assert snapshot["form_tokens"] == ["bullets"]
    assert snapshot["channel_tokens"] == ["slack"]
    assert snapshot["directional"] == "fog"


def test_last_recipe_snapshot_uses_fallback_when_last_axes_missing() -> None:
    GPTState.reset_all()
    GPTState.last_recipe = "infer · full · bound edges · rigor · plain"
    GPTState.last_static_prompt = "infer"
    GPTState.last_completeness = "full"
    GPTState.last_scope = "bound edges"
    GPTState.last_method = "rigor"
    GPTState.last_form = "plain"
    GPTState.last_channel = "slack"
    GPTState.last_directional = "fog"
    GPTState.last_axes = {}

    snapshot = last_recipe_snapshot()

    assert snapshot["recipe"] == "infer · full · bound edges · rigor · plain"
    assert snapshot["static_prompt"] == "infer"
    assert snapshot["completeness"] == "full"
    assert snapshot["scope_tokens"] == ["bound", "edges"]
    assert snapshot["method_tokens"] == ["rigor"]
    assert snapshot["form_tokens"] == ["plain"]
    assert snapshot["channel_tokens"] == ["slack"]
    assert snapshot["directional"] == "fog"
