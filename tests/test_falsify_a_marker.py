"""Tests asserting key literal strings for the (a) failure marker validity constraint.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_a_marker_appears_when_artifact_absent():
    assert "appears in executor output when the governed artifact is absent" in defn()

def test_a_marker_no_artifact_created():
    assert "where the governed artifact has not yet been created" in defn()

def test_a_marker_requires_artifact_executed_invalid():
    assert "requires the governed artifact to have executed in order to appear" in defn()

def test_a_marker_independence_from_test_body():
    assert "a string appearing in the assertion message, description, or name written by the agent does not satisfy (a)" in defn()
