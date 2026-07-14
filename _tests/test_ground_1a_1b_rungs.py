"""Tests for §1a/§1b intermediate rungs in ground prompt (ADR-new).

These tests MUST FAIL before the edit to lib/groundPrompt.py and PASS after.
Governed behaviors:
- §1a decomposed sentinel present in core string
- §1b candidates sentinel present in core string
- §2 tracing rule references §1a/§1b items (not verbatim-substring only)
- means-test requires >=2 alternatives before §1 goal derived
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


def _core() -> str:
    return GROUND_PARTS_MINIMAL["core"]


def test_ground_has_1a_decomposed_sentinel():
    """§1a rung must write '§1a decomposed' as a sentinel before the means-test."""
    assert "§1a decomposed" in _core()


def test_ground_has_1b_candidates_sentinel():
    """§1b rung must write '§1b candidates' before ## Behavioral dimensions gate."""
    assert "§1b candidates" in _core()


def test_ground_s2_tracing_rule_references_1a_or_1b():
    """§2 provenance rule must require tracing to §1a or §1b items."""
    core = _core()
    assert "§1a" in core and "§1b" in core
    # The tracing rule must reference both rungs as sources for dimensions
    assert "traces to one item" in core or "trace" in core and "§1a" in core


def test_ground_means_test_requires_two_alternatives():
    """means-test must gate §1 goal derived on >=2 alternatives being present."""
    core = _core()
    # The clause must explicitly tie the §1 goal derived sentinel to >=2 alternatives
    assert "≥2 alternatives" in core and "§1 goal derived" in core


def test_ground_1a_decomposed_appears_before_means_test_gate():
    """§1a decomposed sentinel must be required before the means-test line."""
    core = _core()
    # The protocol must state that §1a decomposed must appear before the means-test
    assert "'§1a decomposed' must appear before the means-test line" in core


def test_ground_1b_candidates_appears_before_behavioral_dimensions_gate():
    """§2 gate must reference §1b candidates as its blocking condition."""
    core = _core()
    # The §2 gate must specifically name §1b candidates as what ## Behavioral dimensions must not appear before
    assert "'## Behavioral dimensions' must not appear before '§1b candidates'" in core
