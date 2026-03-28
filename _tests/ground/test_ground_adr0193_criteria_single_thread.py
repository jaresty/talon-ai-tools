"""Thread 1: criteria rung artifact is for exactly ONE thread (not one-per-thread)."""
from lib.groundPrompt import build_ground_prompt

def _p():
    return build_ground_prompt()

def test_criteria_artifact_for_current_thread_only():
    p = _p()
    # The artifact definition must say the criteria rung produces ONE criterion for
    # the CURRENT thread — not "one per thread". The "per thread per cycle" phrasing
    # is ambiguous and allows batch-collecting.
    assert (
        "criteria rung artifact" in p
        or ("criteria rung" in p and "current thread only" in p)
        or ("criteria rung" in p and "exactly one thread" in p)
        or "one criterion for the current thread" in p
    ), "No positive definition of criteria rung artifact as single-thread artifact"

def test_criteria_per_thread_phrasing_unambiguous():
    p = _p()
    # "exactly one criterion may be written per thread per cycle" allows the
    # interpretation "one per each thread". Must clarify this means one for the
    # current thread, not one for each thread.
    # Check for a disambiguation like "current thread" near "exactly one criterion"
    idx = p.find("exactly one criterion may be written")
    assert idx != -1
    window = p[max(0,idx-200):idx+400]
    assert "current thread" in window, \
        "No disambiguation: 'per thread per cycle' is ambiguous — must say 'current thread'"
