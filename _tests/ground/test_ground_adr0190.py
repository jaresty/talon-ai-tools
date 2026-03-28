"""Tests for ADR-0190: criteria-rung forward gate + length-override rule."""

from lib.groundPrompt import build_ground_prompt


def _p() -> str:
    return build_ground_prompt()


# ── Thread 1: criteria Gap forward gate ───────────────────────────────────────

def test_criteria_gap_not_a_stop_point():
    assert "criteria rung is not a stop point" in _p()


def test_criteria_gap_criterion_must_follow():
    p = _p()
    assert "criterion must appear" in p or "criterion must follow" in p


# ── Thread 2: length override ─────────────────────────────────────────────────

def test_length_override_present():
    assert "response length" in _p()


def test_length_override_names_continuation():
    p = _p()
    assert "continue from the current rung" in p
