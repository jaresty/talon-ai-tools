"""Tests for the zoom completeness token definition in axisConfig.py.

BD-RESTORE: restored to 43e67d6e version — concept-description framing with process
constraints as natural language, dropping the hollow-added 'To apply:' procedural checklist.

Dimensions:
- Dim-A: concept-description framing — treats subject as exponentially-spaced buckets
- Dim-B: process constraint — both ends as explicit anchors
- Dim-C: process constraint — steps multiplicative not additive
- Dim-D: no procedural checklist — 'To apply:' must be absent
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_zoom_dim_a_concept_description_framing():
    """Dim-A: definition uses concept-description framing — exponentially-spaced buckets."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "exponentially-spaced buckets" in defn


def test_zoom_dim_b_explicit_anchors():
    """Dim-B: both ends must appear as explicit anchors."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "Both ends must appear as explicit anchors" in defn


def test_zoom_dim_c_multiplicative_steps():
    """Dim-C: steps are multiplicative not additive."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "steps are multiplicative, not additive" in defn


def test_zoom_dim_d_no_procedural_checklist():
    """Dim-D: hollow-added 'To apply:' checklist must be absent."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "To apply:" not in defn
