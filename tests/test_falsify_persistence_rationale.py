"""Tests asserting the epistemic rationale for governing artifact persistence in falsify.

Each test must FAIL before the edit and PASS after.

Gap: the falsify definition explains mechanical gate requirements but never states
WHY governing artifacts must persist. The purpose is ongoing governance and future
regression detection — not point-in-time confirmation. An ephemeral artifact that
satisfies (g) in session then is deleted collapses falsify back to verify.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_falsify_ongoing_governance():
    # Rationale: falsify's purpose is ongoing governance, not point-in-time confirmation
    assert "ongoing governance" in defn()


def test_falsify_continues_detecting():
    # Falsify is stronger than verify because evidence continues detecting regressions
    assert "continues detecting regressions" in defn()


def test_falsify_ephemeral_disqualified():
    # Ephemeral artifacts are explicitly disqualified regardless of (g)
    assert "ephemeral governing artifact" in defn()
