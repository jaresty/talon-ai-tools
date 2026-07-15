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
