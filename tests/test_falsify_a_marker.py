"""Tests asserting key literal strings for the (a) failure marker validity constraint.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_a_marker_failure_line_defined_first():
    assert "Before naming (a) and (c), identify the failure line" in defn()

def test_a_marker_failure_line_transform_not_echo():
    assert "rather than by echoing content supplied as a string literal argument to an output-producing call" in defn()

def test_a_marker_read_from_failure_line():
    assert "substring of the failure line that signals the artifact detected behavior absence" in defn()

def test_a_marker_no_artifact_created():
    assert "where the governed artifact has not yet been created" in defn()

def test_a_marker_requires_artifact_executed_invalid():
    assert "requires the governed artifact to have executed in order to appear" in defn()
