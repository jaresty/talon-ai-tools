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
    assert "(iii) symbol under-declaration" in defn
    assert "(iv) post-call line mismatch" in defn


def test_atomic_hollow_enumeration_absent():
    """Dim 5: old hollow enumeration-completeness clause must be gone."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "The enumeration is complete when no remaining open path exists" not in defn
