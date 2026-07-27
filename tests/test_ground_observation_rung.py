"""Tests asserting the observation-as-rung and isolation constraint additions to groundPrompt.py.

Each test must FAIL before the edit and PASS after.

Gap: build_ground_prompt() does not name the behavioral observation (FAIL output) as the
epistemic pivot rung where reality enters the chain, and does not state that each rung must
derive exclusively from the immediately preceding rung's output (not from earlier rungs).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.groundPrompt import build_ground_prompt, GROUND_PARTS_MINIMAL


def narrative():
    return build_ground_prompt()


def core():
    return GROUND_PARTS_MINIMAL["core"]


def test_ground_observation_epistemic_pivot():
    # The behavioral observation is the rung where reality enters the chain
    assert "the rung where reality enters the chain" in narrative()


def test_ground_isolation_in_core():
    # Isolation constraint must be in the enforcement text, not just narrative
    assert "rung that references content from any rung earlier than its immediate predecessor" in core()


def test_ground_derives_exclusively():
    # The stronger "exclusively from the immediately preceding rung" must appear
    assert "derives exclusively from the immediately preceding rung" in narrative() or \
           "derives exclusively from the immediately preceding rung" in core()
