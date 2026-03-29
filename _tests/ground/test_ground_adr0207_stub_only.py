def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_stub_forbids_conditional_logic():
    """Stub at EV step (2a) must not contain conditional logic."""
    prompt = get_prompt()
    assert "stub" in prompt and (
        "no conditional logic" in prompt or
        "conditional logic" in prompt and "forbidden" in prompt or
        "no logic" in prompt
    ), \
        "Protocol must specify that a stub contains no conditional logic"


def test_stub_forbids_non_empty_function_bodies():
    """Stub at EV step (2a) must not contain non-empty function bodies."""
    prompt = get_prompt()
    assert "stub" in prompt and (
        "no non-empty" in prompt or
        "empty" in prompt and "bod" in prompt
    ), \
        "Protocol must specify that a stub contains no non-empty function bodies"


def test_non_stub_behavior_at_ev_is_violation():
    """Writing non-stub behavior at EV step (2a) must be a protocol violation.
    ADR-0214: 'writing implementation files at the EV rung is a protocol violation' removed as
    derivable from EV closed action set. Presence of stub constraints + 'advancing to (2b)' gate
    is sufficient to close this escape route via type discipline.
    """
    prompt = get_prompt()
    assert "stub" in prompt and "protocol violation" in prompt and (
        "non-stub" in prompt
        or "implementation files at the EV rung" in prompt
        or ("EV rung" in prompt and "stub" in prompt and "advancing to (2b)" in prompt)
    ), \
        "Protocol must state that writing non-stub behavior at EV step (2a) is a protocol violation"
