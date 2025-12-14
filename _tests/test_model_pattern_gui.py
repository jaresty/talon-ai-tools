import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch
import importlib

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
            pattern_debug_snapshot,
        )
        from talon_user.lib.patternDebugCoordinator import (
            pattern_debug_catalog,
            pattern_debug_view,
        )
        from talon_user.lib.modelState import GPTState
        from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG
        import talon_user.lib.talonSettings as talonSettings

        class ModelPatternGUITests(unittest.TestCase):
            def setUp(self) -> None:
                GPTState.reset_all()
                PatternGUIState.domain = None
                actions.app.notify = MagicMock()
                actions.user.notify = MagicMock()
                actions.user.gpt_apply_prompt = MagicMock()
                actions.user.model_pattern_gui_close = MagicMock()
                # Ensure talon_user.lib is importable for patch targets.
                importlib.import_module("talon_user.lib.patternDebugCoordinator")

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
                recipe = "describe · full · narrow · debugging · bullets · rog"

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "narrow")
                self.assertEqual(method, "debugging")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "rog")

            def test_model_pattern_run_name_dispatches_and_updates_last_recipe(
                self,
            ) -> None:
                """Ensure pattern selection flows through to GPTState.last_recipe."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")

                UserActions.model_pattern_run_name(target.name)

                actions.app.notify.assert_called_once()
                actions.user.gpt_apply_prompt.assert_called_once()
                actions.user.model_pattern_gui_close.assert_called_once()

                # modelPatternGUI keeps last_recipe concise and token-based.
                self.assertEqual(
                    GPTState.last_recipe,
                    "describe · full · narrow · debugging",
                )
                self.assertEqual(GPTState.last_static_prompt, "describe")
                self.assertEqual(GPTState.last_completeness, "full")
                self.assertEqual(GPTState.last_scope, "narrow")
                self.assertEqual(GPTState.last_method, "debugging")
                self.assertEqual(GPTState.last_form, "")
                self.assertEqual(GPTState.last_channel, "")
                self.assertEqual(GPTState.last_directional, "rog")

            def test_model_pattern_handles_legacy_style_prompt_error(self) -> None:
                """Pattern run should surface migration hint and abort on legacy style."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")
                # Simulate modelPrompt raising on legacy style tokens.
                with patch.object(
                    talonSettings, "modelPrompt", side_effect=ValueError("style axis is removed")
                ):
                    UserActions.model_pattern_run_name(target.name)

                actions.user.gpt_apply_prompt.assert_not_called()
                # Either user- or app-level notification should carry the hint.
                notifications = [
                    str(args[0])
                    for args in [
                        *(ca.args for ca in actions.app.notify.call_args_list),
                        *(ca.args for ca in actions.user.notify.call_args_list),
                    ]
                    if args
                ]
                self.assertTrue(
                    any("style axis is removed" in note or "styleModifier is no longer supported" in note for note in notifications),
                    f"Expected migration hint notification, got {notifications}",
                )

            def test_model_pattern_save_source_delegates_to_confirmation_helper(
                self,
            ) -> None:
                actions.user.confirmation_gui_save_to_file = MagicMock()

                UserActions.model_pattern_save_source_to_file()

                actions.user.confirmation_gui_save_to_file.assert_called_once_with()

            def test_pattern_with_form_token_sets_form_axis(self) -> None:
                """Patterns that include a form token map to the form axis."""

                target = next(p for p in PATTERNS if p.name == "Sketch diagram")

                UserActions.model_pattern_run_name(target.name)

                self.assertEqual(GPTState.last_static_prompt, "describe")
                self.assertEqual(GPTState.last_completeness, "gist")
                self.assertEqual(GPTState.last_scope, "focus")
                self.assertEqual(GPTState.last_method, "structure")
                self.assertEqual(GPTState.last_form, "code")
                self.assertEqual(GPTState.last_channel, "diagram")
                self.assertEqual(GPTState.last_directional, "fog")

            def test_parse_recipe_handles_new_method_tokens(self) -> None:
                """New method tokens like 'flow' should be parsed as methods."""
                target = next(p for p in PATTERNS if p.name == "Explain flow")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(target.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "flow")
                self.assertEqual(form, "")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_slack_and_jira_patterns_are_configured(self) -> None:
                """Slack summary and Jira ticket patterns should parse to expected axes."""
                slack = next(p for p in PATTERNS if p.name == "Slack summary")
                jira = next(p for p in PATTERNS if p.name == "Jira ticket")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(slack.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "")
                self.assertEqual(form, "")
                self.assertEqual(channel, "slack")
                self.assertEqual(directional, "fog")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(jira.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "steps")
                self.assertEqual(form, "story")
                self.assertEqual(channel, "jira")
                self.assertEqual(directional, "fog")

            def test_parse_recipe_ignores_unknown_axis_tokens(self) -> None:
                """Recipes with unknown axis tokens should keep known tokens and ignore unknown ones."""
                recipe = "describe · full · actions UNKNOWN_SCOPE · structure UNKNOWN_METHOD · jira UNKNOWN_FORM · rog"

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                # Only known scope token should be retained.
                self.assertEqual(scope, "actions")
                # Only known method token should be retained.
                self.assertEqual(method, "structure")
                # Only known channel token should be retained.
                self.assertEqual(form, "")
                self.assertEqual(channel, "jira")
                self.assertEqual(directional, "rog")

            def test_parse_recipe_applies_axis_caps_and_canonicalises(self) -> None:
                """Recipes exceeding axis caps should be canonicalised with last-wins semantics."""
                recipe = (
                    "describe · full · actions edges system · steps plan rigor filter · "
                    "plain bullets taxonomy · slack jira · rog fog"
                )

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "edges system")
                self.assertEqual(method, "filter plan rigor")
                self.assertEqual(form, "taxonomy")
                self.assertEqual(channel, "jira")
                self.assertEqual(directional, "fog")

            def test_motif_scan_pattern_uses_motifs_method(self) -> None:
                """Motif scan pattern should use relations scope and motifs method."""
                motif = next(p for p in PATTERNS if p.name == "Motif scan")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(motif.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "relations")
                self.assertEqual(method, "motifs")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_pattern_debug_snapshot_includes_axes_and_state(self) -> None:
                """pattern_debug_snapshot should expose config and GPTState axes."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")

                GPTState.last_recipe = "unit-test-recipe"
                GPTState.last_axes = {
                    "completeness": ["full"],
                    "scope": ["narrow"],
                    "method": ["debugging"],
                    "form": [],
                    "channel": [],
                }

                snapshot = pattern_debug_snapshot(target.name)

                self.assertEqual(snapshot["name"], target.name)
                self.assertEqual(snapshot["domain"], target.domain)
                self.assertEqual(snapshot["description"], target.description)
                self.assertEqual(snapshot["recipe"], target.recipe)
                self.assertEqual(snapshot["static_prompt"], "describe")

                axes = snapshot["axes"]
                self.assertEqual(axes["completeness"], "full")
                self.assertEqual(axes["scope"], ["narrow"])
                self.assertEqual(axes["method"], ["debugging"])
                self.assertEqual(axes.get("form", []), [])
                self.assertEqual(axes.get("channel", []), [])
                self.assertEqual(axes["directional"], "rog")

                self.assertEqual(snapshot["last_recipe"], "unit-test-recipe")
                self.assertEqual(snapshot["last_axes"], GPTState.last_axes)

            def test_pattern_debug_snapshot_unknown_pattern_returns_empty_dict(
                self,
            ) -> None:
                snapshot = pattern_debug_snapshot("does-not-exist")
                self.assertEqual(snapshot, {})

            def test_pattern_debug_catalog_includes_all_patterns(self) -> None:
                """pattern_debug_catalog should return a snapshot per pattern by default."""
                snapshots = pattern_debug_catalog()
                names = {snap["name"] for snap in snapshots}
                for pattern in PATTERNS:
                    self.assertIn(pattern.name, names)

            def test_pattern_debug_view_builds_gui_friendly_recipe_line(self) -> None:
                """pattern_debug_view should expose name, axes, last_axes, and a concise recipe line."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")

                # Seed GPTState axes so the underlying snapshot has last_axes data.
                GPTState.last_axes = {
                    "completeness": ["full"],
                    "scope": ["narrow"],
                    "method": ["debugging"],
                    "form": [],
                    "channel": [],
                }

                view = pattern_debug_view(target.name)
                self.assertEqual(view["name"], target.name)
                # Axes in the view should match the snapshot axes shape tested elsewhere.
                axes = view["axes"]
                self.assertEqual(axes["completeness"], "full")
                self.assertEqual(axes["scope"], ["narrow"])
                self.assertEqual(axes["method"], ["debugging"])
                self.assertEqual(axes.get("form", []), [])
                self.assertEqual(axes.get("channel", []), [])
                self.assertEqual(axes["directional"], "rog")

                # recipe_line should be a concise, token-based recap including directional.
                self.assertEqual(
                    view["recipe_line"],
                    "describe · full · narrow · debugging · rog",
                )
                # last_axes should surface the seeded GPTState.last_axes.
                self.assertEqual(view["last_axes"], GPTState.last_axes)

            def test_model_pattern_debug_name_uses_coordinator_view(self) -> None:
                """model_pattern_debug_name should call the coordinator view and notify with its recipe line."""
                target = next(p for p in PATTERNS if p.name == "Debug bug")

                pdc = importlib.import_module("talon_user.lib.patternDebugCoordinator")

                with patch.object(
                    pdc,
                    "pattern_debug_view",
                    return_value={
                        "name": target.name,
                        "recipe_line": "describe · full · narrow · debugging · rog",
                        "axes": {
                            "completeness": "full",
                            "scope": ["narrow"],
                            "method": ["debugging"],
                            "form": [],
                            "channel": [],
                            "directional": "rog",
                        },
                        "last_axes": {},
                    },
                ) as mocked_view:
                    calls: list[str] = []

                    def _notify(msg: str) -> None:
                        calls.append(msg)

                    actions.app.notify = _notify  # type: ignore[assignment]

                    UserActions.model_pattern_debug_name(target.name)

                mocked_view.assert_called_once_with(target.name)
                self.assertEqual(len(calls), 1)
                message = calls[0]
                self.assertIn("Pattern debug:", message)
                self.assertIn(target.name, message)
                self.assertIn("describe · full · narrow · debugging · rog", message)

            def test_pattern_debug_catalog_filters_by_domain(self) -> None:
                """pattern_debug_catalog should filter snapshots by domain when requested."""
                coding_snapshots = pattern_debug_catalog(domain="coding")
                writing_snapshots = pattern_debug_catalog(domain="writing")

                self.assertTrue(coding_snapshots)
                self.assertTrue(writing_snapshots)

                coding_domains = {snap["domain"] for snap in coding_snapshots}
                writing_domains = {snap["domain"] for snap in writing_snapshots}

                self.assertEqual(coding_domains, {"coding"})
                self.assertEqual(writing_domains, {"writing"})

            def test_type_outline_pattern_uses_taxonomy_style(self) -> None:
                """Type outline pattern should use taxonomy style."""
                pattern = next(p for p in PATTERNS if p.name == "Type outline")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "")
                self.assertEqual(form, "taxonomy")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "rog")

            def test_xp_next_steps_pattern_uses_xp_method(self) -> None:
                """XP next steps pattern should use xp method on actions scope."""
                pattern = next(p for p in PATTERNS if p.name == "XP next steps")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "actions")
                self.assertEqual(method, "xp")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "ong")

            def test_explain_for_beginner_pattern_uses_scaffold_method(self) -> None:
                """Explain for beginner pattern should use scaffold method."""
                pattern = next(p for p in PATTERNS if p.name == "Explain for beginner")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "scaffold")
                self.assertEqual(form, "")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_liberating_facilitation_pattern_uses_liberating_method(
                self,
            ) -> None:
                """Liberating facilitation pattern should use liberating method."""
                pattern = next(
                    p for p in PATTERNS if p.name == "Liberating facilitation"
                )

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "liberating")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "rog")

            def test_diverge_options_pattern_uses_diverge_method(self) -> None:
                """Diverge options pattern should use diverge method."""
                pattern = next(p for p in PATTERNS if p.name == "Diverge options")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "diverge")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_converge_decision_pattern_uses_converge_method(self) -> None:
                """Converge decision pattern should use converge method."""
                pattern = next(p for p in PATTERNS if p.name == "Converge decision")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "focus")
                self.assertEqual(method, "converge")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "rog")

            def test_mapping_scan_pattern_uses_mapping_method(self) -> None:
                """Mapping scan pattern should use mapping method on relations scope."""
                pattern = next(p for p in PATTERNS if p.name == "Mapping scan")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "relations")
                self.assertEqual(method, "mapping")
                self.assertEqual(form, "bullets")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_tap_map_pattern_uses_full_and_taxonomy(self) -> None:
                """Tap map pattern should use full completeness, system scope, mapping method, and taxonomy style."""
                pattern = next(p for p in PATTERNS if p.name == "Tap map")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "system")
                self.assertEqual(method, "mapping")
                self.assertEqual(form, "taxonomy")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_multi_angle_view_pattern_uses_diverge_and_cards(self) -> None:
                """Multi-angle view pattern should use diverge method on relations scope with cards style."""
                pattern = next(p for p in PATTERNS if p.name == "Multi-angle view")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "full")
                self.assertEqual(scope, "relations")
                self.assertEqual(method, "diverge")
                self.assertEqual(form, "cards")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "rog")

            def test_flip_it_review_pattern_uses_adversarial_and_edges(self) -> None:
                """Flip it review pattern should use adversarial method on edges scope with fog lens."""
                pattern = next(p for p in PATTERNS if p.name == "Flip it review")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "edges")
                self.assertEqual(method, "adversarial")
                self.assertEqual(form, "")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "fog")

            def test_systems_path_pattern_uses_mapping_steps_and_ong(self) -> None:
                """Systems path pattern should use mapping method, steps, and ong directional on system scope."""
                pattern = next(p for p in PATTERNS if p.name == "Systems path")

                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    form,
                    channel,
                    directional,
                ) = _parse_recipe(pattern.recipe)

                self.assertEqual(static_prompt, "describe")
                self.assertEqual(completeness, "gist")
                self.assertEqual(scope, "system")
                self.assertEqual(method, "mapping")
                # Systems path does not fix a specific style; default is fine.
                self.assertEqual(form, "")
                self.assertEqual(channel, "")
                self.assertEqual(directional, "ong")

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
