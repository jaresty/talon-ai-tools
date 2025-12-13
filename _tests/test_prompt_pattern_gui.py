import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

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
            PromptAxisPattern,
            PromptPatternGUIState,
            UserActions,
            _run_prompt_pattern,
        )
        from talon_user.lib.modelState import GPTState
        import talon_user.lib.modelPromptPatternGUI as promptPatternGUI

        class PromptPatternGUITests(unittest.TestCase):
            def setUp(self) -> None:
                GPTState.reset_all()
                PromptPatternGUIState.static_prompt = "todo"
                actions.app.notify = MagicMock()
                actions.user.notify = MagicMock()
                actions.user.gpt_apply_prompt = MagicMock()
                actions.user.prompt_pattern_gui_close = MagicMock()

            def test_run_prompt_pattern_executes_and_updates_last_recipe(self) -> None:
                pattern = PROMPT_PRESETS[0]

                _run_prompt_pattern("todo", pattern)

                actions.app.notify.assert_called_once()
                actions.user.gpt_apply_prompt.assert_called_once()
                actions.user.prompt_pattern_gui_close.assert_called_once()
                # last_recipe should reflect the static prompt and axis tokens.
                self.assertEqual(GPTState.last_recipe, "todo · gist · focus · plain · fog")
                self.assertEqual(GPTState.last_static_prompt, "todo")
                self.assertEqual(GPTState.last_completeness, pattern.completeness)
                self.assertEqual(GPTState.last_scope, pattern.scope)
                self.assertEqual(GPTState.last_method, pattern.method)
                self.assertEqual(GPTState.last_form, pattern.form)
                self.assertEqual(GPTState.last_channel, pattern.channel)
                self.assertEqual(GPTState.last_directional, pattern.directional)
                self.assertEqual(
                    GPTState.last_axes.get("directional"),
                    [pattern.directional],
                )

            def test_run_prompt_pattern_applies_axis_caps(self) -> None:
                noisy_pattern = PromptAxisPattern(
                    name="Noisy prompt pattern",
                    description="Test pattern with overlong axes.",
                    completeness="full",
                    scope="actions edges system",
                    method="steps rigor filter plan",
                    form="bullets plain",
                    channel="slack jira",
                    directional="rog fog",
                )

                _run_prompt_pattern("todo", noisy_pattern)

                self.assertEqual(GPTState.last_scope, "edges system")
                self.assertEqual(GPTState.last_method, "filter plan rigor")
                self.assertEqual(GPTState.last_form, "plain")
                self.assertEqual(GPTState.last_channel, "jira")
                self.assertEqual(GPTState.last_directional, "fog")
                self.assertEqual(
                    GPTState.last_recipe,
                    "todo · full · edges system · filter plan rigor · plain · jira · fog",
                )

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

            def test_run_prompt_pattern_surfaces_migration_hint(self) -> None:
                pattern = PROMPT_PRESETS[0]

                def _fake_safe(match):
                    actions.app.notify("GPT: style axis is removed")
                    return ""

                with patch.object(promptPatternGUI, "safe_model_prompt", side_effect=_fake_safe):
                    _run_prompt_pattern("todo", pattern)

                actions.user.gpt_apply_prompt.assert_not_called()
                notes = [
                    str(args[0])
                    for args in [
                        *(ca.args for ca in actions.app.notify.call_args_list),
                        *(ca.args for ca in actions.user.notify.call_args_list),
                    ]
                    if args
                ]
                self.assertTrue(
                    any("style axis is removed" in n or "styleModifier is no longer supported" in n for n in notes),
                    f"Expected migration hint notification, got {notes}",
                )

    except ImportError:
        # When Talon loads this test but the underlying GUI module is not
        # importable, provide a skipped placeholder so Talon does not log an
        # import error.
        if not TYPE_CHECKING:

            class PromptPatternGUITests(unittest.TestCase):
                @unittest.skip(
                    "modelPromptPatternGUI unavailable in this Talon runtime"
                )
                def test_placeholder(self) -> None:
                    pass

else:
    if not TYPE_CHECKING:

        class PromptPatternGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
