from lib.sequenceConfig import SEQUENCES


def test_context_to_interactive_exists():
    assert "context-to-interactive" in SEQUENCES


def test_context_to_interactive_mode():
    assert SEQUENCES["context-to-interactive"]["mode"] == "autonomous"


def test_context_to_interactive_steps():
    assert len(SEQUENCES["context-to-interactive"]["steps"]) == 3


def test_context_to_interactive_step_tokens():
    steps = SEQUENCES["context-to-interactive"]["steps"]
    assert steps[0]["token"] == "probe contextualise"
    assert steps[1]["token"] == "sim mint"
    assert steps[2]["token"] == "make form:interactive"
