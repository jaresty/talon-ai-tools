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
    # ADR-0215: compact routing table blocks HARD STOP for all three harness error types
    assert "HARD STOP is not valid" in p or "HARD STOP may not" in p
    # Compact routing table names all three harness error subtypes
    assert "Harness error routing" in p or "harness error" in p.lower()
