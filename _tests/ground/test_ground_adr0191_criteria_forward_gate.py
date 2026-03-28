"""Test: standalone criteria→formal-notation forward gate."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_criteria_to_fn_forward_gate_standalone():
    p = _p()
    # The forward gate must be present as a standalone sentence
    assert "after the criterion is written, the only valid next token is the formal notation rung label" in p

def test_criteria_forward_gate_not_only_in_second_criterion_sentence():
    p = _p()
    # Must appear independently, not only embedded in "exactly one criterion may be written"
    idx_standalone = p.find("after the criterion is written, the only valid next token is the formal notation rung label")
    idx_second = p.find("exactly one criterion may be written per thread per cycle")
    assert idx_standalone != -1
    # The standalone gate must appear before the second-criterion rule
    assert idx_standalone < idx_second
