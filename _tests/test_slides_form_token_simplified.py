"""Falsifiable tests for the simplified slides form token definition.

Each test must FAIL before axisConfig.py is updated and PASS after.
The simplified definition removes the procedural counting gate, 4-line
body cap, and heading requirement — keeping only the sequence-of-discrete-
units constraint with unrestricted content type and medium.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def _slides() -> str:
    return AXIS_KEY_TO_VALUE["form"]["slides"]


def test_slides_describes_discrete_units():
    """slides definition must describe the form as discrete units."""
    text = _slides()
    assert "discrete" in text or "self-contained" in text, (
        "slides must describe units as discrete or self-contained — "
        "this is the sole structural constraint after simplification"
    )


def test_slides_does_not_require_heading():
    """slides definition must not require a heading line for each unit."""
    text = _slides()
    assert "heading line" not in text, (
        "slides must not require a heading line — "
        "headings are not strictly needed for every slide"
    )


def test_slides_does_not_require_body_line_count():
    """slides definition must not impose a line count on slide bodies."""
    text = _slides()
    assert "four lines" not in text and "4 lines" not in text, (
        "slides must not cap body at four lines — content type is unrestricted"
    )


def test_slides_does_not_have_counting_gate():
    """slides definition must not require pre-emission counting or confirmation."""
    text = _slides()
    assert "count the planned" not in text, (
        "slides must not include procedural counting gate — "
        "the pre-emission count/confirm clause has been removed"
    )


def test_slides_permits_any_content_type():
    """slides definition must not restrict content to text."""
    text = _slides()
    assert "rendering format is permitted" in text or "content type" in text or "medium" in text, (
        "slides must explicitly permit any rendering format or content type — "
        "slides can be diagrams, images, or any other medium"
    )
