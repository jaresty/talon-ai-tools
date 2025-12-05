import textwrap
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import pathlib

    from talon_user.GPT.gpt import _build_axis_docs, _build_static_prompt_docs
    from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG
    from talon_user.lib.modelPatternGUI import PATTERNS, _parse_recipe

    class StaticPromptDocsTests(unittest.TestCase):
        def setUp(self) -> None:
            # Ensure we start from the real staticPrompt.talon-list so this
            # test characterises current behaviour rather than overwriting it.
            root = pathlib.Path(__file__).resolve().parents[1]
            self._static_list_path = (
                root / "GPT" / "lists" / "staticPrompt.talon-list"
            )
            self.assertTrue(
                self._static_list_path.is_file(),
                "staticPrompt.talon-list should exist for this test",
            )

        def test_static_prompt_docs_include_profiled_and_unprofiled_prompts(self) -> None:
            docs = _build_static_prompt_docs()

            # A profiled prompt like "todo" should appear with its description
            # and axis defaults, since it lives in STATIC_PROMPT_CONFIG.
            self.assertIn("todo", docs)
            self.assertIn("Format this as a todo list.", docs)
            self.assertIn("defaults:", docs)

            # The fallback line listing other prompts (tokens only) should
            # still be present for unprofiled prompts.
            self.assertIn("Other static prompts (tokens only;", docs)

        def test_all_profiled_prompts_have_static_prompt_token(self) -> None:
            """Guardrail: every profiled prompt key should appear in the Talon list."""
            root = pathlib.Path(__file__).resolve().parents[1]
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
            # The list may contain additional unprofiled prompts, but every
            # profiled prompt should have a corresponding token.
            self.assertTrue(
                config_keys.issubset(talon_keys),
                f"Profiled static prompts missing from staticPrompt.talon-list: {sorted(config_keys - talon_keys)}",
            )

        def test_static_prompt_docs_note_axis_only_behaviours(self) -> None:
            """Static prompt docs should mention axis-only behaviours and where to find recipes."""
            docs = _build_static_prompt_docs()
            self.assertIn(
                "live only as style/method axis values",
                docs,
            )

        def test_axis_docs_include_all_axis_sections(self) -> None:
            """Characterise the axis docs block for completeness."""
            docs = _build_axis_docs()

            # Headings for each axis group should be present.
            self.assertIn("Completeness modifiers:", docs)
            self.assertIn("Scope modifiers:", docs)
            self.assertIn("Method modifiers:", docs)
            self.assertIn("Style modifiers:", docs)
            self.assertIn("Directional modifiers:", docs)

            # At least one known key from each list should appear.
            self.assertIn("full:", docs)
            self.assertIn("narrow:", docs)
            self.assertIn("steps:", docs)
            self.assertIn("plain:", docs)
            # Directional keys depend on local config; check for a typical one.
            self.assertTrue(
                any(k in docs for k in ("fog:", "rog:", "ong:")),
                "Expected at least one directional modifier key in axis docs",
            )

        def test_axis_docs_note_adrs_and_readme_cheat_sheet(self) -> None:
            """Axis docs should point readers at ADRs and the README cheat sheet."""
            docs = _build_axis_docs()
            self.assertIn(
                "ADR 005/012/013/016",
                docs,
            )

        def test_new_completeness_and_method_tokens_present(self) -> None:
            """Ensure ADR 017's axis tokens exist in the Talon lists."""
            root = pathlib.Path(__file__).resolve().parents[1]

            completeness_list_path = root / "GPT" / "lists" / "completenessModifier.talon-list"
            completeness_keys: set[str] = set()
            with completeness_list_path.open("r", encoding="utf-8") as f:
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
                    completeness_keys.add(key.strip())

            method_list_path = root / "GPT" / "lists" / "methodModifier.talon-list"
            method_keys: set[str] = set()
            with method_list_path.open("r", encoding="utf-8") as f:
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
                    method_keys.add(key.strip())

            style_list_path = root / "GPT" / "lists" / "styleModifier.talon-list"
            style_keys: set[str] = set()
            with style_list_path.open("r", encoding="utf-8") as f:
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
                    style_keys.add(key.strip())

            self.assertIn(
                "analysis",
                method_keys,
                "Expected 'analysis' method token from ADR 017 to be present",
            )
            self.assertIn(
                "samples",
                method_keys,
                "Expected 'samples' method token from ADR 017/018 to be present",
            )
            self.assertIn(
                "socratic",
                method_keys,
                "Expected 'socratic' method token from ADR 018 to be present",
            )
            self.assertIn(
                "faq",
                style_keys,
                "Expected 'faq' style token from ADR 018 to be present",
            )

        def test_axis_only_tokens_do_not_appear_as_static_prompts(self) -> None:
            """Guardrail: axis-only tokens from ADR 012 must not be static prompts."""
            root = pathlib.Path(__file__).resolve().parents[1]
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

            # Style-only behaviours (ADR 012 axis-only styles).
            style_only = {
                "diagram",
                "presenterm",
                "HTML",
                "gherkin",
                "shell",
                "code",
                "emoji",
                "format",
                "recipe",
                "lens",
                "commit",
                "ADR",
                "taxonomy",
            }
            # Method-only or axis-shaped prompts that were retired as static prompts.
            method_only = {
                "debug",
                "structure",
                "flow",
                "compare",
                "type",
                "relation",
                "clusters",
                "motifs",
            }

            forbidden = style_only | method_only
            present = sorted(forbidden & talon_keys)
            self.assertEqual(
                present,
                [],
                f"Axis-only tokens should not appear as staticPrompt keys, but found: {present}",
            )

        def test_pattern_static_prompts_are_documented(self) -> None:
            """Ensure patterns' static prompts are mentioned in static prompt docs."""
            docs = _build_static_prompt_docs()
            missing: list[str] = []
            for pattern in PATTERNS:
                static_prompt, *_ = _parse_recipe(pattern.recipe)
                if static_prompt not in docs:
                    missing.append(f"{pattern.name!r} uses {static_prompt!r}")

            self.assertFalse(
                missing,
                f"Expected all pattern static prompts to appear in docs; missing: {', '.join(missing)}",
            )

        def test_directional_list_matches_adr_016_core_and_retired_tokens(self) -> None:
            """Guardrail: directional list includes core lenses and excludes retired tokens (ADR 016)."""
            root = pathlib.Path(__file__).resolve().parents[1]
            directional_list_path = root / "GPT" / "lists" / "directionalModifier.talon-list"
            talon_keys: set[str] = set()
            with directional_list_path.open("r", encoding="utf-8") as f:
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

            # Core directional lenses from ADR 016 that must be present.
            core_lenses = {"fog", "fig", "dig", "ong", "rog", "bog", "jog"}
            missing_core = sorted(core_lenses - talon_keys)
            self.assertFalse(
                missing_core,
                f"Core directional lenses from ADR 016 missing from directionalModifier.talon-list: {missing_core}",
            )

            # Tokens explicitly retired by ADR 016 should not appear.
            retired = {"flip", "flop"}
            present_retired = sorted(retired & talon_keys)
            self.assertEqual(
                present_retired,
                [],
                f"Retired directional tokens from ADR 016 should not be present: {present_retired}",
            )

else:
    if not TYPE_CHECKING:
        class StaticPromptDocsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
