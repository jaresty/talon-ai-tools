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
        "style_tokens": ["bullets"],
        "directional": "fog",
    }

    lines = recipe_header_lines_from_snapshot(snapshot)

    assert "recipe: describe · full · relations · cluster · bullets · fog" in lines
    assert "completeness: full" in lines
    assert "scope_tokens: relations" in lines
    assert "method_tokens: cluster" in lines
    assert "style_tokens: bullets" in lines
    assert "directional: fog" in lines


def test_recipe_header_lines_skip_empty_axes() -> None:
    snapshot = {
        "recipe": "describe · full",
        "completeness": "full",
        "scope_tokens": [],
        "method_tokens": [],
        "style_tokens": [],
        "directional": "",
    }

    lines = recipe_header_lines_from_snapshot(snapshot)

    assert "recipe: describe · full" in lines
    assert "completeness: full" in lines
    # No scope/method/style/directional lines when tokens are empty.
    assert all("scope_tokens:" not in line for line in lines)
    assert all("method_tokens:" not in line for line in lines)
    assert all("style_tokens:" not in line for line in lines)
    assert all("directional:" not in line for line in lines)


def test_last_recipe_snapshot_prefers_last_axes_tokens_over_legacy_fields() -> None:
    GPTState.reset_all()
    GPTState.last_recipe = "hydrated legacy string"
    GPTState.last_static_prompt = "infer"
    GPTState.last_completeness = "hydrated-completeness"
    GPTState.last_scope = "hydrated-scope"
    GPTState.last_method = "hydrated-method"
    GPTState.last_style = "hydrated-style"
    GPTState.last_directional = "fog"
    GPTState.last_axes = {
        "completeness": ["full"],
        "scope": ["bound", "edges"],
        "method": ["rigor"],
        "style": ["plain"],
    }

    snapshot = last_recipe_snapshot()

    assert snapshot["recipe"] == "hydrated legacy string"
    assert snapshot["static_prompt"] == "infer"
    assert snapshot["completeness"] == "full"
    assert snapshot["scope_tokens"] == ["bound", "edges"]
    assert snapshot["method_tokens"] == ["rigor"]
    assert snapshot["style_tokens"] == ["plain"]
    assert snapshot["directional"] == "fog"


def test_last_recipe_snapshot_uses_fallback_when_last_axes_missing() -> None:
    GPTState.reset_all()
    GPTState.last_recipe = "infer · full · bound edges · rigor · plain"
    GPTState.last_static_prompt = "infer"
    GPTState.last_completeness = "full"
    GPTState.last_scope = "bound edges"
    GPTState.last_method = "rigor"
    GPTState.last_style = "plain"
    GPTState.last_directional = "fog"
    GPTState.last_axes = {}

    snapshot = last_recipe_snapshot()

    assert snapshot["recipe"] == "infer · full · bound edges · rigor · plain"
    assert snapshot["static_prompt"] == "infer"
    assert snapshot["completeness"] == "full"
    assert snapshot["scope_tokens"] == ["bound", "edges"]
    assert snapshot["method_tokens"] == ["rigor"]
    assert snapshot["style_tokens"] == ["plain"]
    assert snapshot["directional"] == "fog"
