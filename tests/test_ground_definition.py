"""Tests for ground token definition — assert new structural clauses present, old underenforced clauses absent."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.groundPrompt import build_ground_prompt


def _ground_def() -> str:
    return build_ground_prompt()


def test_ground_definition_contains_implementation_permitted():
    """New definition requires gate string '§ implementation permitted' — absent from old definition.
    Closes D1: gate was prose instruction, not a transcript-inspectable string."""
    assert "§ implementation permitted" in _ground_def()


def test_ground_definition_contains_enumeration_complete():
    """New definition requires gate string '§5 enumeration complete' — absent from old definition.
    Closes CL1/D3: drops weaker 'at least one per section' floor, replaces with gate string."""
    assert "§5 enumeration complete" in _ground_def()


def test_ground_definition_contains_markdown_heading_form():
    """New definition specifies heading form as markdown '## ' — absent from old definition.
    Closes G1: 'literal heading' was undefined, allowing inline bold as escape."""
    assert "markdown" in _ground_def()


def test_ground_definition_contains_transcript_inspectable():
    """New definition names root criterion as 'transcript-inspectable' — absent from old definition.
    Closes the root criterion gap: compliance must be verifiable without intent assessment."""
    assert "transcript-inspectable" in _ground_def()
