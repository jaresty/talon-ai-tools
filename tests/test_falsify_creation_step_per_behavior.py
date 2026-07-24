"""Tests asserting key literal strings for the per-behavior creation-step clarification.

Each test must FAIL before the edit and PASS after.

Gap: the creation-step exception's "(c) is absent before the action" condition can be
read as applying to (c) for any behavior of the governed symbol, blocking addition of
a new assertion to an existing test file where (c) for prior behaviors is already present.
The clarification makes explicit that the absent/present condition is evaluated for the
specific (c) of the behavior being added, not for any other behavior's (c).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_creation_step_per_behavior_condition_scoped():
    assert "the absent/present condition is evaluated for the specific (c) of the behavior being added, not for (c) of any other behavior" in defn()

def test_creation_step_prior_c_does_not_block():
    assert "prior occurrences of (c) for other behaviors of the same governed symbol do not prevent the creation-step exception from applying to a new behavior" in defn()
