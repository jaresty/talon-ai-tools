"""
Falsifiable tests for the 'dialogue' form token definition.

These tests assert the 4 key literal strings from the verified definition:
  'The response presents content as a sequence of turns from at least two distinct
   speakers; each turn begins with a name or role label followed by a colon on the
   same line as the speaker's content.'

Tests FAIL when the 'dialogue' key is absent from axisConfig.py.
Tests PASS after the key is added with the correct definition.
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


def test_dialogue_sequence_of_turns():
    assert "sequence of turns" in DIALOGUE_DEF, (
        "dialogue definition must contain 'sequence of turns'"
    )


def test_dialogue_two_distinct_speakers():
    assert "at least two distinct speakers" in DIALOGUE_DEF, (
        "dialogue definition must contain 'at least two distinct speakers'"
    )


def test_dialogue_colon_pattern():
    assert "name or role label followed by a colon" in DIALOGUE_DEF, (
        "dialogue definition must contain 'name or role label followed by a colon'"
    )


def test_dialogue_same_line():
    assert "on the same line as the speaker" in DIALOGUE_DEF, (
        "dialogue definition must contain 'on the same line as the speaker'"
    )


def test_dialogue_narration_brackets():
    assert "Unattributed content may appear on its own line enclosed in square brackets" in DIALOGUE_DEF, (
        "dialogue definition must contain 'Unattributed content may appear on its own line enclosed in square brackets'"
    )
