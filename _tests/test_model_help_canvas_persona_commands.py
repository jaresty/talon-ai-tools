import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpCanvas import (
        Rect,
        _default_draw_quick_help,
        HelpGUIState,
    )
    from talon_user.lib.modelState import GPTState

    class _DummyCanvas:
        def __init__(self) -> None:
            self.text: list[str] = []

        def draw_text(self, text: str, x: int, y: int) -> None:
            self.text.append(text)

    class ModelHelpPersonaCommandTests(unittest.TestCase):
        def setUp(self) -> None:
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            GPTState.reset_all()

        def test_persona_block_shows_command_forms(self) -> None:
            canvas = _DummyCanvas()
            _default_draw_quick_help(canvas)

            prefix = "  Persona: "
            persona_lines = [
                line
                for line in canvas.text
                if line.startswith(prefix) or line.startswith(" " * len(prefix))
            ]
            self.assertTrue(persona_lines, "Persona presets line not rendered")
            combined = " ".join(persona_lines)
            self.assertIn("Persona: peer", combined)
            for token in ("mentor", "exec"):
                self.assertIn(token, combined)

        def test_persona_commands_wrap_when_panel_is_narrow(self) -> None:
            rect = Rect(0, 0, 160, 120)
            canvas = _DummyCanvas()
            canvas.rect = rect

            _default_draw_quick_help(canvas)

            prefix = "  Persona: "
            persona_lines = [
                line
                for line in canvas.text
                if line.startswith(prefix) or line.startswith(" " * len(prefix))
            ]
            # With a narrow rect, the persona commands should wrap to multiple lines.
            self.assertGreaterEqual(len(persona_lines), 2)

        def test_persona_commands_cover_catalog_spoken_tokens(self) -> None:
            from talon_user.lib.personaConfig import persona_catalog

            canvas = _DummyCanvas()
            _default_draw_quick_help(canvas)

            prefix = "  Persona: "
            persona_lines = [
                line
                for line in canvas.text
                if line.startswith(prefix) or line.startswith(" " * len(prefix))
            ]
            self.assertTrue(persona_lines, "Persona presets line not rendered")
            combined = " ".join(persona_lines).lower()

            catalog_spoken = {
                (preset.spoken or "").strip().lower()
                for preset in persona_catalog().values()
                if (preset.spoken or "").strip()
            }
            missing = {token for token in catalog_spoken if token not in combined}
            self.assertFalse(
                missing,
                f"Quick help persona block missing spoken presets: {sorted(missing)}",
            )

        def test_intent_presets_align_with_intent_catalog(self) -> None:
            from talon_user.lib.personaConfig import intent_catalog
            from talon_user.lib import modelHelpCanvas as help_module

            catalog = intent_catalog()
            helper_presets = help_module._intent_presets()
            catalog_keys = {preset.key for preset in catalog.values()}
            helper_keys = {preset.key for preset in helper_presets}
            self.assertEqual(
                catalog_keys,
                helper_keys,
                "modelHelpCanvas _intent_presets must cover the same IntentPreset keys as intent_catalog",
            )

else:
    if not TYPE_CHECKING:

        class ModelHelpPersonaCommandTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
