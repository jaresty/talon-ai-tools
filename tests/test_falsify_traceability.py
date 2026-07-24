"""Tests asserting key literal strings for the governed symbol traceability requirement.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_traceability_call_chain():
    assert "reachable from the assertion call expression by following the execution call chain" in defn()

def test_traceability_governed_artifact_allowed():
    assert "the chain may pass through the test body, test setup, or the governed artifact" in defn()

def test_traceability_naming_proxy_blocked():
    assert "naming proxy and does not satisfy this requirement" in defn()

def test_traceability_substring_not_sufficient():
    assert "contains the governed symbol name as a substring but through which the governed symbol does not appear as a call expression" in defn()
