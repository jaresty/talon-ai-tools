def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_thread_complete_hard_block_no_reasoning_override():
    """No reasoning or inference may override the Thread N complete block."""
    prompt = get_prompt()
    assert (
        "no reasoning" in prompt or
        "no intervening prose, reasoning" in prompt or
        "reasoning" in prompt and "lifts this block" in prompt
    ), \
        "Protocol must state that no reasoning overrides the Thread N complete block"


def test_thread_complete_blocked_without_live_process():
    """Thread N complete is blocked without a live-process result in current cycle."""
    prompt = get_prompt()
    assert (
        "most recent" in prompt and "test failure" in prompt
    ) or (
        "blocked" in prompt and "live-process" in prompt
    ), \
        "Protocol must explicitly block Thread N complete without live-process evidence"
