from talon_user.lib.staticPromptConfig import (
    STATIC_PROMPT_CONFIG,
    static_prompt_description_overrides,
)


def test_static_prompt_description_overrides_matches_config_descriptions() -> None:
    overrides = static_prompt_description_overrides()

    assert isinstance(overrides, dict)

    for name, profile in STATIC_PROMPT_CONFIG.items():
        description = str(profile.get("description", "")).strip()
        if description:
            # Prompts with a non-empty description should appear in overrides.
            assert name in overrides
            assert overrides[name] == description
        else:
            # Prompts without a description should not appear in overrides.
            assert name not in overrides
