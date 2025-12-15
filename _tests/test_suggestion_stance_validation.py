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
            def test_accepts_model_write_with_persona_axes(self) -> None:
                self.assertTrue(
                    valid_stance_command("model write as teacher to junior engineer kindly")
                )

            def test_rejects_bare_model_write_and_model_write_for(self) -> None:
                self.assertFalse(valid_stance_command("model write"))
                self.assertFalse(valid_stance_command("model write for"))
                self.assertFalse(valid_stance_command("model write plan"))
                self.assertFalse(valid_stance_command("model write for teaching"))

            def test_accepts_persona_presets_and_rejects_intent_presets(self) -> None:
                # Persona presets are valid stance commands; intent is a separate command.
                self.assertTrue(valid_stance_command("persona teach junior dev"))
                self.assertFalse(valid_stance_command("intent teach"))
                self.assertFalse(valid_stance_command("persona teach junior dev · intent teach"))

            def test_accepts_persona_preset_spoken_shorthand(self) -> None:
                self.assertTrue(valid_stance_command("persona stake"))

            def test_rejects_axis_tokens_after_persona_or_intent(self) -> None:
                # Raw axis tokens after persona/intent are not valid preset names.
                self.assertFalse(
                    valid_stance_command(
                        "persona as facilitator to stakeholders gently"
                    )
                )
                self.assertFalse(valid_stance_command("intent for collaborating"))

            def test_rejects_model_write_with_unknown_tail_words(self) -> None:
                # Unknown words that are not part of any axis token should cause
                # model write stances to be rejected even if they contain
                # something that looks like a intent.
                self.assertFalse(
                    valid_stance_command(
                        "model write as teacher to junior engineer kindly for teaching quickly"
                    )
                )

    except ImportError:
        # When Talon loads this test but the underlying validator module is not
        # importable, provide a skipped placeholder so Talon does not log an
        # import error.
        if not TYPE_CHECKING:

            class SuggestionStanceValidationTests(unittest.TestCase):  # type: ignore[no-redef]
                @unittest.skip("stanceValidation not importable in this environment")
                def test_placeholder(self) -> None:
                    pass
