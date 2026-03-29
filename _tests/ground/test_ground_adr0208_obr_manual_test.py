def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_obr_requires_manual_test():
    """OBR rung must require a live-process invocation (ADR-0215: 'manual' removed, 'live-process' retained)."""
    prompt = get_prompt()
    assert "live-process invocation" in prompt, \
        "OBR rung must require a live-process invocation"


def test_obr_browser_test_runner_forbidden():
    """Browser-mode test runners must not satisfy the OBR rung."""
    prompt = get_prompt()
    assert "browser" in prompt and (
        "test runner" in prompt or "automated" in prompt
    ), \
        "OBR rung must explicitly forbid browser-mode test runners"


def test_obr_automated_test_does_not_satisfy():
    """Automated test runner output must not satisfy OBR regardless of framework."""
    prompt = get_prompt()
    assert "automated" in prompt or (
        "test runner" in prompt and "not" in prompt
    ), \
        "OBR rung must state that automated test runner output does not satisfy it"
