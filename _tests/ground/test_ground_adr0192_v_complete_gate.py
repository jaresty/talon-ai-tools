"""Thread 2: V-complete gate requires pre-existence check tool call."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_v_complete_requires_pre_existence_tool_call():
    p = _p()
    # Must state explicitly: before V-complete, pre-existence check tool call is required
    assert (
        "before emitting" in p
        and "Validation artifact V complete" in p
        and "pre-exist" in p
        and "tool" in p
    ) or "V complete" in p and "does not pre-exist" in p

def test_v_complete_gate_not_file_write_alone():
    p = _p()
    # A file-write alone (without a pre-existence check result) must not satisfy the gate
    # Find the occurrence in the EV rules section (the one with "before emitting")
    idx = p.find("before emitting \u2705 Validation artifact V complete")
    assert idx != -1
    # Check there's a rule near that sentence about pre-existence check
    window = p[max(0, idx-200):idx+500]
    assert "pre-exist" in window or "does not pre-exist" in window, \
        "No pre-existence rule found near V-complete sentinel rule"
