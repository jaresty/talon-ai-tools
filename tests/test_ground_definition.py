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


# Gate string tests — each FAILS against old definition, PASSES after new definition is implemented.

def test_ground_gate_D2_nonsoft_heading():
    """D2: non-software §0 must use a literal '## ' heading or it does not satisfy §0."""
    assert "an observation not under such a heading does not satisfy §0" in _ground_def()


def test_ground_gate_D3_goal_before_tool_result():
    """D3: governing goal line before any tool-result block above it does not satisfy §1."""
    assert "a '## Governing goal:' line appearing before any tool-result block above it does not satisfy §1" in _ground_def()


def test_ground_gate_D4_dimensions_ordering():
    """D4: behavioral dimensions heading must not appear before governing goal appears in transcript."""
    assert "this heading must not appear before '## Governing goal:' appears in the transcript" in _ground_def()


def test_ground_gate_G1_enforcement_before_edit():
    """G1: enforcement sequence heading must appear before first file-modifying tool call regardless of § implementation permitted."""
    assert "this heading must appear in the transcript before the first file-modifying tool call regardless of whether" in _ground_def()


def test_ground_gate_G2_completion_ordering():
    """G2: completion check heading must not appear before enforcement sequence in transcript."""
    assert "this heading must not appear before '## Enforcement sequence' in the transcript" in _ground_def()


def test_ground_gate_C2_done_without_completion():
    """C2: done declaration before completion check does not satisfy ground."""
    assert "a done declaration appearing before '## Completion check' does not satisfy ground" in _ground_def()


def test_ground_gate_CL2_completion_check_tool_result():
    """CL2: dimension declared covered without tool-result substring does not satisfy §4."""
    assert "a dimension declared covered without such a substring does not satisfy §4" in _ground_def()


# §1 means-test clause tests — each FAILS against old definition, PASSES after new §1 is implemented.

def test_ground_gate_S1_means_test_sentence_form():
    """S1: §1 requires means-test sentence form immediately below heading."""
    assert "The goal [text] could be achieved by:" in _ground_def()


def test_ground_gate_S1_hypothetical_fallback():
    """S1: §1 requires [hypothetical] fallback when no concrete alternative can be named."""
    assert "[hypothetical]" in _ground_def()


def test_ground_gate_S1_behavioral_dimensions_gate():
    """S1: ## Behavioral dimensions heading appearing without means-test sentence above it does not satisfy §1."""
    assert "a '## Behavioral dimensions' heading appearing without this sentence above it does not satisfy §1" in _ground_def()


def test_ground_gate_S1_selection_criterion_revised():
    """S1: tie-breaking criterion replaced — now selects goal whose means-test names more concrete alternative."""
    assert "more concrete alternative than those listed in §0" in _ground_def()


# §2 observable-field clause tests — each FAILS against old definition, PASSES after new §2 is implemented.

def test_ground_gate_S2_observable_field_tag():
    """S2: each dimension must end with [observable: <string>] tag."""
    assert "[observable:" in _ground_def()


def test_ground_gate_S2_observable_prose_path():
    """S2: [observable: prose] is the correct tag when no tool-result blocks appear above §2."""
    assert "[observable: prose]" in _ground_def()


def test_ground_gate_S2_enforcement_sequence_gate():
    """S2: ## Enforcement sequence heading must not appear before every dimension has [observable:] tag."""
    assert "a '## Enforcement sequence' heading appearing before every dimension carries an '[observable:]' tag does not satisfy §2" in _ground_def()


def test_ground_gate_S2_reader_uncertainty_replaces_implied():
    """S2: 'directly implied' replaced with reader-uncertainty test."""
    assert "still uncertain whether" in _ground_def()
