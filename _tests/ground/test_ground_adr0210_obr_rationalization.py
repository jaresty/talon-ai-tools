def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_passing_tests_do_not_satisfy_obr():
    """Passing tests must be named as insufficient to satisfy the OBR gate."""
    prompt = get_prompt()
    assert "passing tests" in prompt or \
           "all tests pass" in prompt or \
           "tests passing" in prompt, \
        "Protocol must explicitly name passing tests as insufficient to satisfy the OBR gate"


def test_functional_completeness_does_not_satisfy_obr():
    """Functional completeness must not substitute for OBR live-process invocation."""
    prompt = get_prompt()
    assert "functionally complete" in prompt or "appears complete" in prompt, \
        "Protocol must name functional completeness as an insufficient reason to skip OBR"


def test_prior_precedent_does_not_satisfy_obr():
    """Prior work stopping at EI must not justify skipping OBR."""
    prompt = get_prompt()
    assert "prior work" in prompt or "stopped at EI" in prompt or \
           "prior cycles stopped" in prompt or "precedent" in prompt, \
        "Protocol must name prior precedent (prior work stopping at EI) as insufficient to skip OBR"
