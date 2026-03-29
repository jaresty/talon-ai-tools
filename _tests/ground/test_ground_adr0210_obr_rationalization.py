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
    # ADR-0215: compressed to why-sentence; "complete implementation" replaces "functionally complete"
    prompt = get_prompt()
    assert "complete implementation" in prompt or "functionally complete" in prompt or "appears complete" in prompt, \
        "Protocol must name complete implementation as insufficient to satisfy the OBR gate"


def test_prior_precedent_does_not_satisfy_obr():
    """Prior cycles must not justify skipping OBR."""
    # ADR-0215: compressed to why-sentence; "prior cycles" replaces "prior work stopped at EI, or precedent"
    prompt = get_prompt()
    assert "prior cycles" in prompt or "prior work" in prompt or "precedent" in prompt, \
        "Protocol must name prior cycles as insufficient to satisfy the OBR gate"
