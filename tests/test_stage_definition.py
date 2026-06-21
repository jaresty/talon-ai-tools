"""
Falsifiable tests for the 'stage' form token definition.

Definition being implemented:
  'The response is organized as a named-state sequence: each state is a
   labeled block, each transition names its source state and target state,
   and each segment carries a duration value — a number with a time unit or
   a percentage position. At least two named states must be present. Any
   notation is permitted; the token governs structure, not medium.'

Tests FAIL when 'stage' key is absent; PASS after the key is added.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.axisConfig import AXIS_KEY_TO_VALUE


STAGE_DEF = AXIS_KEY_TO_VALUE.get("form", {}).get("stage", "")


def test_stage_key_present():
    assert "stage" in AXIS_KEY_TO_VALUE.get("form", {}), (
        "'stage' key must be present in AXIS_KEY_TO_VALUE['form']"
    )


def test_stage_named_state_sequence():
    assert "named-state sequence" in STAGE_DEF, (
        "stage definition must contain 'named-state sequence' (root criterion)"
    )


def test_stage_labeled_block():
    assert "labeled block" in STAGE_DEF, (
        "stage definition must contain 'labeled block' (D1+D2: state identifier addressability)"
    )


def test_stage_transition_source_target():
    assert "each transition names its source state and target state" in STAGE_DEF, (
        "stage definition must contain 'each transition names its source state and target state' (D3)"
    )


def test_stage_duration_value():
    assert "a number with a time unit or a percentage position" in STAGE_DEF, (
        "stage definition must contain 'a number with a time unit or a percentage position' (G2+R3)"
    )


def test_stage_minimum_states():
    assert "At least two named states" in STAGE_DEF, (
        "stage definition must contain 'At least two named states' (G1)"
    )


def test_stage_notation_agnostic():
    assert "the token governs structure, not medium" in STAGE_DEF, (
        "stage definition must contain 'the token governs structure, not medium' (G3+C1)"
    )
