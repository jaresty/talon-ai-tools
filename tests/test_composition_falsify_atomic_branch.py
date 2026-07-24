"""Tests asserting key literal strings for Clause C (branch constraint) in falsify+atomic composition.

Each test must FAIL before the edit and PASS after.

Gap: one governing failure could authorize a whole chain of branching logic
(insert, link, preserve prior state) by declaring it all as one "implementation depth."
The branch constraint requires each new branch construct to have an identifier from
a failure line in the governing executor result.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.compositionConfig import COMPOSITIONS


def falsify_atomic():
    for entry in COMPOSITIONS:
        if entry["name"] == "falsify+atomic":
            return entry["prose"]
    raise KeyError("falsify+atomic not found")


def test_branch_constraint_present():
    assert "branch construct" in falsify_atomic()

def test_branch_constraint_condition_or_guard():
    assert "condition or guard expression" in falsify_atomic()

def test_branch_constraint_requires_failure_line_identifier():
    assert "at least one identifier appearing in that construct's condition or guard expression also appears on a failure line in the immediately preceding governing executor result block" in falsify_atomic()

def test_branch_constraint_no_failure_line_identifier_requires_own_fail():
    assert "a branch construct whose condition or guard contains no identifier from any failure line in that block requires its own governing failure before it may be introduced" in falsify_atomic()
