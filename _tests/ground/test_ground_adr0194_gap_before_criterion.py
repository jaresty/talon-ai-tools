from lib.groundPrompt import build_ground_prompt

def _p(): return build_ground_prompt()

def test_gap_first_at_criteria_rung():
    p = _p()
    # Must state criteria-rung-specific ordering: Gap is first content after label
    assert (
        "must be the first content after the criteria rung label" in p
        or "criteria rung label" in p and "Gap:" in p and "criterion sentence" in p
        or "after the criteria rung label, the first content must be" in p
    )

def test_criterion_before_gap_explicitly_prohibited():
    p = _p()
    # Must explicitly say criterion before Gap is a violation (not just in the generic rule)
    assert (
        "criterion" in p and "before" in p and ("Gap" in p) and "criteria rung" in p
        and ("violation" in p or "prohibited" in p or "may not precede" in p)
    ) or "criterion sentence may not precede" in p
