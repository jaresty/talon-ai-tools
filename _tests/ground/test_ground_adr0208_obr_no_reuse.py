def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_obr_tool_call_must_be_at_obr_rung():
    """OBR exec_observed must come from a tool call made at the OBR rung, not reused from earlier."""
    prompt = get_prompt()
    assert "reused" in prompt or "may not be reused" in prompt or \
           "output produced before the OBR" in prompt, \
        "Protocol must forbid reusing output produced before the OBR rung label"
