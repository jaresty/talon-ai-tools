"""Tests asserting key literal strings for the governing-artifact proxy closure.

Each test must FAIL against the current definition and PASS after implementation.

Gap: an agent names a function in the test file identically to the governed symbol,
imports production under an alias, and the failure line contains the test helper's
name — satisfying (c)/(d) nominally while never calling the production function.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_governing_artifact_proxy_label():
    assert "governing-artifact proxy" in defn()

def test_governing_artifact_proxy_condition():
    assert "appears as the name of a callable definition in the content of any Write or Edit tool call whose path argument matches the governing artifact" in defn()

def test_governing_artifact_proxy_invalidates_c():
    assert "is a governing-artifact proxy and does not satisfy (c)" in defn()
