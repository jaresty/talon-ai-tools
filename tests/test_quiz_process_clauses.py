"""Tests asserting two process clauses (reframed as structural constraints) added to quiz form token.

Each test must FAIL before the edit and PASS after.

Clause 5 (Learner-safety): pass/skip/I don't know in human message turn triggers reveal
without gap-reveal comparison; satisfies prediction requirement for that concept.

Clause 6 (Bounded-round): Quiz purpose: and Stopping condition: lines required before
first question; Round complete: closes the round when stopping condition is satisfied.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["form"]["quiz"]


def test_quiz_learner_safety():
    assert "without gap-reveal comparison" in defn()


def test_quiz_purpose_declaration():
    assert "Quiz purpose:" in defn()


def test_quiz_round_complete():
    assert "Round complete:" in defn()


def test_quiz_pass_satisfies():
    assert "satisfies the prediction requirement" in defn()
