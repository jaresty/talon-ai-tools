"""Tests for the rebase method token definition in axisConfig.py.

These tests assert the presence of specific structural artifacts in the rebase definition.
Each test FAILS before the token is added and PASSES after.

Dimensions:
- D1: definition key present in method token dict
- D2: short_label present
- D3: kanji present
- D4: routing_concept present
- D5: category present in AXIS_KEY_TO_CATEGORY
- D6: 'Original basis:' label required (R1/C1 closure)
- D7: 'What this reveals:' label required (R3/C3 closure)
- D8: single-basis constraint (C5 closure — distinguish from prism)
- D9: heuristics entry present
- D10: distinctions entry present
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import (
    AXIS_KEY_TO_VALUE,
    AXIS_KEY_TO_LABEL,
    AXIS_KEY_TO_KANJI,
    AXIS_KEY_TO_ROUTING_CONCEPT,
    AXIS_KEY_TO_CATEGORY,
    AXIS_TOKEN_METADATA,
)


def test_rebase_definition_key():
    """D1: 'rebase' key present in method token definitions dict."""
    assert "rebase" in AXIS_KEY_TO_VALUE["method"]


def test_rebase_short_label():
    """D2: short_label present for rebase."""
    assert "rebase" in AXIS_KEY_TO_LABEL["method"]


def test_rebase_kanji():
    """D3: kanji present for rebase."""
    assert "rebase" in AXIS_KEY_TO_KANJI["method"]


def test_rebase_routing_concept():
    """D4: routing_concept present for rebase."""
    assert "rebase" in AXIS_KEY_TO_ROUTING_CONCEPT["method"]


def test_rebase_category():
    """D5: category present in AXIS_KEY_TO_CATEGORY for rebase."""
    assert "rebase" in AXIS_KEY_TO_CATEGORY["method"]


def test_rebase_original_basis_label():
    """D6: definition requires 'Original basis:' label (structural R1 closure)."""
    defn = AXIS_KEY_TO_VALUE["method"]["rebase"]
    assert "Original basis:" in defn


def test_rebase_what_this_reveals_label():
    """D7: definition requires 'What this reveals:' label (structural R3 closure)."""
    defn = AXIS_KEY_TO_VALUE["method"]["rebase"]
    assert "What this reveals:" in defn


def test_rebase_single_basis_constraint():
    """D8: definition encodes single named alternative basis (C5 closure — not prism enumeration)."""
    defn = AXIS_KEY_TO_VALUE["method"]["rebase"]
    assert "single named alternative basis" in defn


def test_rebase_heuristics_entry():
    """D9: heuristics entry present in AXIS_TOKEN_METADATA for rebase."""
    assert "rebase" in AXIS_TOKEN_METADATA["method"]
    assert "heuristics" in AXIS_TOKEN_METADATA["method"]["rebase"]
    assert len(AXIS_TOKEN_METADATA["method"]["rebase"]["heuristics"]) > 0


def test_rebase_distinctions_entry():
    """D10: distinctions entry present in AXIS_TOKEN_METADATA for rebase."""
    assert "rebase" in AXIS_TOKEN_METADATA["method"]
    assert "distinctions" in AXIS_TOKEN_METADATA["method"]["rebase"]
    assert len(AXIS_TOKEN_METADATA["method"]["rebase"]["distinctions"]) > 0
