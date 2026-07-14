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
    """Gate must require qualifying prior-executed result — prose assertion excluded by qualifying result type."""
    assert "prior-executed result" in _gate_def()
    assert "does not qualify regardless of its content" in _gate_def()


def test_gate_definition_condition_block_precedes_result():
    """Gate condition block must appear before the result it references (allow-list form)."""
    assert "does not appear verbatim in any qualifying result above it has not been satisfied" in _gate_def()


def test_gate_definition_has_boundary_string():
    """Gate condition block must be identified by literal 'Gate condition:' boundary string."""
    assert "'Gate condition:'" in _gate_def()


def test_gate_definition_restricts_qualifying_results():
    """Qualifying results must be command/test/endpoint executions — reads and searches excluded."""
    assert "running a test suite, or invoking an endpoint" in _gate_def()
    assert "does not qualify regardless of its content" in _gate_def()


def test_gate_definition_no_structural_property_escape():
    """Definition must not allow 'structural property' as an alternative to named literal string."""
    assert "structural property" not in _gate_def()


def test_gate_definition_per_action_cardinality():
    """Each governed action requires its own gate condition block."""
    assert "a gate condition block from a prior action does not satisfy" in _gate_def()
