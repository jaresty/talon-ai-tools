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


def test_gate_definition_blocks_prose_assertion():
    """Gate must require prior-executed result — not asserted in prose."""
    assert "prior-executed result" in _gate_def()
    assert "not asserted in prose" in _gate_def()


def test_gate_definition_condition_block_precedes_result():
    """Gate condition block must not appear after the result it references."""
    assert "appears after the result it references does not satisfy" in _gate_def()
