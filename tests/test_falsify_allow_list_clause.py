"""Tests asserting key literal strings for the allow-list source revision and path constraint.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


# Allow-list source broadened to full (g) block
def test_allow_list_full_g_block():
    assert "the allow-list is derived from the full content of the (g) tool-result block" in defn()

def test_allow_list_named_in_active_derivation():
    assert "named in the active Falsify derivation block" in defn()

def test_allow_list_line_restriction_c_derivation_only():
    assert "applies only to (c) derivation, not to allow-list sourcing" in defn()


# Path constraint
def test_path_constraint_reachable_execution_outcome():
    assert "a construct whose introduction makes a reachable execution outcome possible" in defn()

def test_path_constraint_satisfied_condition():
    assert "the path constraint is satisfied only when every execution outcome" in defn()

def test_path_constraint_appears_in_g():
    assert "appears as a verbatim substring of the (g) tool-result block" in defn()
