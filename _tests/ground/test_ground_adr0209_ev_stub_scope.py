def get_prompt():
    from lib.groundPrompt import build_ground_prompt
    return build_ground_prompt()


def test_stub_scope_bound_to_import_statement():
    """Stub must contain only names referenced in the test's import statement."""
    prompt = get_prompt()
    assert "import statement" in prompt and "stub" in prompt and (
        "only" in prompt or "exactly" in prompt or "beyond" in prompt
    ), \
        "Protocol must bound stub content to what the test's import statement requires"


def test_stub_extra_exports_forbidden():
    """Stub must not contain exports beyond what the import requires."""
    prompt = get_prompt()
    assert "stub" in prompt and (
        "beyond what the import" in prompt or
        "not required by the import" in prompt or
        "import statement requires" in prompt
    ), \
        "Protocol must forbid exports in the stub beyond what the import statement requires"
