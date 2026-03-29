def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_ei_test_modification_forbidden_without_meta_test():
    """Modifying a test file at EI is a protocol violation unless meta-test pattern is in effect."""
    prompt = get_prompt()
    assert (
        "modifying a test file at the EI rung" in prompt or
        "writing to a test file at EI" in prompt or
        "test file at the EI rung is a protocol violation" in prompt or
        "test file at EI is a protocol violation" in prompt
    ), \
        "Protocol must explicitly state that modifying a test file at EI is a protocol violation"


def test_ei_only_permits_implementation_writes():
    """EI rung must only permit implementation file-writes."""
    prompt = get_prompt()
    assert "implementation file-writes only" in prompt, \
        "Protocol must state EI rung allows implementation file-writes only"
