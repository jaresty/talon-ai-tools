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
        HelpCanvasState,
        HelpGUIState,
        UserActions,
        _ensure_canvas,
        register_draw_handler,
        unregister_draw_handler,
        _default_draw_quick_help,
        Rect,
    )
    from talon_user.lib.staticPromptConfig import static_prompt_settings_catalog

    class ModelHelpCanvasTests(unittest.TestCase):
        def setUp(self) -> None:
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            HelpCanvasState.showing = False

        def test_open_and_close_toggle_canvas_and_reset_state(self) -> None:
            # Initially hidden.
            self.assertFalse(HelpCanvasState.showing)

            # First call opens the canvas and resets state.
            UserActions.model_help_canvas_open()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

            # Second call closes and resets.
            UserActions.model_help_canvas_open()
            self.assertFalse(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_explicit_close_hides_canvas_and_resets_state(self) -> None:
            HelpGUIState.section = "scope"
            HelpGUIState.static_prompt = "fix"
            HelpCanvasState.showing = True

            UserActions.model_help_canvas_close()

            self.assertFalse(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_open_for_static_prompt_sets_focus_prompt(self) -> None:
            self.assertIsNone(HelpGUIState.static_prompt)

            UserActions.model_help_canvas_open_for_static_prompt("todo")

            self.assertTrue(HelpGUIState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertEqual(HelpGUIState.static_prompt, "todo")

        def test_open_for_last_recipe_resets_static_prompt(self) -> None:
            HelpGUIState.static_prompt = "fix"

            UserActions.model_help_canvas_open_for_last_recipe()

            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_axis_specific_openers_set_section(self) -> None:
            UserActions.model_help_canvas_open_completeness()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "completeness")
            self.assertIsNone(HelpGUIState.static_prompt)

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_scope()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "scope")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_method()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "method")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_style()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "style")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_directional()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "directional")

            HelpCanvasState.showing = False
            UserActions.model_help_canvas_open_examples()
            self.assertTrue(HelpCanvasState.showing)
            self.assertEqual(HelpGUIState.section, "examples")

        def test_custom_draw_handler_invoked_on_open(self) -> None:
            calls: list[object] = []

            def _handler(c) -> None:
                calls.append(c)

            register_draw_handler(_handler)
            try:
                UserActions.model_help_canvas_open()
                self.assertGreaterEqual(len(calls), 1)
            finally:
                unregister_draw_handler(_handler)

        def test_key_handler_registered_on_canvas(self) -> None:
            canvas_obj = _ensure_canvas()
            # In the test stub, the canvas exposes a `_callbacks` dict; in real
            # Talon this attribute may not exist, so guard accordingly.
            callbacks = getattr(canvas_obj, "_callbacks", None)
            if callbacks is None:
                self.skipTest("Canvas stub does not expose _callbacks")
            self.assertIn("key", callbacks)

        def test_static_prompt_focus_uses_settings_catalog(self) -> None:
            """Quick-help static prompt focus should render settings catalog data."""
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = "todo"

            catalog = static_prompt_settings_catalog()
            entry = catalog.get("todo")
            self.assertIsNotNone(
                entry,
                "Expected 'todo' in static prompt settings catalog",
            )
            description = entry["description"]
            axes = entry["axes"]

            class StubCanvas:
                def __init__(self) -> None:
                    self.rect = Rect(0, 0, 800, 600)
                    self.drawn: list[str] = []

                def draw_text(self, text, x, y) -> None:  # type: ignore[override]
                    self.drawn.append(str(text))

            canvas = StubCanvas()
            _default_draw_quick_help(canvas)

            self.assertIn("Static prompt focus: todo", canvas.drawn)
            if description:
                self.assertIn(description, canvas.drawn)
            if axes:
                self.assertIn("Profile axes:", canvas.drawn)


else:
    if not TYPE_CHECKING:

        class ModelHelpCanvasTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
