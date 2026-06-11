"""Tests for the falsify token definition in axisConfig.py.

These tests assert the presence of specific key phrases in the falsify definition:
- Dimension A: allow-list clause for persistent artifacts (Gap 1)
- Dimension B: revert-run-restore clause for the retroactive case (Gap 2+3)

Each test FAILS against the old definition (which uses a deny-list clause and a
counterfactual retrospective check) and PASSES after the new definition is applied.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_falsify_allow_list_clause():
    """Dimension A: artifact must be named by an allow-list clause, not a deny-list."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "A result satisfies this token only when produced by an artifact whose file path exists in the work product" in defn


def test_falsify_retroactive_clause():
    """Dimension B: definition must name the revert-run-restore path for the retroactive case."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "If implementation already exists when this token is invoked: revert the implementation" in defn
