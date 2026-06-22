"""
Falsifiable tests for the 'slides' form token definition.

Definition being implemented:
  'The response is organized as a sequence of slide units. A slide unit is a
   heading line followed by a body of at most four lines. Before emitting any
   content, count the planned slide units and confirm each has a heading line;
   a slide unit with no heading line or a body exceeding four lines does not
   satisfy this token. At least two slide units must be present. Any rendering
   format is permitted; the token governs structure, not medium.'

Tests FAIL against the old definition; PASS after the new definition is in place.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.axisConfig import AXIS_KEY_TO_VALUE


SLIDES_DEF = AXIS_KEY_TO_VALUE.get("form", {}).get("slides", "")


def test_slides_key_present():
    assert "slides" in AXIS_KEY_TO_VALUE.get("form", {}), (
        "'slides' key must be present in AXIS_KEY_TO_VALUE['form']"
    )


def test_slides_sequence_of_slide_units():
    assert "sequence of slide units" in SLIDES_DEF, (
        "slides definition must contain 'sequence of slide units' (root criterion — replaces 'slide deck')"
    )


def test_slides_unit_is_heading_line():
    assert "A slide unit is a heading line" in SLIDES_DEF, (
        "slides definition must contain 'A slide unit is a heading line' (structural definition)"
    )


def test_slides_body_at_most_four_lines():
    assert "a body of at most four lines" in SLIDES_DEF, (
        "slides definition must contain 'a body of at most four lines' (replaces bullet-only constraint)"
    )


def test_slides_derivation_gate():
    assert "count the planned slide units" in SLIDES_DEF, (
        "slides definition must contain 'count the planned slide units' (derivation gate — closes G3)"
    )


def test_slides_minimum_count():
    assert "At least two slide units" in SLIDES_DEF, (
        "slides definition must contain 'At least two slide units' (minimum count)"
    )


def test_slides_notation_agnostic():
    assert "the token governs structure, not medium" in SLIDES_DEF, (
        "slides definition must contain 'the token governs structure, not medium' (hollow-closure)"
    )
