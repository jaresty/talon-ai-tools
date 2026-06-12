"""Tests for the abduce step insertion between probe and vet in frame-explore
and frame-debug inner cycles, and for the vet prompt_hint gating on abduce.

Tests FAIL before the edits (abduce step absent, vet hint lacks gate clause)
and PASS after.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.sequenceConfig import SEQUENCES


def _get_inner_steps(sequence_name: str):
    steps = SEQUENCES[sequence_name]["steps"]
    dispatch_step = next(
        (s for s in steps if s.get("type") == "dispatch" and "inner" in s),
        None,
    )
    if not dispatch_step:
        return []
    return dispatch_step["inner"].get("steps", [])


def _get_inner_step_tokens(sequence_name: str):
    return [s.get("token", "") for s in _get_inner_steps(sequence_name)]


def _get_vet_hint(sequence_name: str) -> str:
    for step in _get_inner_steps(sequence_name):
        token = step.get("token", "")
        if "vet" in token:
            return step.get("prompt_hint", "")
    return ""


# BD1: abduce step present in frame-explore inner cycle
def test_frame_explore_abduce_step_present():
    tokens = _get_inner_step_tokens("frame-explore")
    assert any("abduce" in t for t in tokens), (
        f"frame-explore inner cycle missing 'show abduce' step. Got tokens: {tokens}"
    )


# BD2: abduce step present in frame-debug inner cycle
def test_frame_debug_abduce_step_present():
    tokens = _get_inner_step_tokens("frame-debug")
    assert any("abduce" in t for t in tokens), (
        f"frame-debug inner cycle missing 'show abduce' step. Got tokens: {tokens}"
    )


# BD1+BD2: abduce step appears between probe and vet in frame-explore
def test_frame_explore_abduce_between_probe_and_vet():
    tokens = _get_inner_step_tokens("frame-explore")
    probe_idx = next((i for i, t in enumerate(tokens) if "probe" in t), None)
    abduce_idx = next((i for i, t in enumerate(tokens) if "abduce" in t), None)
    vet_idx = next((i for i, t in enumerate(tokens) if "vet" in t), None)
    assert probe_idx is not None, "frame-explore: probe step not found"
    assert abduce_idx is not None, "frame-explore: abduce step not found"
    assert vet_idx is not None, "frame-explore: vet step not found"
    assert probe_idx < abduce_idx < vet_idx, (
        f"frame-explore: abduce not between probe and vet. Order: probe={probe_idx}, abduce={abduce_idx}, vet={vet_idx}"
    )


# BD1+BD2: abduce step appears between probe and vet in frame-debug
def test_frame_debug_abduce_between_probe_and_vet():
    tokens = _get_inner_step_tokens("frame-debug")
    probe_idx = next((i for i, t in enumerate(tokens) if "probe" in t), None)
    abduce_idx = next((i for i, t in enumerate(tokens) if "abduce" in t), None)
    vet_idx = next((i for i, t in enumerate(tokens) if "vet" in t), None)
    assert probe_idx is not None, "frame-debug: probe step not found"
    assert abduce_idx is not None, "frame-debug: abduce step not found"
    assert vet_idx is not None, "frame-debug: vet step not found"
    assert probe_idx < abduce_idx < vet_idx, (
        f"frame-debug: abduce not between probe and vet. Order: probe={probe_idx}, abduce={abduce_idx}, vet={vet_idx}"
    )


# BD3: frame-explore vet hint gates on abduce block
def test_frame_explore_vet_hint_gates_on_abduce():
    hint = _get_vet_hint("frame-explore")
    assert "abduce output block" in hint, (
        f"frame-explore vet prompt_hint missing abduce gate clause. Got: {hint[:300]}"
    )


# BD4: frame-debug vet hint gates on abduce block
def test_frame_debug_vet_hint_gates_on_abduce():
    hint = _get_vet_hint("frame-debug")
    assert "abduce output block" in hint, (
        f"frame-debug vet prompt_hint missing abduce gate clause. Got: {hint[:300]}"
    )
