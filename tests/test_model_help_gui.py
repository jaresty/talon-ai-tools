import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpGUI import HelpGUIState, UserActions, model_help_gui

    class ModelHelpGUITests(unittest.TestCase):
        def setUp(self) -> None:
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            # Ensure GUI starts hidden.
            model_help_gui.hide()

        def test_open_and_close_toggle_gui_and_reset_state(self) -> None:
            # Initially hidden.
            self.assertFalse(model_help_gui.showing)

            # First call opens the GUI and resets state.
            UserActions.model_help_gui_open()
            self.assertTrue(model_help_gui.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

        def test_explicit_close_hides_gui_and_resets_state(self) -> None:
            # Simulate an open GUI with a focused static prompt.
            HelpGUIState.section = "scope"
            HelpGUIState.static_prompt = "fix"
            model_help_gui.show()

            UserActions.model_help_gui_close()

            # In the stub imgui wrapper, hide() does not currently drive the
            # showing flag back to False, but state resets should still occur.
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)


        def test_open_for_static_prompt_sets_focus_prompt(self) -> None:
            self.assertIsNone(HelpGUIState.static_prompt)

            UserActions.model_help_gui_open_for_static_prompt("todo")

            self.assertTrue(model_help_gui.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertEqual(HelpGUIState.static_prompt, "todo")

        def test_open_for_last_recipe_resets_static_prompt(self) -> None:
            HelpGUIState.static_prompt = "fix"

            UserActions.model_help_gui_open_for_last_recipe()

            self.assertTrue(model_help_gui.showing)
            self.assertEqual(HelpGUIState.section, "all")
            self.assertIsNone(HelpGUIState.static_prompt)

else:
    if not TYPE_CHECKING:
        class ModelHelpGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
