"""Tests asserting key literal strings for the (d) specificity constraint.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_d_is_identifier_on_failure_line():
    assert "(d) must be the identifier that appears as a substring of the failure line in (g) — not a symbol that contains or is associated with that identifier" in defn()

def test_d_narrower_identifier_wins():
    assert "if the failure line names a narrower identifier, that narrower identifier is (d) regardless of which broader symbol was invoked to reach it" in defn()
