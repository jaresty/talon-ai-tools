def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_impl_gate_explicitly_forbidden_after_harness_error():
    """Protocol must name impl_gate as blocked after harness-error (ADR-0215: compact routing table)."""
    prompt = get_prompt()
    # ADR-0215: compact routing table blocks 🟢 Implementation gate cleared for all harness error types
    assert (
        ("Harness error routing" in prompt and "\U0001f7e2 Implementation gate cleared" in prompt)
        or "may not be emitted after a harness" in prompt
        or "\U0001f7e2 Implementation gate cleared may not" in prompt
    ), "Protocol must block 🟢 Implementation gate cleared after harness-error exec_observed"
