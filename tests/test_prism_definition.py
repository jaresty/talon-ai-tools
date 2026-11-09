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


def test_prism_definition_contains_cognitive_frame_clause():
    """A frame is a way of construing the subject, not a topic or a vantage-point label."""
    assert (
        "a cognitive frame is a way of construing the subject that fixes what it is taken to be, what unstated background it brings, and how the same facts read under it"
        in _prism_def()
    )


def test_prism_definition_contains_shared_facts_and_frame_lines():
    """Each frame block carries Construal, Presupposes and one Reads line per shared fact."""
    d = _prism_def()
    assert "numbered list of the shared facts of the subject" in d
    assert "'Construal:' followed by a sentence beginning 'The subject is taken to be'" in d
    assert "'Presupposes:' naming the roles present under that frame" in d
    assert "one 'Reads fact K:' line per shared fact K" in d


def test_prism_definition_requires_a_differing_reading():
    """At least one shared fact is read differently by every frame."""
    assert "reads it differently from every other frame's" in _prism_def()
