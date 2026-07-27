"""Tests asserting the rung-type homogeneity constraint in groundPrompt.py.

Each test must FAIL before the edit and PASS after.

Gap: build_ground_prompt() does not state that all rungs before the behavioral
observation must be successive precision-narrowings of the same governed behavior.
A model can satisfy heading ordering while switching rung type mid-ladder —
inserting preflight checks, new deliverables, or task categories as rungs.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.groundPrompt import build_ground_prompt, GROUND_PARTS_MINIMAL


def narrative():
    return build_ground_prompt()


def test_ground_homogeneity_narrative():
    # Narrative must state that introducing a new kind of artifact is not a narrowing
    assert "introducing a new kind of artifact" in narrative()


def test_ground_homogeneity_task_category():
    # Narrative must name task category as a disqualifying rung type
    assert "task category as a rung" in narrative()


def test_ground_homogeneity_example():
    # Example ladder must carry the homogeneity annotation
    assert "rung types must stay homogeneous" in narrative()
