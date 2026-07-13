"""Tests for the atomic token definition in axisConfig.py.

These tests assert the presence of specific key phrases in the new atomic definition
and the absence of the hollow enumeration-completeness clause.

Each test FAILs against the old definition and PASSes after the new definition is applied.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_atomic_fail_signal_prefix():
    """Dim 1: scope commitment must name first FAIL-signal-prefixed line — closes Gap 2."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "first line beginning with the FAIL signal prefix" in defn


def test_atomic_nonrun_recency():
    """Dim 2: non-run tool calls must not break recency — closes Gap 3."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "non-run tool calls do not break this recency" in defn


def test_atomic_symbol_same_run_result():
    """Dim 3: symbol commitment must derive from same run result as scope commitment — resolves Clash 1."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "derived from the same run result that produced the scope commitment" in defn


def test_atomic_four_escape_categories():
    """Dim 4: four named escape categories must be present — closes Drift 1."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "(i) scope inflation" in defn
    assert "(ii) stale quote" in defn
    assert "(iii) symbol cardinality" in defn
    assert "(iv) post-call line mismatch" in defn


def test_atomic_hollow_enumeration_absent():
    """Dim 5: old hollow enumeration-completeness clause must be gone."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "The enumeration is complete when no remaining open path exists" not in defn


def test_atomic_last_line_immediately_before():
    """Dim 6: scope line must appear immediately above (i) escape category line — closes D1+G1."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "line immediately above the `(i)` escape category line must be the quoted scope commitment" in defn


def test_atomic_run_result_definition():
    """Dim 7: definition must specify what counts as a tool-executed run result — closes G3."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "a result block from a test runner, build command, or linter" in defn


def test_atomic_per_call_independence():
    """Dim 8: scope line requirement must apply independently per call — closes D3+G2."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "independently" in defn


def test_atomic_escape_categories_per_call_positional():
    """Dim 9: escape categories must appear as last four lines immediately before each call — closes once-discharge gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "last five content lines begin with" in defn


def test_atomic_scope_line_above_escape_categories():
    """Dim 10: quoted scope line must appear immediately above (i) — closes mutual-exclusion conflict with escape categories."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "line immediately above the `(i)` escape category line must be the quoted scope commitment" in defn


def test_atomic_stub_new_symbol():
    """Dim 11: new-symbol calls must introduce only a stub (one-statement body) — closes implementation-depth gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "does not appear as a substring of any tool-executed result block above this call" in defn


def test_atomic_five_escape_categories():
    """Dim 12: five named escape categories must be present including (v) implementation depth."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "(v) implementation depth" in defn


def test_atomic_stub_kind_dispatch():
    """Dim 13: stub requirement dispatches on symbol kind — closes non-callable stub gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "stub requirement for its kind" in defn


def test_atomic_stub_noncallable_path():
    """Dim 14: non-callable path explicitly named — variables/constants/exported values covered."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "non-callable (variable, constant, exported value, or class field)" in defn
