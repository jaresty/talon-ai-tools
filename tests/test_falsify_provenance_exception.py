"""Tests asserting key literal strings for the assertion-target provenance exception.

Each test must FAIL against the current definition and PASS after implementation.

Gap: the (d) clause's 'not used only as an argument' restriction blocks the canonical
  const result = await governed(...);
  expect(result.property).toBe(value);
pattern. The provenance exception suspends that restriction when the identifier is
provably sourced from the governed call by static inspection of the governing artifact.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_provenance_exception_label():
    assert "Assertion-target provenance exception" in defn()

def test_provenance_exception_suspension():
    assert "the restriction that (d) must appear as a direct callee of the assertion call expression is suspended" in defn()

def test_provenance_exception_single_assignment():
    assert "assigned exactly once in the governing artifact" in defn()

def test_provenance_exception_outermost_callee():
    assert "outermost non-structural callee" in defn()

def test_provenance_exception_structural_strip():
    assert "after stripping any leading" in defn()

def test_provenance_exception_identifier_as_argument():
    assert "that identifier appears as an argument to an assertion call expression" in defn()

def test_provenance_exception_no_reassignment():
    assert "does not appear on the left-hand side of any assignment expression between its initial assignment and the assertion" in defn()

def test_provenance_exception_failure_line():
    assert "contains either (d) or the identifier from condition (1) as a substring" in defn()
