import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    try:
        from talon_user.lib.stanceValidation import valid_stance_command

        class SuggestionStanceValidationTests(unittest.TestCase):
            def test_accepts_model_write_with_full_persona_intent(self) -> None:
                self.assertTrue(
                    valid_stance_command(
                        "model write as teacher to junior engineer kindly for teaching"
                    )
                )

            def test_rejects_bare_model_write_and_model_write_for(self) -> None:
                self.assertFalse(valid_stance_command("model write"))
                self.assertFalse(valid_stance_command("model write for"))

            def test_accepts_persona_and_intent_presets(self) -> None:
                # These presets are defined in personaConfig.PERSONA_PRESETS / INTENT_PRESETS
                self.assertTrue(valid_stance_command("persona teach junior dev"))
                self.assertTrue(valid_stance_command("intent teach"))

            def test_accepts_combined_persona_and_intent(self) -> None:
                self.assertTrue(
                    valid_stance_command("persona teach junior dev · intent teach")
                )

            def test_rejects_axis_tokens_after_persona_or_intent(self) -> None:
                # Raw axis tokens after persona/intent are not valid preset names.
                self.assertFalse(
                    valid_stance_command(
                        "persona as facilitator to stakeholders gently"
                    )
                )
                self.assertFalse(valid_stance_command("intent for collaborating"))

    except ImportError:
        # When Talon loads this test but the underlying validator module is not
        # importable, provide a skipped placeholder so Talon does not log an
        # import error.
        if not TYPE_CHECKING:

            class SuggestionStanceValidationTests(unittest.TestCase):  # type: ignore[no-redef]
                @unittest.skip("stanceValidation not importable in this environment")
                def test_placeholder(self) -> None:
                    pass
