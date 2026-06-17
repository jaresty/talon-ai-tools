"""Tests for gate token definition — assert new structural clauses present, old underenforced clauses absent."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.axisConfig import AXIS_KEY_TO_VALUE


def _gate_def() -> str:
    return AXIS_KEY_TO_VALUE["method"]["gate"]


def test_gate_definition_contains_gate_condition_block():
    """New definition names 'gate condition block' as structural artifact — absent from old definition."""
    assert "gate condition block" in _gate_def()


def test_gate_definition_contains_earlier_transcript_position():
    """New definition requires gate condition at earlier transcript position — absent from old definition."""
    assert "earlier transcript position" in _gate_def()


def test_gate_definition_contains_later_transcript_position():
    """New definition requires named string at later transcript position — absent from old definition."""
    assert "later transcript position" in _gate_def()


def test_gate_definition_does_not_contain_prior_executed():
    """Old underenforced phrase 'prior-executed result' replaced by 'tool call result' — should be absent."""
    assert "prior-executed result" not in _gate_def()
