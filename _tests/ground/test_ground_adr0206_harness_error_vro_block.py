def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_harness_error_blocks_impl_gate():
    """impl_gate may not follow a harness-error exec_observed at VRO rung."""
    prompt = get_prompt()
    assert "harness error" in prompt, \
        "Protocol must explicitly state that a harness error at VRO blocks impl_gate"


def test_harness_error_requires_fix_and_rerun():
    """After a harness error, the model must fix the harness and re-run before impl_gate."""
    prompt = get_prompt()
    assert "fix" in prompt and "harness" in prompt and "re-run" in prompt or \
           "fix the harness" in prompt or \
           "repair the harness" in prompt, \
        "Protocol must require fixing the harness and re-running before impl_gate after a harness error"
