"""Test: standalone criteria→formal-notation forward gate."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_criteria_to_fn_forward_gate_prose_absent():
    # ADR-0215: A2 type-context restatement at criteria rung removed (derivable from gate formula)
    p = _p()
    assert "after the criterion is written, the only valid next token is the formal notation rung label" not in p

def test_criteria_content_type_prose_absent():
    # ADR-0215: "each rung label opens a content-type context" prose removed (A2 restatement)
    p = _p()
    assert "each rung label opens a content-type context" not in p
