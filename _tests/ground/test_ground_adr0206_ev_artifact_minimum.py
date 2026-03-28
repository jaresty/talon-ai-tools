def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_ev_artifact_minimum_test_blocks_required():
    """V-complete gate requires each test block (name + body) to appear in transcript."""
    prompt = get_prompt()
    assert "test block" in prompt or "assertion body" in prompt or \
           "each it(" in prompt or "each test(" in prompt or \
           "test case bod" in prompt, \
        "EV artifact gate must specify that test case bodies (name + assertion) must appear in transcript before V-complete"


def test_ev_artifact_full_file_not_required():
    """Boilerplate (imports, describe wrappers) must not be required for V-complete."""
    prompt = get_prompt()
    assert "import statements are not required" in prompt or \
           "boilerplate" in prompt or \
           "describe wrapper" in prompt or \
           "test block" in prompt, \
        "EV artifact gate must clarify that full file content is not required — only test blocks"
