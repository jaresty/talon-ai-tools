"""
Falsifiable tests for the 'slides' form token definition.

Definition being implemented:
  'The response is structured as a presentation slide deck: each slide has a
   title and two to four bullet points. At least two slides must be present.
   Any visual format is permitted; the token governs structure, not medium.'

Tests FAIL when 'slides' key is absent; PASS after the key is added.
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


def test_slides_slide_deck():
    assert "slide deck" in SLIDES_DEF, (
        "slides definition must contain 'slide deck' (root criterion)"
    )


def test_slides_title_per_slide():
    assert "each slide has a title" in SLIDES_DEF, (
        "slides definition must contain 'each slide has a title' (D1)"
    )


def test_slides_bounded_points():
    assert "two to four bullet points" in SLIDES_DEF, (
        "slides definition must contain 'two to four bullet points' (D2)"
    )


def test_slides_minimum_count():
    assert "At least two slides" in SLIDES_DEF, (
        "slides definition must contain 'At least two slides' (D3)"
    )


def test_slides_notation_agnostic():
    assert "the token governs structure, not medium" in SLIDES_DEF, (
        "slides definition must contain 'the token governs structure, not medium' (hollow)"
    )
