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
    assert "sequence of discrete slide units" in SLIDES_DEF, (
        "slides definition must contain 'sequence of discrete slide units' (root criterion)"
    )


def test_slides_notation_agnostic():
    assert "the token governs the sequence structure, not the content type or medium" in SLIDES_DEF, (
        "slides definition must contain 'the token governs the sequence structure, not the content type or medium'"
    )
