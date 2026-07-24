"""Tests asserting key literal strings in the falsify token definition.

Each test must FAIL against the old definition and PASS after the new definition
is implemented in lib/axisConfig.py.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def get_falsify_definition():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_falsify_definition_epistemic_reframe():
    """Clause 0: implementation derivation constrained exclusively to observed governing failures."""
    defn = get_falsify_definition()
    assert "constrained exclusively to observed governing failures" in defn


def test_falsify_definition_literal_file_path():
    """Artifact binding: governing failure requires invocation by literal file path."""
    defn = get_falsify_definition()
    assert "literal file path" in defn or "appears as a literal string" in defn


def test_falsify_definition_governed_symbol_as_substring():
    """Symbol attribution: failure line must contain governed symbol or assertion call expression substring."""
    defn = get_falsify_definition()
    assert "governed symbol as a substring" in defn or "governed assertion call expression" in defn


def test_falsify_definition_behavioral_value():
    """Behavioral tracing: assertion target must be a behavioral value."""
    defn = get_falsify_definition()
    assert "behavioral value" in defn


def test_falsify_definition_derivation_block_label():
    """Derivation block: literal label 'Falsify derivation:' required."""
    defn = get_falsify_definition()
    assert "Falsify derivation:" in defn


def test_falsify_definition_separate_files():
    """Separate-artifacts requirement: assertion text and governed symbol in separate artifacts/files."""
    defn = get_falsify_definition()
    assert "separate files" in defn or "separate artifacts" in defn


def test_falsify_definition_creation_step_scoping():
    """Creation-step exception: scoped to single action producing governing artifact assertion text."""
    defn = get_falsify_definition()
    assert (
        "single executor invocation whose result first produces" in defn
        or "single action that produces the governing artifact's assertion text" in defn
    )


def test_falsify_definition_refactor_clause():
    """Refactor clause: renamed symbol is a new governed symbol requiring new derivation block."""
    defn = get_falsify_definition()
    assert "renamed by a refactor is a new governed symbol" in defn


def test_falsify_definition_no_named_executor_exit():
    """G1 exit condition: token does not apply when no named executor exists."""
    defn = get_falsify_definition()
    assert "no named executor exists" in defn
