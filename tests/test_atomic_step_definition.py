"""Regression guard: atomic token 'step' is bound to the unit-of-change, not an
assistant turn, and the definition disclaims returning control to the user between
steps. Prevents the hollow where 'one observable change per step' reads as 'one
change per turn, then yield' (see design note 20260522000153-6621: atomic is
granularity control only; change-observability stays delegated to falsify).
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _atomic():
    return AXIS_KEY_TO_VALUE["method"]["atomic"]


def test_atomic_binds_step_to_unit_of_change():
    assert "a step is a single unit of change" in _atomic()


def test_atomic_disclaims_returning_control_between_steps():
    assert "do not return control to the user between steps" in _atomic()


def test_atomic_allows_yield_when_step_requires_user_input():
    assert "unless a step requires user input" in _atomic()
