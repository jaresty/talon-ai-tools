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
    """Writing non-stub behavior at EV step (2a) must be a protocol violation."""
    prompt = get_prompt()
    assert "stub" in prompt and "protocol violation" in prompt and (
        "non-stub" in prompt or "implementation files at the EV rung" in prompt
    ), \
        "Protocol must state that writing non-stub behavior at EV step (2a) is a protocol violation"
