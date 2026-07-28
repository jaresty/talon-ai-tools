"""Tests asserting key literal strings for H3 clauses C1-C5 and description-escape closure.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


# C1 — (c) derivation from assertion call expression direct callee
def test_c1_direct_callee_of_assertion():
    assert "direct callee of the assertion call expression" in defn()

def test_c1_read_from_failure_line():
    assert "read from the failure line, not chosen independently" in defn()

def test_c1_failure_line_is_line_on_which_a_appears():
    assert "the line on which (a) appears" in defn()


# C2 — (d) derivation from assertion call expression direct callee in governing artifact
def test_c2_direct_callee_governing_artifact():
    assert "direct callee of the assertion call expression in the governing artifact" in defn()

def test_c2_only_as_argument():
    assert "only as an argument to a call expression whose callee does not contain" in defn()


# C3 — temporal gate: (c) must appear as verbatim substring of tool-result block before derivation
def test_c3_derivation_block_temporal_gate():
    assert "Derivation block temporal gate" in defn()

def test_c3_before_falsify_derivation_block():
    assert "before the Falsify derivation block" in defn()

def test_c3_not_verbatim_substring_tool_result():
    assert "does not appear as a verbatim substring of any tool-result block preceding it" in defn()


# C4 — creation-step exception requires co-occurrence of (a), (c), and direct callee containing (d)
def test_c4_abc_d_co_occur():
    assert "a line on which (a), (c), and a direct callee name containing (d) co-occur" in defn()

def test_c4_does_not_satisfy_creation_step():
    assert "does not satisfy the creation-step exception" in defn()


# C5 — scope-governing entry classification
def test_c5_scope_governing_entries():
    assert "Scope-governing entries" in defn()

def test_c5_abef_not_scope_governing():
    assert "entries (a), (b), (e), (f), and (f2) are not scope-governing entries" in defn()


# C6 — description-escape closure: executor output lines not on FAIL line are not valid sources
def test_c6_description_lines_not_valid():
    assert "test description lines" in defn()

def test_c6_docstring_echo_not_valid():
    assert "docstring echo lines" in defn()

def test_c6_parametrize_not_valid():
    assert "parametrize label lines" in defn()

def test_c6_only_fail_lines_valid_source():
    assert "applies only to (c) derivation, not to allow-list sourcing" in defn()
