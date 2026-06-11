"""Tests for the precondition-verification clause in the probe step prompt_hint
in frame-explore and frame-debug inner cycles.

Each test asserts a key literal string from the new definition. Tests FAIL against the old
definition (which lacks precondition verification) and PASS after the edit.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.sequenceConfig import SEQUENCES


def _get_probe_hint(sequence_name: str) -> str:
    steps = SEQUENCES[sequence_name]["steps"]
    dispatch_step = next(
        (s for s in steps if s.get("type") == "dispatch" and "inner" in s),
        None,
    )
    if not dispatch_step:
        return ""
    inner_steps = dispatch_step["inner"].get("steps", [])
    for step in inner_steps:
        token = step.get("token", "")
        if "probe" in token:
            return step.get("prompt_hint", "")
    return ""


# BD1: precondition verification phase must appear
def test_frame_explore_probe_precondition_identify_claims():
    hint = _get_probe_hint("frame-explore")
    assert "identify every factual claim" in hint, (
        f"frame-explore probe prompt_hint missing precondition phrase. Got: {hint[:300]}"
    )


def test_frame_debug_probe_precondition_identify_claims():
    hint = _get_probe_hint("frame-debug")
    assert "identify every factual claim" in hint, (
        f"frame-debug probe prompt_hint missing precondition phrase. Got: {hint[:300]}"
    )


# BD2: per-claim command requirement
def test_frame_explore_probe_precondition_differ_if_false():
    hint = _get_probe_hint("frame-explore")
    assert "run a Bash command whose output would differ if the claim were false" in hint, (
        f"frame-explore probe prompt_hint missing per-claim command requirement. Got: {hint[:300]}"
    )


def test_frame_debug_probe_precondition_differ_if_false():
    hint = _get_probe_hint("frame-debug")
    assert "run a Bash command whose output would differ if the claim were false" in hint, (
        f"frame-debug probe prompt_hint missing per-claim command requirement. Got: {hint[:300]}"
    )


# BD3: permit condition
def test_frame_explore_probe_permit_condition():
    hint = _get_probe_hint("frame-explore")
    assert "output that could not exist in the repository at rest" in hint, (
        f"frame-explore probe prompt_hint missing permit condition. Got: {hint[:300]}"
    )


def test_frame_debug_probe_permit_condition():
    hint = _get_probe_hint("frame-debug")
    assert "output that could not exist in the repository at rest" in hint, (
        f"frame-debug probe prompt_hint missing permit condition. Got: {hint[:300]}"
    )


# BD4: valid-class enumeration
def test_frame_explore_probe_valid_class_enumeration():
    hint = _get_probe_hint("frame-explore")
    assert "stdout lines, stderr lines, log entries, test result records, application trace" in hint, (
        f"frame-explore probe prompt_hint missing valid-class enumeration. Got: {hint[:300]}"
    )


def test_frame_debug_probe_valid_class_enumeration():
    hint = _get_probe_hint("frame-debug")
    assert "stdout lines, stderr lines, log entries, test result records, application trace" in hint, (
        f"frame-debug probe prompt_hint missing valid-class enumeration. Got: {hint[:300]}"
    )


# BD5: old deny-list text must be gone
def test_frame_explore_probe_old_read_deny_list_removed():
    hint = _get_probe_hint("frame-explore")
    assert "A response in which every tool call is a Read tool call does not satisfy this step" not in hint, (
        "frame-explore probe prompt_hint still contains old deny-list clause"
    )


def test_frame_debug_probe_old_read_deny_list_removed():
    hint = _get_probe_hint("frame-debug")
    assert "A response in which every tool call is a Read tool call does not satisfy this step" not in hint, (
        "frame-debug probe prompt_hint still contains old deny-list clause"
    )
