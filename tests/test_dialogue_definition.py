"""
Falsifiable tests for the 'dialogue' form token definition.

Tests assert the 4 key literal strings from the verified definition:
  'The response formats content as a back-and-forth exchange between at least
   two named speakers, with each turn written as `Speaker: their words`.
   Stage directions or scene-setting may appear on separate lines in [square brackets].'

Tests FAIL against the old definition; PASS after the new definition is implemented.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.axisConfig import AXIS_KEY_TO_VALUE


DIALOGUE_DEF = AXIS_KEY_TO_VALUE.get("form", {}).get("dialogue", "")


def test_dialogue_key_present():
    assert "dialogue" in AXIS_KEY_TO_VALUE.get("form", {}), (
        "'dialogue' key must be present in AXIS_KEY_TO_VALUE['form']"
    )


def test_dialogue_back_and_forth():
    assert "back-and-forth exchange" in DIALOGUE_DEF, (
        "dialogue definition must contain 'back-and-forth exchange'"
    )


def test_dialogue_named_speakers():
    assert "at least two named speakers" in DIALOGUE_DEF, (
        "dialogue definition must contain 'at least two named speakers'"
    )


def test_dialogue_speaker_pattern():
    assert "Speaker: their words" in DIALOGUE_DEF, (
        "dialogue definition must contain 'Speaker: their words'"
    )


def test_dialogue_square_brackets():
    assert "square brackets" in DIALOGUE_DEF, (
        "dialogue definition must contain 'square brackets'"
    )
