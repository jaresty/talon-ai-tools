"""Tests for composition config entries in compositionConfig.py."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.compositionConfig import COMPOSITIONS


def _get_entry(name):
    for entry in COMPOSITIONS:
        if entry["name"] == name:
            return entry["prose"]
    return None


def test_falsify_atomic_has_implementation_depth():
    """(v) implementation depth must appear in the falsify+atomic composition config entry."""
    prose = _get_entry("falsify+atomic")
    assert prose is not None, "falsify+atomic entry not found"
    assert "(v) implementation depth" in prose


def test_falsify_atomic_mechanism_level_fail_required():
    """Draft A v3.1: mechanism-level behavior requires its own governing FAIL."""
    prose = _get_entry("falsify+atomic")
    assert prose is not None, "falsify+atomic entry not found"
    assert "mechanism-level behavior" in prose


def test_falsify_atomic_outcome_contract_does_not_govern_mechanism():
    """Draft A v3.1: outcome-contract FAIL does not automatically govern mechanism-level behaviors."""
    prose = _get_entry("falsify+atomic")
    assert prose is not None, "falsify+atomic entry not found"
    assert "outcome-contract FAIL does not automatically govern" in prose


def test_falsify_atomic_mechanism_fail_names_distinct_identifier():
    """Draft A v3.1: FAIL failure line must name identifier not a substring of outcome-contract symbol."""
    prose = _get_entry("falsify+atomic")
    assert prose is not None, "falsify+atomic entry not found"
    assert "does not appear as a substring of the outcome-contract symbol" in prose


def test_falsify_atomic_mechanism_identifier_in_assert_statement():
    """Draft A v3.1: mechanism identifier must appear in assert statement of governing artifact."""
    prose = _get_entry("falsify+atomic")
    assert prose is not None, "falsify+atomic entry not found"
    assert "assert statement of the governing artifact" in prose
