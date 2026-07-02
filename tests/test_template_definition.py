"""Tests for the form:template token definition in AXIS_KEY_TO_VALUE.

Each test asserts a key literal string from the new definition that:
- FAILS against the old definition (string absent)
- PASSES after the edit (string present)

Five independently testable structural requirements, one string per test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def get_template_def() -> str:
    return AXIS_KEY_TO_VALUE.get("form", {}).get("template", "")


def test_template_sr1_bracket_syntax():
    """SR1: [ContentType] bracket syntax requirement.
    Old definition said 'blanks, brackets, or labeled slots' — no specific syntax mandated.
    New definition requires: '[ContentType]' syntax to close the blank vs. label clash.
    """
    defn = get_template_def()
    assert "[ContentType]" in defn, (
        "template definition must mandate [ContentType] bracket syntax for slots"
    )


def test_template_sr2_noun_phrase_label():
    """SR2: label type constraint.
    Old definition said 'labeled with what it expects' — permitted full-sentence pre-fills.
    New definition requires: 'noun-phrase' to close the label-type drift finding.
    """
    defn = get_template_def()
    assert "noun-phrase" in defn, (
        "template definition must constrain labels to noun-phrases naming content type"
    )


def test_template_sr3_absent_from_response():
    """SR3: slot content absence (deny-list conversion).
    Old definition said 'the reader fills in' — no present-state observable.
    New definition requires: 'absent from the response' as a structural check.
    """
    defn = get_template_def()
    assert "absent from the response" in defn, (
        "template definition must state that slot content is absent from the response"
    )


def test_template_sr4_at_least_two_slots():
    """SR4: minimum slot count.
    Old definition had no minimum — a single slot trivially satisfied it.
    New definition requires: 'at least two slots'.
    """
    defn = get_template_def()
    assert "at least two slots" in defn, (
        "template definition must require at least two slots"
    )


def test_template_sr5_structural_connectors():
    """SR5: structural connectors allow-list (deny-list conversion).
    Old definition said 'no surrounding prose elaboration required' — no allow-list.
    New definition requires: 'Structural connectors' as the permitted non-slot content.
    """
    defn = get_template_def()
    assert "Structural connectors" in defn, (
        "template definition must name Structural connectors as the permitted non-slot content"
    )
