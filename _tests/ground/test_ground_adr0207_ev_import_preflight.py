def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_ev_import_preflight_required():
    """EV rung must require writing and running import block before assertion bodies."""
    prompt = get_prompt()
    assert "import block" in prompt or "import check" in prompt, \
        "EV rung must require writing the import block first and confirming it loads"


def test_ev_assertions_blocked_until_imports_load():
    """Assertion bodies must not be written until import check passes."""
    prompt = get_prompt()
    assert ("assertion" in prompt or "assertion bodies" in prompt) and (
        "import" in prompt
    ) and (
        "before" in prompt or "until" in prompt or "first" in prompt
    ), \
        "EV rung must block assertion bodies until imports are confirmed to load"
