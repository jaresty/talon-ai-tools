"""Tests asserting key literal strings for the bootstrap exception clause.

Each test must FAIL against the current definition and PASS after implementation.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def test_bootstrap_label():
    assert "Bootstrap exception" in defn()

def test_bootstrap_condition_transcript_observable():
    assert "no tool-result block in the transcript before the Falsify derivation block contains the governed symbol name as a verbatim substring" in defn()

def test_bootstrap_no_b_in_result():
    assert "this action may not produce a result in which (b) appears" in defn()

def test_bootstrap_immediacy():
    assert "no executor result block between the action and the invocation" in defn()

def test_bootstrap_d_on_failure_line():
    assert "with (d) appearing as a substring of the failure line" in defn()

def test_bootstrap_gate_further_actions():
    assert "no further governed artifact-producing action is permitted until this executor result appears in the transcript" in defn()
