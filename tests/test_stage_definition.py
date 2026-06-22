"""
Falsifiable tests for the 'stage' form token definition.

Definition being tested:
  'The response presents a named-state sequence: each state is a named block
   whose name appears in at least one transition source or target field; each
   transition is a separate artifact naming its source and target state. At
   least two named state blocks and at least one transition connecting them
   must be present.'

Duration and medium-agnosticism clauses removed (animation residue).
Transitions are the sole structural differentiator from other sequence forms.
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


def test_stage_named_block_with_transition_reference():
    assert "named block whose name appears in at least one transition" in STAGE_DEF, (
        "stage definition must contain 'named block whose name appears in at least one transition' "
        "(state identity established via transition reference, not label alone)"
    )


def test_stage_transition_separate_artifact():
    assert "separate artifact" in STAGE_DEF, (
        "stage definition must contain 'separate artifact' "
        "(each transition is structurally distinct from the state blocks)"
    )


def test_stage_transition_names_source_and_target():
    assert "naming its source and target state" in STAGE_DEF, (
        "stage definition must contain 'naming its source and target state' "
        "(transition artifact must name both endpoints)"
    )


def test_stage_minimum_gate():
    assert "At least two named state blocks and at least one transition" in STAGE_DEF, (
        "stage definition must contain 'At least two named state blocks and at least one transition' "
        "(joint minimum: states and a transition connecting them)"
    )


def test_stage_no_duration_clause():
    assert "number with a time unit" not in STAGE_DEF, (
        "stage definition must not contain duration-value format (animation residue removed)"
    )


def test_stage_no_labeled_block():
    assert "labeled block" not in STAGE_DEF, (
        "stage definition must not contain 'labeled block' "
        "(replaced by 'named block whose name appears in at least one transition')"
    )
