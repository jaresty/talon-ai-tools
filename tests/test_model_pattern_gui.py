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
        from pathlib import Path

        from talon import actions
        from talon_user.lib.modelPatternGUI import (
            PATTERNS,
            PatternGUIState,
            UserActions,
            _axis_value,
            _parse_recipe,
        )
        from talon_user.lib.modelState import GPTState
        from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG

        class ModelPatternGUITests(unittest.TestCase):
            def setUp(self) -> None:
                GPTState.reset_all()
                PatternGUIState.domain = None
                actions.app.notify = MagicMock()
                actions.user.gpt_apply_prompt = MagicMock()
                actions.user.model_pattern_gui_close = MagicMock()

            def test_axis_value_returns_description_when_present(self) -> None:
                mapping = {"gist": "Important: Provide a short but complete answer."}
                self.assertEqual(
                    _axis_value("gist", mapping),
                    "Important: Provide a short but complete answer.",
                )
                # Unknown tokens fall back to the raw token.
                self.assertEqual(_axis_value("unknown", mapping), "unknown")
                # Empty tokens map to the empty string.
                self.assertEqual(_axis_value("", mapping), "")

            def test_parse_recipe_extracts_static_prompt_and_axes(self) -> None:
                recipe = "debug · full · narrow · rigor · plain · rog"

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    style,
                    directional,
                ) = _parse_recipe(recipe)

                self.assertEqual(static_prompt, "debug")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "narrow")
                self.assertEqual(method, "rigor")
                self.assertEqual(style, "plain")
                self.assertEqual(directional, "rog")

            def test_model_pattern_run_name_dispatches_and_updates_last_recipe(self) -> None:
                """Ensure pattern selection flows through to GPTState.last_recipe."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")

                UserActions.model_pattern_run_name(target.name)

                actions.app.notify.assert_called_once()
                actions.user.gpt_apply_prompt.assert_called_once()
                actions.user.model_pattern_gui_close.assert_called_once()

                # modelPatternGUI keeps last_recipe concise and token-based, but
                # omits the style token in the recap; this assertion matches that
                # current behaviour rather than restating the full axes.
                self.assertEqual(
                    GPTState.last_recipe,
                    "debug · full · narrow · rigor",
                )
                self.assertEqual(GPTState.last_static_prompt, "debug")
                self.assertEqual(GPTState.last_completeness, "full")
                self.assertEqual(GPTState.last_scope, "narrow")
                self.assertEqual(GPTState.last_method, "rigor")
                # last_style is left empty for this pattern; the style token is
                # not included in last_recipe.
                self.assertEqual(GPTState.last_style, "")
                self.assertEqual(GPTState.last_directional, "rog")

            def test_all_pattern_static_prompts_exist_in_config_and_list(self) -> None:
                """Ensure every pattern's static prompt token is wired into config and the list."""
                root = Path(__file__).resolve().parents[1]
                static_list_path = root / "GPT" / "lists" / "staticPrompt.talon-list"
                talon_keys: set[str] = set()
                with static_list_path.open("r", encoding="utf-8") as f:
                    for line in f:
                        s = line.strip()
                        if (
                            not s
                            or s.startswith("#")
                            or s.startswith("list:")
                            or s == "-"
                        ):
                            continue
                        if ":" not in s:
                            continue
                        key, _ = s.split(":", 1)
                        talon_keys.add(key.strip())

                config_keys = set(STATIC_PROMPT_CONFIG.keys())

                for pattern in PATTERNS:
                    static_prompt, *_ = _parse_recipe(pattern.recipe)
                    self.assertIn(
                        static_prompt,
                        config_keys,
                        f"Pattern {pattern.name!r} uses static prompt {static_prompt!r} "
                        "which is missing from STATIC_PROMPT_CONFIG",
                    )
                    self.assertIn(
                        static_prompt,
                        talon_keys,
                        f"Pattern {pattern.name!r} uses static prompt {static_prompt!r} "
                        "which is missing from staticPrompt.talon-list",
                    )

    except ImportError:
        if not TYPE_CHECKING:
            class ModelPatternGUITests(unittest.TestCase):
                @unittest.skip("modelPatternGUI unavailable in this Talon runtime")
                def test_placeholder(self) -> None:
                    pass

else:
    if not TYPE_CHECKING:
        class ModelPatternGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
