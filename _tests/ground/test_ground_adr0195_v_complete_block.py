from lib.groundPrompt import build_ground_prompt

def _p(): return build_ground_prompt()

def test_v_complete_blocked_when_p4_step1_absent():
    p = _p()
    # Must explicitly say V-complete may not be emitted if P4 step (1) result absent
    assert (
        "Validation artifact V complete may not be emitted" in p
        or "V complete may not be emitted" in p
    ), "V-complete must be named as blocked (not just a violation) when P4 step (1) absent"
