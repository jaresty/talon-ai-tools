def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_impl_gate_explicitly_forbidden_after_harness_error():
    """Protocol must name impl_gate as forbidden after harness-error exec_observed."""
    prompt = get_prompt()
    assert "may not be emitted after a harness" in prompt or \
           "Implementation gate cleared may not follow a harness" in prompt or \
           "harness error" in prompt and "🟢 Implementation gate cleared may not" in prompt, \
        "Protocol must explicitly name 🟢 Implementation gate cleared as forbidden after harness-error exec_observed"
