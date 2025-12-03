import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    try:
        from talon import actions
        from talon_user.lib.modelPromptPatternGUI import (
            PROMPT_PRESETS,
            PromptPatternGUIState,
            UserActions,
            _run_prompt_pattern,
        )
        from talon_user.lib.modelState import GPTState

        class PromptPatternGUITests(unittest.TestCase):
            def setUp(self) -> None:
                GPTState.reset_all()
                PromptPatternGUIState.static_prompt = "todo"
                actions.app.notify = MagicMock()
                actions.user.gpt_apply_prompt = MagicMock()
                actions.user.prompt_pattern_gui_close = MagicMock()

            def test_run_prompt_pattern_executes_and_updates_last_recipe(self) -> None:
                pattern = PROMPT_PRESETS[0]

                _run_prompt_pattern("todo", pattern)

                actions.app.notify.assert_called_once()
                actions.user.gpt_apply_prompt.assert_called_once()
                actions.user.prompt_pattern_gui_close.assert_called_once()
                # last_recipe should reflect the static prompt and axis tokens.
                self.assertEqual(
                    GPTState.last_recipe,
                    "todo · gist · focus · plain",
                )
                self.assertEqual(GPTState.last_static_prompt, "todo")
                self.assertEqual(GPTState.last_completeness, pattern.completeness)
                self.assertEqual(GPTState.last_scope, pattern.scope)
                self.assertEqual(GPTState.last_method, pattern.method)
                self.assertEqual(GPTState.last_style, pattern.style)
                self.assertEqual(GPTState.last_directional, pattern.directional)

            def test_prompt_pattern_run_preset_dispatches_by_name(self) -> None:
                # Ensure the action locates the preset by name and delegates to
                # _run_prompt_pattern with the current static prompt.
                target_preset = PROMPT_PRESETS[1]
                PromptPatternGUIState.static_prompt = "fix"
                # Spy on _run_prompt_pattern via a simple wrapper.
                original = _run_prompt_pattern
                called = {}

                def wrapper(static_prompt: str, pattern):
                    called["args"] = (static_prompt, pattern)
                    return original(static_prompt, pattern)

                try:
                    # Monkey-patch in module namespace.
                    import talon_user.lib.modelPromptPatternGUI as gui_mod

                    gui_mod._run_prompt_pattern = wrapper  # type: ignore[assignment]

                    UserActions.prompt_pattern_run_preset(target_preset.name)
                finally:
                    gui_mod._run_prompt_pattern = original  # type: ignore[assignment]

                self.assertIn("args", called)
                static_prompt_arg, pattern_arg = called["args"]
                self.assertEqual(static_prompt_arg, "fix")
                self.assertEqual(pattern_arg.name, target_preset.name)

    except ImportError:
        # When Talon loads this test but the underlying GUI module is not
        # importable, provide a skipped placeholder so Talon does not log an
        # import error.
        if not TYPE_CHECKING:
            class PromptPatternGUITests(unittest.TestCase):
                @unittest.skip("modelPromptPatternGUI unavailable in this Talon runtime")
                def test_placeholder(self) -> None:
                    pass

else:
    if not TYPE_CHECKING:
        class PromptPatternGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
