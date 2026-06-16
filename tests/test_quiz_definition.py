"""Tests for the quiz token definition in AXIS_KEY_TO_DEFINITION.

Each test asserts a key literal string from the new definition that:
- FAILS against the old definition (string absent)
- PASSES after the edit (string present)

Four independently testable changes, one string per test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def get_quiz_def() -> str:
    return AXIS_KEY_TO_VALUE.get("form", {}).get("quiz", "")


def test_quiz_permit_condition_for_answer_in_same_turn():
    """Gap 1: halt-before-answer was an absence constraint.
    New definition converts it to a permit-condition with a named literal string.
    Old definition: 'An answer is permitted in the same response turn as a Predict: line only when an output-exclusive channel token is present'
    New definition: names structural condition (static document or terminal sequence artifact) instead of bar token type
    """
    defn = get_quiz_def()
    assert "An answer is permitted in the same response turn as the question only" in defn, (
        "quiz definition must state the permit-condition for answer-in-same-turn as a named literal string"
    )


def test_quiz_hook_boundary_markers():
    """Gap 2: Hook: had no named boundary markers for its structural position.
    New definition names both boundaries: after gap-reveal, before Following from:.
    """
    defn = get_quiz_def()
    assert "compliant only when it appears after the gap-reveal sentence for this concept and before the Following from: line of the next concept" in defn, (
        "quiz definition must name Hook: boundary: after gap-reveal sentence, before Following from: of next concept"
    )


def test_quiz_misconception_placement_boundary():
    """Gap 3: Misconception:/Why: had no named placement boundary.
    New definition names the boundary: in the answer block of the named concept.
    """
    defn = get_quiz_def()
    assert "compliant only when they appear in the answer block of that named concept" in defn, (
        "quiz definition must name Misconception:/Why: placement boundary: in the answer block of the named concept"
    )


def test_quiz_terminal_declaration_evaluator_criterion():
    """Gap 4: terminal declaration said 'listing all confirmed concepts' (semantic).
    New definition names the evaluator criterion: verbatim names from opening list, compared by evaluator.
    """
    defn = get_quiz_def()
    assert "an evaluator determines completeness by comparing the terminal declaration against the opening list" in defn, (
        "quiz definition must name the evaluator criterion for terminal declaration completeness"
    )
