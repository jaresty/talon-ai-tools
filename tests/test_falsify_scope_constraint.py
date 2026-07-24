"""Tests asserting key literal strings in the falsify implementation scope constraint clause.

Each test FAILS against the definition before the clause is added and PASSES after.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def get_falsify_definition():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_falsify_scope_constraint_label():
    """Clause label 'Implementation scope constraint' must appear in the definition."""
    defn = get_falsify_definition()
    assert "Implementation scope constraint" in defn


def test_falsify_scope_constraint_complete_identifier():
    """Full-name requirement: 'complete identifier' must appear in the definition."""
    defn = get_falsify_definition()
    assert "complete identifier" in defn


def test_falsify_scope_constraint_verbatim_substring():
    """Substring match type: 'verbatim substring' must appear in the definition."""
    defn = get_falsify_definition()
    assert "verbatim substring" in defn


def test_falsify_scope_constraint_governing_artifact_exclusion():
    """G3 exclusion: governing artifact content named as excluded from allow-list."""
    defn = get_falsify_definition()
    assert "governing artifact's content is not a valid source" in defn


def test_falsify_scope_constraint_creation_step_d_only():
    """CL1 carve-out: during creation-step exception, allow-list is (d) only."""
    defn = get_falsify_definition()
    assert "allow-list is (d) only" in defn


def test_falsify_scope_constraint_stub_not_exempt():
    """CL2 closure: reference within a stub or partial implementation is not exempt."""
    defn = get_falsify_definition()
    assert "not on the allow-list within a stub" in defn
