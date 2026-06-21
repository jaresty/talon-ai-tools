"""
Falsifiable tests for the 'animation' form token definition.

Definition being implemented:
  'The response is organized as a named-state sequence: each state is a
   labeled block, each transition names its source state and target state,
   and each segment carries a duration value — a number with a time unit or
   a percentage position. At least two named states must be present. Any
   notation is permitted; the token governs structure, not medium.'

Tests FAIL when 'animation' key is absent; PASS after the key is added.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.axisConfig import AXIS_KEY_TO_VALUE


ANIMATION_DEF = AXIS_KEY_TO_VALUE.get("form", {}).get("animation", "")


def test_animation_key_present():
    assert "animation" in AXIS_KEY_TO_VALUE.get("form", {}), (
        "'animation' key must be present in AXIS_KEY_TO_VALUE['form']"
    )


def test_animation_named_state_sequence():
    assert "named-state sequence" in ANIMATION_DEF, (
        "animation definition must contain 'named-state sequence' (root criterion)"
    )


def test_animation_labeled_block():
    assert "labeled block" in ANIMATION_DEF, (
        "animation definition must contain 'labeled block' (D1+D2: state identifier addressability)"
    )


def test_animation_transition_source_target():
    assert "each transition names its source state and target state" in ANIMATION_DEF, (
        "animation definition must contain 'each transition names its source state and target state' (D3)"
    )


def test_animation_duration_value():
    assert "a number with a time unit or a percentage position" in ANIMATION_DEF, (
        "animation definition must contain 'a number with a time unit or a percentage position' (G2+R3)"
    )


def test_animation_minimum_states():
    assert "At least two named states" in ANIMATION_DEF, (
        "animation definition must contain 'At least two named states' (G1)"
    )


def test_animation_notation_agnostic():
    assert "the token governs structure, not medium" in ANIMATION_DEF, (
        "animation definition must contain 'the token governs structure, not medium' (G3+C1)"
    )
