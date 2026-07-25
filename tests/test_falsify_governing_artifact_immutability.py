"""Tests asserting key literal strings for the governing-artifact immutability constraint.

Each test must FAIL before the edit and PASS after.

Gap (root structural conflict): the agent writes the governing artifact (test file),
which determines what executor output says. An agent can modify the test file after
running (g) to embed desired strings, then proceed to implementation using a (g) that
no longer matches the current test file. The immutability constraint closes this:
between the executor invocation that produces (g) and the governed artifact-producing
action, the governing artifact must not be modified.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_immutability_no_write_edit_between_g_and_action():
    assert "no Write or Edit tool call whose path argument matches the governing artifact file path may appear between the executor invocation that produces (g) and the governed artifact-producing action" in defn()

def test_immutability_invalidation_on_modification():
    assert "a Write or Edit tool call matching the governing artifact file path that appears after the executor invocation producing (g) and before the governed artifact-producing action invalidates (g)" in defn()
