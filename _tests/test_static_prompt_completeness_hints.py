import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - handled by bootstrap guard below
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE
    from talon_user.lib.staticPromptConfig import (
        STATIC_PROMPT_CONFIG,
        completeness_freeform_allowlist,
    )

    class StaticPromptCompletenessHintTests(unittest.TestCase):
        def test_completeness_hints_are_axis_tokens_or_allowed_free_form(self) -> None:
            axis_tokens = set(AXIS_KEY_TO_VALUE.get("completeness", {}).keys())
            allowed_free_form = completeness_freeform_allowlist()
            self.assertTrue(allowed_free_form)

            unexpected: list[tuple[str, str]] = []
            for name, profile in STATIC_PROMPT_CONFIG.items():
                completeness = (profile.get("completeness") or "").strip()
                if not completeness:
                    continue
                if completeness in axis_tokens:
                    continue
                if completeness in allowed_free_form:
                    continue
                unexpected.append((name, completeness))

            self.assertFalse(
                unexpected,
                f"Unexpected completeness hints outside axis tokens/allowed free-form: {unexpected}",
            )
