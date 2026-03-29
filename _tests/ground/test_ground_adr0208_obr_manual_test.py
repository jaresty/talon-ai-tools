def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_obr_requires_manual_test():
    """OBR rung must require a manual test — a live-process invocation."""
    prompt = get_prompt()
    assert "manual" in prompt, \
        "OBR rung must name the required artifact as a manual test"


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
