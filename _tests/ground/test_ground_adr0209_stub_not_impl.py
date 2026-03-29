def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_stub_must_be_overwritten_at_impl_rung():
    """Implementation rung must overwrite the stub with real behavior."""
    prompt = get_prompt()
    assert "stub" in prompt and (
        "overwrite" in prompt or
        "replace" in prompt or
        "not the implementation" in prompt or
        "stub is not" in prompt
    ), \
        "Protocol must require the implementation rung to overwrite the stub with real behavior"


def test_leaving_stub_as_implementation_is_violation():
    """Leaving the stub as the final implementation must be a protocol violation."""
    prompt = get_prompt()
    assert "stub" in prompt and "protocol violation" in prompt and (
        "leaving" in prompt or
        "not the implementation" in prompt or
        "stub as" in prompt
    ), \
        "Protocol must state that leaving the stub as implementation is a protocol violation"
