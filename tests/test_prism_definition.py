"""Tests for the prism token definition — assert key literal strings from the new definition.

These tests FAIL against the old definition and PASS after the edit.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _prism_def() -> str:
    return AXIS_KEY_TO_VALUE["method"]["prism"]


def test_prism_definition_contains_numeral_clause():
    assert "where N is stated as a numeral in the enumeration artifact" in _prism_def()


def test_prism_definition_contains_single_vantage_point_clause():
    assert "Each frame names a single structural vantage point" in _prism_def()


def test_prism_definition_contains_approach_prohibition_clause():
    assert (
        "a frame body that enumerates alternative approaches, methods, or investigation paths does not satisfy this requirement"
        in _prism_def()
    )
