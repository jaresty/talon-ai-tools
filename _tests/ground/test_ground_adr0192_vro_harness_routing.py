"""Thread 1: VRO harness error caused by missing impl file must route to EI."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_vro_missing_impl_file_routes_to_ei():
    p = _p()
    # The rule must name EI (implementation rung) as the destination when VRO
    # harness fails due to a missing implementation file
    assert (
        "missing implementation file" in p
        or ("harness error at" in p and "VRO" in p and "EI" in p)
        or ("harness error" in p and "missing" in p and "implementation" in p)
    )

def test_hard_stop_blocked_at_vro_for_harness_error():
    p = _p()
    # Must explicitly block HARD STOP at VRO for harness errors (not just at EV)
    assert "HARD STOP may not" in p
    # Specifically at VRO context -- check there's a VRO-specific harness rule
    idx_vro_harness = p.find("harness error at the VRO")
    idx_vro_harness2 = p.find("harness error at VRO")
    assert idx_vro_harness != -1 or idx_vro_harness2 != -1, \
        "No VRO-specific harness error rule found"
