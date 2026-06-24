from lib.sequenceConfig import SEQUENCES


def test_context_to_interactive_guided_exists():
    assert "context-to-interactive-guided" in SEQUENCES


def test_context_to_interactive_guided_mode():
    assert SEQUENCES["context-to-interactive-guided"]["mode"] == "linear"


def test_context_to_interactive_guided_steps():
    assert len(SEQUENCES["context-to-interactive-guided"]["steps"]) == 3


def test_context_to_interactive_guided_step_tokens():
    steps = SEQUENCES["context-to-interactive-guided"]["steps"]
    assert steps[0]["token"] == "probe contextualise"
    assert steps[1]["token"] == "sim mint"
    assert steps[2]["token"] == "make form:interactive"


def test_context_to_interactive_guided_pause():
    steps = SEQUENCES["context-to-interactive-guided"]["steps"]
    assert steps[0].get("requires_user_input") is True
