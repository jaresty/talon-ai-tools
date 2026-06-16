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
    """Dimension A: artifact path must be evidenced by a prior tool call in the transcript."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "the tool call names a file whose path appears as the target of a prior Write, Edit, or tool-executed directory-listing result in the transcript before the governed action" in defn


def test_falsify_retroactive_clause():
    """Dimension B: definition must name the revert-run-restore path for the retroactive case."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "If the governing artifact file already exists when this token is invoked: revert the implementation" in defn


def test_falsify_consecutive_lines():
    """Dim 3: consecutive-lines requirement must be explicit — closes Drift 3."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "on consecutive lines with no intervening content" in defn


def test_falsify_creation_step_file_nonexistence():
    """Dim 1: creation-step exception must be gated on file-nonexistence, not string absence."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "does not appear as the target of any Write or Edit tool call at any earlier position in the transcript" in defn


def test_falsify_symbol_substring():
    """Dim 4: (d) must be a literal substring of the symbol name — closes Gap 2."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "which must be a literal substring of the symbol name added or modified by the governed action" in defn


def test_falsify_old_creation_step_string_absent():
    """Dim 2: old proxy condition must be gone — no longer fires on any new string addition."""
    defn = AXIS_KEY_TO_VALUE["method"]["falsify"]
    assert "(c) is absent before the action and present after it" not in defn
