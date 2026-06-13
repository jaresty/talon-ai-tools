"""Tests for the zoom completeness token definition in axisConfig.py.

These tests assert the presence of specific structural permit conditions in the zoom definition.
Each test FAILS against the old definition (which uses hollow/deny-list clauses) and PASSES
after the new definition is applied.

Dimensions:
- Dim-A: permit condition replacing hollow 'substantive coverage' clause
- Dim-B: permit condition replacing deny-list 'do not begin at an intermediate level'
- Dim-C: permit condition replacing deny-list 'multiplicative, not additive'
- Dim-D: derivation instruction for self-application
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_zoom_dim_a_substantive_permit_condition():
    """Dim-A: 'substantive coverage' replaced with structural permit condition."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "at least one sentence of content beyond a label or enumeration" in defn


def test_zoom_dim_b_first_bucket_anchor():
    """Dim-B: deny-list 'do not begin at intermediate' replaced with permit condition naming first bucket attachment."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "first bucket section is anchored at the smallest natural unit" in defn


def test_zoom_dim_c_ratio_steps_permit():
    """Dim-C: deny-list 'multiplicative, not additive' replaced with permit condition naming ratio steps."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "bucket sizes are stated as ratios or orders-of-magnitude steps" in defn


def test_zoom_dim_d_derivation_instruction():
    """Dim-D: definition contains self-application derivation instruction."""
    defn = AXIS_KEY_TO_VALUE["completeness"]["zoom"]
    assert "To apply: name the smallest and largest natural units" in defn
