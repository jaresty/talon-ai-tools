"""ADR-0187 deletion guards — derivable rules must be absent from the prompt.

Prevents re-introduction of prose that is now derivable from amended P4.
"""
import pytest
from lib.groundPrompt import build_ground_prompt


@pytest.fixture(scope="module")
def prompt():
    return build_ground_prompt()


def test_l31_explicit_gate_phrase_absent(prompt):
    """L31 forward gate phrase must be deleted — derivable from P4 Clause A + EV sequence."""
    assert (
        "if that tool call has not been made in the current response, "
        "the only valid next action is that tool call"
    ) not in prompt


def test_obr_forward_gate_phrase_absent(prompt):
    """OBR forward gate phrase must be deleted — derivable from P4 Clause B ordering + Clause A."""
    assert "if the most recent tool call at this rung is a test runner" not in prompt


def test_rung_entry_gate_phrase_absent(prompt):
    """Rung-entry gate block must be deleted — P1 procedural restatement."""
    assert "Rung-entry gate: before producing content at any rung" not in prompt


def test_criterion_reemission_explicit_prohibition_absent(prompt):
    """OBR criterion re-emission explicit prohibition must be deleted — derivable from P4 Clause B step 1 + Clause A."""
    assert (
        "criterion re-emission is required: emitting the OBR label without immediately"
    ) not in prompt
