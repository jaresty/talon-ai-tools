"""ADR-0187 behavioral anchors — sequence-binding extension to P4.

Tests assert behavioral effects on the generated prompt string,
not literal phrase pins.
"""
import pytest
from lib.groundPrompt import build_ground_prompt


@pytest.fixture(scope="module")
def prompt():
    return build_ground_prompt()


# Thread 1: p4-clause-a — sequence-binding clause in P4
def test_p4_sequence_binding_clause_present(prompt):
    """P4 must contain a clause binding the enumerated sequence for completion."""
    assert "sequence enumerated for a rung is binding for completion" in prompt


def test_p4_no_completion_sentinel_before_full_sequence(prompt):
    """P4 clause must state no completion sentinel may precede the full sequence."""
    assert "no completion sentinel" in prompt
    assert "full sequence" in prompt
    assert "in order" in prompt


def test_p4_no_content_between_steps(prompt):
    """P4 clause must state no other content may appear between steps."""
    assert "no content other than the next step" in prompt


# Thread 2: p4-obr-sequence — OBR action list in P4
def test_p4_obr_has_criterion_reemission_step(prompt):
    """OBR action list must name criterion re-emission as a step."""
    assert "criterion re-emission" in prompt


def test_p4_obr_has_provenance_statement_step(prompt):
    """OBR action list must name provenance statement as a step."""
    assert "provenance statement" in prompt


def test_p4_obr_has_live_process_invocation_step(prompt):
    """OBR action list must name live-process invocation as a step."""
    assert "live-process invocation" in prompt


def test_p4_obr_has_test_suite_step_after_live_process(prompt):
    """OBR action list must name test suite run as a step, after live-process."""
    lp_pos = prompt.find("live-process invocation")
    ts_pos = prompt.find("test suite run")
    assert lp_pos != -1, "live-process invocation not found"
    assert ts_pos != -1, "test suite run not found"
    assert lp_pos < ts_pos, "test suite run must appear after live-process invocation"


# Thread 3: rung-table-obr-artifact — rung table OBR artifact type
def test_rung_table_obr_artifact_directly_demonstrates(prompt):
    """OBR rung table artifact type must reference 'directly demonstrates'."""
    assert "directly demonstrating all criteria" in prompt


# Thread 4: deletions — derivable rules removed
# (Deletion guards are in test_ground_adr0187_deletions.py)

# Thread 5: test suite passes — covered by running the suite itself
