"""Tests for PLANNING_DIRECTIVE definition in metaPromptConfig.py.

GAP-1 closure: deny-list clause replaced with allow-list scoped to planning block interior.
GAP-4 closure: permit condition requiring task content after planning block.
"""

from lib.metaPromptConfig import PLANNING_DIRECTIVE


def test_gap1_allow_list_clause_present():
    """GAP-1: planning block interior allow-list clause must be present."""
    assert "All text within the planning block (between 'SECTION 1 —' and the end of 'SECTION 4 —') belongs to one of the four named sections" in PLANNING_DIRECTIVE


def test_gap1_deny_list_clause_absent():
    """GAP-1: old deny-list clause (entire-response scope) must be removed."""
    assert "A response containing any text that does not belong to one of the four named sections does not satisfy this requirement" not in PLANNING_DIRECTIVE


def test_gap4_permit_condition_present():
    """GAP-4: permit condition requiring task content after planning block must be present."""
    assert "Task content appears after the planning block — a response ending at SECTION 4 without task content does not satisfy this requirement" in PLANNING_DIRECTIVE


def test_gap_output_category_not_reasoning_artifact():
    """GAP-OUTPUT-CATEGORY BD-1: 'not a reasoning artifact' must appear in PLANNING_DIRECTIVE."""
    assert "not a reasoning artifact" in PLANNING_DIRECTIVE


def test_gap_output_category_response_itself():
    """GAP-OUTPUT-CATEGORY BD-2: 'the response itself up to this point' must appear."""
    assert "the response itself up to this point" in PLANNING_DIRECTIVE


def test_gap_output_category_section1_literal_string_gate():
    """GAP-OUTPUT-CATEGORY BD-3: literal string gate on SECTION 1 — in user-facing text must appear."""
    assert "does not appear in the user-facing text has not produced the planning block" in PLANNING_DIRECTIVE
