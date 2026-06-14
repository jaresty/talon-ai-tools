"""
Falsifiable tests for the 'dialogue' form token definition.

New definition being implemented:
  'The response formats content as a dialogue between named speakers.
   Before writing turns: name each speaker and their register
   (formal/casual/expert/naive). Write each turn as `Speaker: their words`,
   maintaining the register committed above. Where the subject has a scene
   boundary or tonal shift, add a narration line in [square brackets] before
   the relevant turn.'

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


def test_dialogue_speaker_pattern():
    assert "Speaker: their words" in DIALOGUE_DEF, (
        "dialogue definition must contain 'Speaker: their words'"
    )


def test_dialogue_square_brackets():
    assert "square brackets" in DIALOGUE_DEF, (
        "dialogue definition must contain 'square brackets'"
    )


def test_dialogue_pre_production_instruction():
    assert "Before writing turns" in DIALOGUE_DEF, (
        "dialogue definition must contain 'Before writing turns' (GAP-1: pre-production commitment)"
    )


def test_dialogue_register_vocabulary():
    assert "formal/casual/expert/naive" in DIALOGUE_DEF, (
        "dialogue definition must contain 'formal/casual/expert/naive' (GAP-3: voice consistency)"
    )


def test_dialogue_narration_trigger():
    assert "scene boundary or tonal shift" in DIALOGUE_DEF, (
        "dialogue definition must contain 'scene boundary or tonal shift' (GAP-2: narration trigger)"
    )
