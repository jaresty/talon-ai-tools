"""Tests asserting key literal strings for the assertion message-label extension.

Each test must FAIL against the current definition and PASS after implementation.

Gap: condition (4) of the provenance exception requires the failure line to contain
(d) or the single-assignment identifier. An agent satisfies this by embedding an
implementation identifier as the assertion message label. The extension permits a
human-readable string literal label instead, sourced from the governing artifact.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_assertion_label_extension_string_literal():
    assert "string literal that appears verbatim as the message argument to the assertion call expression in the governing artifact" in defn()

def test_assertion_label_extension_not_variable():
    assert "the message argument satisfies this only when it appears as a string literal (not a variable or computed expression)" in defn()

def test_assertion_label_extension_path_match():
    assert "in the content of a Write or Edit tool call whose path argument matches the governing artifact file path" in defn()
