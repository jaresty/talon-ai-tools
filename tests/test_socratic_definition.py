"""Tests for the socratic token definition in AXIS_KEY_TO_VALUE.

Each test asserts a key literal string from the new definition that:
- FAILS against the old definition (string absent)
- PASSES after the edit (string present)

Four independently testable structural requirements, one string per test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def get_socratic_def() -> str:
    return AXIS_KEY_TO_VALUE.get("form", {}).get("socratic", "")


def test_socratic_sr1_claim_precondition():
    """SR1: claim-presence precondition.
    Old definition had no requirement to name a specific claim before questioning.
    New definition requires: 'before producing any question, name the specific claim'
    """
    defn = get_socratic_def()
    assert "Before producing any question, name the specific claim" in defn, (
        "socratic definition must require naming the specific claim before the first question"
    )


def test_socratic_sr2_phrase_targeting():
    """SR2: claim-targeting addressability.
    Old definition said 'names an assumption, definition, or gap' — no user-input phrase required.
    New definition requires: 'each question must quote or name a specific phrase from the user's input'
    """
    defn = get_socratic_def()
    assert "Each question must quote or name a specific phrase from the user's input" in defn, (
        "socratic definition must require each question to quote or name a specific phrase from the user's input"
    )


def test_socratic_sr3_no_declarative_assertion():
    """SR3: within-turn conclusion prohibition (C1 clash resolution).
    Old definition used 'rather than stating conclusions' (deny-list, temporal escape via 'until').
    New definition converts to allow-list: 'no declarative sentence asserting the agent's position'
    """
    defn = get_socratic_def()
    assert "no declarative sentence asserting the agent's position" in defn, (
        "socratic definition must prohibit declarative sentences asserting the agent's position"
    )


def test_socratic_sr4_explicit_invitation():
    """SR4: exchange framing / escape hatch broadened.
    Old definition narrowly named 'summary' as the only escape condition.
    New definition requires: 'explicit invitation for the user to respond'
    """
    defn = get_socratic_def()
    assert "explicit invitation for the user to respond" in defn, (
        "socratic definition must require ending with an explicit invitation for the user to respond"
    )
