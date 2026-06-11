"""Tests for the live-signal constraint clause in frame-explore and frame-debug prism prompt_hints.

Each test asserts a key literal string from the new clause definition. Tests must FAIL against
the old definition and PASS after the edit.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.sequenceConfig import SEQUENCES


def _get_prism_hint(sequence_name: str) -> str:
    steps = SEQUENCES[sequence_name]["steps"]
    for step in steps:
        if step.get("token", "").startswith("make method:prism") or step.get("token") == "make method:prism":
            return step.get("prompt_hint", "")
    return ""


def test_frame_explore_live_signal_clause_root_criterion():
    hint = _get_prism_hint("frame-explore")
    assert "cannot exist in the repository at rest" in hint, (
        f"frame-explore prism prompt_hint missing root criterion phrase. Got: {hint[:200]}"
    )


def test_frame_explore_live_signal_clause_exclusion_list():
    hint = _get_prism_hint("frame-explore")
    assert "type definitions, mapping tables, switch branches, schema files, function signatures" in hint, (
        f"frame-explore prism prompt_hint missing code-artifact exclusion list. Got: {hint[:200]}"
    )


def test_frame_explore_live_signal_clause_conditional_prediction():
    hint = _get_prism_hint("frame-explore")
    assert "would show, would appear, could be observed as" in hint, (
        f"frame-explore prism prompt_hint missing conditional-prediction closure strings. Got: {hint[:200]}"
    )


def test_frame_explore_live_signal_clause_valid_classes():
    hint = _get_prism_hint("frame-explore")
    assert "stdout lines, stderr lines, log entries, test result records, application trace" in hint, (
        f"frame-explore prism prompt_hint missing valid signal class enumeration. Got: {hint[:200]}"
    )


def test_frame_debug_live_signal_clause_root_criterion():
    hint = _get_prism_hint("frame-debug")
    assert "cannot exist in the repository at rest" in hint, (
        f"frame-debug prism prompt_hint missing root criterion phrase. Got: {hint[:200]}"
    )


def test_frame_debug_live_signal_clause_exclusion_list():
    hint = _get_prism_hint("frame-debug")
    assert "type definitions, mapping tables, switch branches, schema files, function signatures" in hint, (
        f"frame-debug prism prompt_hint missing code-artifact exclusion list. Got: {hint[:200]}"
    )


def test_frame_debug_live_signal_clause_conditional_prediction():
    hint = _get_prism_hint("frame-debug")
    assert "would show, would appear, could be observed as" in hint, (
        f"frame-debug prism prompt_hint missing conditional-prediction closure strings. Got: {hint[:200]}"
    )


def test_frame_debug_live_signal_clause_valid_classes():
    hint = _get_prism_hint("frame-debug")
    assert "stdout lines, stderr lines, log entries, test result records, application trace" in hint, (
        f"frame-debug prism prompt_hint missing valid signal class enumeration. Got: {hint[:200]}"
    )
