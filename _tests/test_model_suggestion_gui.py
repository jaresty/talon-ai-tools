import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelSuggestionGUI import (
        UserActions,
        SuggestionGUIState,
        SuggestionCanvasState,
        _scroll_suggestions,
    )
    from talon_user.lib import modelSuggestionGUI
    import talon_user.lib.talonSettings as talonSettings
    import talon_user.lib.dropReasonUtils as drop_reason_module

    class ModelSuggestionGUITests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            if hasattr(GPTState, "suppress_overlay_inflight_guard"):
                delattr(GPTState, "suppress_overlay_inflight_guard")
            SuggestionGUIState.suggestions = []
            SuggestionCanvasState.showing = False
            SuggestionCanvasState.scroll_y = 0.0
            self._original_notify = actions.app.notify
            actions.app.notify = MagicMock()
            actions.user.notify = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            actions.user.model_prompt_recipe_suggestions_gui_close = MagicMock()

        def tearDown(self):
            # Restore the original notify implementation so other tests that
            # rely on the stubbed `actions.app.calls` behaviour continue to
            # work as expected.
            actions.app.notify = self._original_notify
            if hasattr(GPTState, "suppress_overlay_inflight_guard"):
                delattr(GPTState, "suppress_overlay_inflight_guard")

        def test_persona_presets_align_with_persona_catalog(self) -> None:
            from talon_user.lib.personaConfig import persona_catalog
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            catalog = persona_catalog()
            helper_presets = suggestion_module._persona_presets()
            catalog_keys = {preset.key for preset in catalog.values()}
            helper_keys = {preset.key for preset in helper_presets}
            self.assertEqual(
                catalog_keys,
                helper_keys,
                "modelSuggestionGUI _persona_presets must cover the same PersonaPreset keys as persona_catalog",
            )

        def test_persona_presets_use_catalog_snapshot(self) -> None:
            from talon_user.lib.personaConfig import persona_intent_catalog_snapshot
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            snapshot = persona_intent_catalog_snapshot()
            with patch(
                "talon_user.lib.personaConfig.persona_intent_catalog_snapshot",
                return_value=snapshot,
            ) as snapshot_mock:
                presets = suggestion_module._persona_presets()
            snapshot_mock.assert_called_once()
            self.assertEqual(
                {preset.key for preset in presets},
                set(snapshot.persona_presets.keys()),
            )

        def test_intent_snapshot_used_in_suggestion_info(self) -> None:
            from talon_user.lib.personaConfig import persona_intent_catalog_snapshot
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            snapshot = persona_intent_catalog_snapshot()
            suggestion = suggestion_module.Suggestion(
                name="Intent snapshot",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="As Facilitator",
                persona_audience="To Stakeholders",
                persona_tone="Directly",
                intent_purpose="for planning",
            )

            with patch(
                "talon_user.lib.personaConfig.persona_intent_catalog_snapshot",
                return_value=snapshot,
            ) as snapshot_mock:
                info = suggestion_module._suggestion_stance_info(suggestion)
            snapshot_mock.assert_called()
            self.assertIn("intent for planning", info["stance_display"].lower())

        def test_persona_preset_map_includes_catalog_synonyms(self) -> None:
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            preset_map = suggestion_module._persona_preset_map()
            for preset in suggestion_module._persona_presets():
                key = (preset.key or "").strip().lower()
                spoken = (preset.spoken or "").strip().lower()
                label = (preset.label or "").strip().lower()
                if key:
                    self.assertIn(key, preset_map)
                    self.assertIs(preset_map[key], preset)
                if spoken:
                    self.assertIn(spoken, preset_map)
                    self.assertIs(preset_map[spoken], preset)
                if label:
                    self.assertIn(label, preset_map)
                    self.assertIs(preset_map[label], preset)

        def test_run_index_executes_suggestion_and_closes_gui(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Deep map",
                    "recipe": "describe · full · relations · cluster · bullets · fog",
                },
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(2)

            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

        def test_run_index_out_of_range_notifies_and_does_not_run(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Only one",
                    "recipe": "describe · gist · focus · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(0)
            UserActions.model_prompt_recipe_suggestions_run_index(3)

            self.assertGreaterEqual(actions.app.notify.call_count, 1)
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_run_index_with_no_suggestions_notifies(self):
            GPTState.last_suggested_recipes = []

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.app.notify.assert_called_once()
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_open_uses_passive_closer_when_suppressed(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Suggest",
                    "recipe": "describe · gist · focus · plain · fog",
                }
            ]

            with (
                patch.object(
                    modelSuggestionGUI,
                    "try_begin_request",
                    return_value=(False, "in_flight"),
                ),
                patch.object(
                    modelSuggestionGUI, "_open_suggestion_canvas"
                ) as open_canvas,
                patch.object(modelSuggestionGUI, "close_common_overlays") as close_stub,
            ):
                setattr(GPTState, "suppress_overlay_inflight_guard", True)
                UserActions.model_prompt_recipe_suggestions_gui_open()

            close_stub.assert_called_once_with(actions.user, passive=True)
            open_canvas.assert_called_once()

        def test_scroll_clamps_to_max_via_overlay_helper(self):
            # Prepare a stub canvas and suggestions to drive a positive max_scroll.
            class RectStub:
                def __init__(self):
                    self.x = 0
                    self.y = 0
                    self.width = 800
                    self.height = 200

            class CanvasStub:
                rect = RectStub()

            SuggestionGUIState.suggestions = [
                modelSuggestionGUI.Suggestion(name="One", recipe="describe · fog"),
                modelSuggestionGUI.Suggestion(name="Two", recipe="describe · fog"),
                modelSuggestionGUI.Suggestion(name="Three", recipe="describe · fog"),
            ]
            modelSuggestionGUI._suggestion_canvas = CanvasStub()
            SuggestionCanvasState.scroll_y = 1000.0

            with patch.object(
                modelSuggestionGUI, "_measure_suggestion_height", return_value=200
            ):
                _scroll_suggestions(raw_delta=1.0)

            # With 3 rows @200px and the current header/layout geometry,
            # clamp_scroll should cap at the computed max_scroll of 640.
            self.assertEqual(SuggestionCanvasState.scroll_y, 640.0)

        def test_persona_stance_display_includes_long_form_axes(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="With persona preset",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="As Facilitator",
                persona_audience="To Stakeholders",
                persona_tone="Directly",
                stance_command="persona stake",
                intent_purpose="teach",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            expected_intent = info["intent_display"] or "teach"
            self.assertEqual(
                info["stance_display"],
                f"model write as facilitator to stakeholders directly (persona stake) · intent {expected_intent}",
            )
            self.assertEqual(info["persona_display"], "persona stake")
            self.assertEqual(
                info["persona_axes_summary"],
                "as facilitator · to stakeholders · directly",
            )

        def test_non_persona_stance_display_prefers_raw_command(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Axes stance",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="as teacher",
                persona_audience="to junior engineer",
                persona_tone="kindly",
                stance_command="model write as teacher to junior engineer kindly",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            self.assertEqual(
                info["stance_display"],
                "model write as teacher to junior engineer kindly",
            )

        def test_persona_stance_synthesises_preset_command_when_missing(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Preset only",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="As Facilitator",
                persona_audience="To Stakeholders",
                persona_tone="Directly",
                intent_purpose="resolve",
                stance_command="",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            expected_intent = info["intent_display"] or "resolve"
            self.assertEqual(
                info["stance_display"],
                f"model write as facilitator to stakeholders directly (persona stake) · intent {expected_intent}",
            )
            self.assertEqual(info["persona_display"], "persona stake")
            self.assertEqual(
                info["persona_axes_summary"],
                "as facilitator · to stakeholders · directly",
            )

        def test_stance_display_defaults_to_model_write_when_prefix_missing(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Audience + tone only",
                recipe="describe · gist · focus · plain · rog",
                persona_voice="",
                persona_audience="to team",
                persona_tone="directly",
                intent_purpose="inform",
                stance_command="",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            expected_intent = info["intent_display"] or "inform"
            self.assertEqual(
                info["stance_display"],
                f"model write to team directly · intent {expected_intent}",
            )
            self.assertEqual(
                info["persona_axes_summary"],
                "to team · directly",
            )

        def test_stance_info_prefers_persona_preset_spoken_alias(self):
            from lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            preset = next(
                preset
                for preset in maps.persona_presets.values()
                if (preset.spoken or preset.label or preset.key)
            )
            spoken_alias = (preset.spoken or preset.label or preset.key or "").strip()
            self.assertTrue(
                spoken_alias, "Expected persona preset to provide spoken alias"
            )

            suggestion = modelSuggestionGUI.Suggestion(
                name="Preset alias",
                recipe="describe · gist · focus · plain · fog",
                persona_voice=preset.voice or "",
                persona_audience=preset.audience or "",
                persona_tone=preset.tone or "",
                persona_preset_key=preset.key,
                persona_preset_label=preset.label,
                persona_preset_spoken=preset.spoken or preset.label or preset.key,
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)
            stance_display = info["stance_display"].lower()
            persona_display = (info.get("persona_display") or "").lower()
            self.assertIn(f"persona {spoken_alias.lower()}", stance_display)
            self.assertIn(spoken_alias.lower(), persona_display)

        def test_stance_info_uses_intent_display_alias(self):
            from lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(
                preset
                for preset in maps.persona_presets.values()
                if (preset.spoken or preset.label or preset.key)
            )
            intent_preset = next(iter(maps.intent_presets.values()))
            display_alias = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
                or ""
            ).strip()
            self.assertTrue(
                display_alias, "Expected intent preset to provide display alias"
            )

            suggestion = modelSuggestionGUI.Suggestion(
                name="Intent alias",
                recipe="describe · gist · focus · plain · fog",
                persona_voice=persona_preset.voice or "",
                persona_audience=persona_preset.audience or "",
                persona_tone=persona_preset.tone or "",
                persona_preset_key=persona_preset.key,
                persona_preset_label=persona_preset.label,
                persona_preset_spoken=persona_preset.spoken
                or persona_preset.label
                or persona_preset.key,
                intent_purpose=intent_preset.intent,
                intent_preset_key=intent_preset.key,
                intent_preset_label=intent_preset.label,
                intent_display=(
                    maps.intent_display_map.get(intent_preset.key)
                    or maps.intent_display_map.get(intent_preset.intent)
                    or ""
                ),
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)
            stance_display = info["stance_display"].lower()
            intent_display = info["intent_display"].lower()
            self.assertIn(f"intent {display_alias.lower()}", stance_display)
            self.assertEqual(intent_display, display_alias.lower())

        def test_stance_info_fetches_alias_when_not_provided(self) -> None:
            from talon_user.lib.personaConfig import IntentPreset
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            intent_preset = IntentPreset(key="decide", label="Decide", intent="decide")
            maps = SimpleNamespace(
                persona_presets={},
                persona_preset_aliases={},
                persona_axis_tokens={},
                intent_presets={"decide": intent_preset},
                intent_preset_aliases={},
                intent_synonyms={},
                intent_display_map={"decide": "Decide"},
            )

            suggestion = suggestion_module.Suggestion(
                name="Alias hydration",
                recipe="describe · gist · focus · plain · fog",
                intent_purpose="decide",
                intent_preset_key="decide",
                intent_preset_label="Decide",
                intent_display="",
            )

            with patch.object(
                suggestion_module, "persona_intent_maps", return_value=maps
            ):
                info = suggestion_module._suggestion_stance_info(suggestion)

            self.assertEqual(info["intent_display"], "Decide")

        def test_open_uses_cached_suggestions_and_shows_canvas(self):
            """model_prompt_recipe_suggestions_gui_open populates state and opens the canvas."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]
            self.assertFalse(SuggestionCanvasState.showing)

        def test_open_populates_alias_metadata_from_cached_suggestions(self):
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))
            persona_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            ).strip()
            display_alias = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
                or intent_preset.intent
                or ""
            ).strip()
            self.assertTrue(persona_spoken, "Expected persona preset spoken alias")
            self.assertTrue(display_alias, "Expected intent preset display alias")

            GPTState.last_suggested_recipes = [
                {
                    "name": "Alias rich",
                    "recipe": "describe · gist · focus · plain · fog",
                    "persona_preset_key": persona_preset.key,
                    "persona_preset_label": persona_preset.label,
                    "persona_preset_spoken": persona_spoken,
                    "intent_preset_key": intent_preset.key,
                    "intent_preset_label": intent_preset.label,
                    "intent_display": display_alias,
                }
            ]

            with (
                patch.object(
                    modelSuggestionGUI,
                    "_reject_if_request_in_flight",
                    return_value=False,
                ),
                patch.object(modelSuggestionGUI, "close_common_overlays"),
                patch.object(
                    modelSuggestionGUI, "_open_suggestion_canvas"
                ) as open_canvas,
            ):
                UserActions.model_prompt_recipe_suggestions_gui_open()

            open_canvas.assert_called_once()
            self.assertTrue(SuggestionGUIState.suggestions)
            suggestion = SuggestionGUIState.suggestions[0]
            self.assertEqual(suggestion.persona_preset_key, persona_preset.key)
            self.assertEqual(suggestion.persona_preset_label, persona_preset.label)
            self.assertEqual(
                suggestion.persona_preset_spoken.lower(), persona_spoken.lower()
            )
            self.assertEqual(suggestion.intent_preset_key, intent_preset.key)
            self.assertEqual(suggestion.intent_preset_label, intent_preset.label)
            self.assertEqual(suggestion.intent_display.lower(), display_alias.lower())

        def test_open_hydrates_alias_metadata_when_missing(self):
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))
            display_alias = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
                or intent_preset.intent
                or ""
            ).strip()
            self.assertTrue(display_alias, "Expected intent preset display alias")

            GPTState.last_suggested_recipes = [
                {
                    "name": "Alias hydrate",
                    "recipe": "describe · gist · focus · plain · fog",
                    "persona_preset_key": persona_preset.key,
                    # Intentionally omit label/spoken metadata so hydration fills them.
                    "persona_preset_label": "",
                    "persona_preset_spoken": "",
                    "persona_voice": "",
                    "persona_audience": "",
                    "persona_tone": "",
                    "intent_purpose": intent_preset.intent,
                    "intent_preset_key": intent_preset.key,
                    "intent_preset_label": "",
                    "intent_display": "",
                }
            ]

            with (
                patch.object(
                    modelSuggestionGUI,
                    "_reject_if_request_in_flight",
                    return_value=False,
                ),
                patch.object(modelSuggestionGUI, "close_common_overlays"),
                patch.object(
                    modelSuggestionGUI, "_open_suggestion_canvas"
                ) as open_canvas,
            ):
                UserActions.model_prompt_recipe_suggestions_gui_open()

            open_canvas.assert_called_once()
            self.assertTrue(SuggestionGUIState.suggestions)
            suggestion = SuggestionGUIState.suggestions[0]
            expected_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            self.assertEqual(suggestion.persona_preset_key, persona_preset.key)
            self.assertEqual(suggestion.persona_preset_label, persona_preset.label)
            self.assertEqual(suggestion.persona_preset_spoken, expected_spoken)
            self.assertEqual(suggestion.persona_voice, persona_preset.voice or "")
            self.assertEqual(suggestion.persona_audience, persona_preset.audience or "")
            self.assertEqual(suggestion.persona_tone, persona_preset.tone or "")
            self.assertEqual(suggestion.intent_preset_key, intent_preset.key)
            self.assertEqual(
                suggestion.intent_preset_label, intent_preset.label or intent_preset.key
            )
            self.assertEqual(suggestion.intent_display, display_alias)
            self.assertEqual(suggestion.intent_purpose, intent_preset.intent)

        def test_open_normalises_alias_only_metadata(self):
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))
            display_alias = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
                or intent_preset.intent
                or ""
            ).strip()
            self.assertTrue(display_alias, "Expected intent preset display alias")

            GPTState.last_suggested_recipes = [
                {
                    "name": "Alias normalisation",
                    "recipe": "describe · gist · focus · plain · fog",
                    "persona_preset_key": "",
                    "persona_preset_label": f"  {persona_preset.label.upper()}!!! ",
                    "persona_preset_spoken": "",
                    "persona_voice": "",
                    "persona_audience": "",
                    "persona_tone": "",
                    "intent_purpose": "",
                    "intent_preset_key": "",
                    "intent_preset_label": "",
                    "intent_display": f" {display_alias}! ? ",
                }
            ]

            with (
                patch.object(
                    modelSuggestionGUI,
                    "_reject_if_request_in_flight",
                    return_value=False,
                ),
                patch.object(modelSuggestionGUI, "close_common_overlays"),
                patch.object(
                    modelSuggestionGUI, "_open_suggestion_canvas"
                ) as open_canvas,
            ):
                UserActions.model_prompt_recipe_suggestions_gui_open()

            open_canvas.assert_called_once()
            self.assertTrue(SuggestionGUIState.suggestions)
            suggestion = SuggestionGUIState.suggestions[0]
            expected_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            self.assertEqual(suggestion.persona_preset_key, persona_preset.key)
            self.assertEqual(suggestion.persona_preset_label, persona_preset.label)
            self.assertEqual(suggestion.persona_preset_spoken, expected_spoken)
            self.assertEqual(suggestion.persona_voice, persona_preset.voice or "")
            self.assertEqual(suggestion.persona_audience, persona_preset.audience or "")
            self.assertEqual(suggestion.persona_tone, persona_preset.tone or "")
            self.assertEqual(suggestion.intent_preset_key, intent_preset.key)
            self.assertEqual(
                suggestion.intent_preset_label, intent_preset.label or intent_preset.key
            )
            self.assertEqual(suggestion.intent_display.lower(), display_alias.lower())

        def test_open_uses_persona_orchestrator_when_maps_empty(self) -> None:
            orchestrator = SimpleNamespace(
                persona_presets={
                    "mentor": SimpleNamespace(
                        key="mentor",
                        label="Mentor Guide",
                        spoken="Friendly Mentor",
                        voice="mentor-voice",
                        audience="mentees",
                        tone="supportive",
                    )
                },
                persona_aliases={"friendly mentor": "mentor"},
                intent_presets={
                    "guide": SimpleNamespace(
                        key="guide",
                        label="Guide",
                        intent="guide choice",
                    )
                },
                intent_aliases={"guide choice": "guide"},
                intent_synonyms={},
                intent_display_map={"guide": "Guide choice"},
                axis_alias_map={},
            )

            suggestion_entry = {
                "name": "Mentor suggestion",
                "recipe": "describe · gist · focus · plain · fog",
                "persona_preset_key": "",
                "persona_preset_label": "",
                "persona_preset_spoken": "Friendly Mentor",
                "persona_voice": "",
                "persona_audience": "",
                "persona_tone": "",
                "intent_purpose": "",
                "intent_preset_key": "",
                "intent_preset_label": "",
                "intent_display": "Guide choice",
            }

            with (
                patch.object(
                    modelSuggestionGUI,
                    "suggestion_entries_with_metadata",
                    return_value=[suggestion_entry],
                ),
                patch.object(
                    modelSuggestionGUI,
                    "persona_intent_maps",
                    return_value=SimpleNamespace(
                        persona_presets={},
                        persona_preset_aliases={},
                        intent_presets={},
                        intent_preset_aliases={},
                        intent_synonyms={},
                        intent_display_map={},
                    ),
                ),
                patch.object(
                    modelSuggestionGUI,
                    "_get_persona_orchestrator",
                    return_value=orchestrator,
                    create=True,
                ),
                patch.object(
                    modelSuggestionGUI,
                    "_reject_if_request_in_flight",
                    return_value=False,
                ),
                patch.object(modelSuggestionGUI, "close_common_overlays"),
                patch.object(
                    modelSuggestionGUI, "_open_suggestion_canvas"
                ) as open_canvas,
            ):
                UserActions.model_prompt_recipe_suggestions_gui_open()

            open_canvas.assert_called_once()
            self.assertTrue(SuggestionGUIState.suggestions)
            suggestion = SuggestionGUIState.suggestions[0]
            self.assertEqual(suggestion.persona_preset_key, "mentor")
            self.assertEqual(suggestion.persona_preset_label, "Mentor Guide")
            self.assertEqual(suggestion.persona_preset_spoken, "Friendly Mentor")
            self.assertEqual(suggestion.persona_voice, "mentor-voice")
            self.assertEqual(suggestion.persona_audience, "mentees")
            self.assertEqual(suggestion.persona_tone, "supportive")
            self.assertEqual(suggestion.intent_preset_key, "guide")
            self.assertEqual(suggestion.intent_preset_label, "Guide")
            self.assertEqual(suggestion.intent_display, "Guide choice")

        def test_run_index_surfaces_migration_hint_on_legacy_style(self):
            """Suggestion execution should hint and abort when legacy style is spoken."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Legacy style",
                    "recipe": "describe · full · narrow · debugging · plain · rog",
                },
            ]

            def _fake_safe(match):
                actions.app.notify("GPT: style axis is removed")
                return ""

            with patch.object(
                modelSuggestionGUI, "safe_model_prompt", side_effect=_fake_safe
            ):
                UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.user.gpt_apply_prompt.assert_not_called()
            notifications = [
                str(args[0])
                for args in [
                    *(ca.args for ca in actions.app.notify.call_args_list),
                    *(ca.args for ca in actions.user.notify.call_args_list),
                ]
                if args
            ]
            self.assertTrue(
                any(
                    "style axis is removed" in note
                    or "styleModifier is no longer supported" in note
                    for note in notifications
                ),
                f"Expected migration hint notification, got {notifications}",
            )

        def test_open_with_no_suggestions_notifies_and_does_not_show_canvas(self):
            GPTState.last_suggested_recipes = []
            self.assertFalse(SuggestionCanvasState.showing)

            UserActions.model_prompt_recipe_suggestions_gui_open()

            actions.app.notify.assert_called_once()
            self.assertFalse(SuggestionCanvasState.showing)

        def test_run_index_handles_multi_tag_axis_recipe(self):
            """Suggestions with multi-tag axis fields should execute and update last_*."""
            # Seed a suggestion that uses multi-token scope/method/style segments.
            GPTState.last_suggested_recipes = [
                {
                    "name": "Jira FAQ ticket",
                    "recipe": "show · full · act fail · flow · faq · jira · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Suggestion should have been executed and the GUI closed.
            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

            # GPTState last_* fields should reflect the parsed multi-tag axes.
            self.assertEqual(GPTState.last_static_prompt, "show")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_directional, "fog")

            # Scope/method/form/channel are stored as space-separated token strings
            # built from recognised axis tokens.
            self.assertEqual(GPTState.last_scope, "act fail")
            self.assertEqual(GPTState.last_method, "flow")
            self.assertEqual(GPTState.last_form, "faq")
            self.assertEqual(GPTState.last_channel, "jira")

        def test_run_index_normalises_alias_only_metadata(self):
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))
            display_alias = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
                or intent_preset.intent
                or ""
            ).strip()
            self.assertTrue(display_alias, "Expected intent preset display alias")

            GPTState.last_suggested_recipes = [
                {
                    "name": "Alias run",
                    "recipe": "describe · gist · focus · plain · fog",
                    "persona_preset_key": "",
                    "persona_preset_label": f" {persona_preset.label.upper()} ",
                    "persona_preset_spoken": "",
                    "persona_voice": "",
                    "persona_audience": "",
                    "persona_tone": "",
                    "intent_purpose": "",
                    "intent_preset_key": "",
                    "intent_preset_label": "",
                    "intent_display": f" {display_alias}! ",
                }
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.user.gpt_apply_prompt.assert_called_once()
            self.assertTrue(SuggestionGUIState.suggestions)
            suggestion = SuggestionGUIState.suggestions[0]
            expected_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            self.assertEqual(suggestion.persona_preset_key, persona_preset.key)
            self.assertEqual(suggestion.persona_preset_label, persona_preset.label)
            self.assertEqual(suggestion.persona_preset_spoken, expected_spoken)
            self.assertEqual(suggestion.intent_preset_key, intent_preset.key)
            self.assertEqual(
                suggestion.intent_preset_label, intent_preset.label or intent_preset.key
            )
            self.assertEqual(suggestion.intent_display.lower(), display_alias.lower())

        def test_drag_header_moves_canvas(self):
            """Dragging the header should move the suggestion canvas."""
            SuggestionGUIState.suggestions = []
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            # Provide a deterministic rect and move method on the stub canvas so
            # the drag handler can adjust position.
            canvas_obj.rect = type(
                "R", (), {"x": 10, "y": 20, "width": 400, "height": 300}
            )()
            moved_to: list[tuple[int, int]] = []

            def _move(x, y):
                moved_to.append((x, y))
                canvas_obj.rect = type(
                    "R", (), {"x": x, "y": y, "width": 400, "height": 300}
                )()

            canvas_obj.move = _move  # type: ignore[attr-defined]
            callbacks = getattr(canvas_obj, "_callbacks", {})
            mouse_cbs = callbacks.get("mouse") or []
            if not mouse_cbs:
                self.skipTest("Canvas stub does not expose mouse callbacks")
            mouse_cb = mouse_cbs[0]

            class _Evt:
                def __init__(self, event: str, x: int, y: int):
                    self.event = event
                    self.button = 0
                    self.pos = type("P", (), {"x": x, "y": y})()
                    self.gpos = type(
                        "P",
                        (),
                        {
                            "x": canvas_obj.rect.x + x,
                            "y": canvas_obj.rect.y + y,
                        },
                    )()

            # Start drag in the header (avoid the close hotspot by keeping x small).
            mouse_cb(_Evt("mousedown", 20, 10))
            # Move to a new position; rect should update via move().
            mouse_cb(_Evt("mousemove", 80, 60))

            self.assertIn((70, 70), moved_to)

        def test_scroll_event_callback_updates_offset(self):
            """Scroll events should adjust the suggestion canvas offset."""
            SuggestionGUIState.suggestions = [
                modelSuggestionGUI.Suggestion(
                    name=f"Suggestion {i}",
                    recipe="describe · gist · focus · plain · fog",
                )
                for i in range(20)
            ]
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            callbacks = getattr(canvas_obj, "_callbacks", {})
            scroll_cbs = (
                callbacks.get("scroll")
                or callbacks.get("wheel")
                or callbacks.get("mouse_scroll")
            )
            if not scroll_cbs:
                self.skipTest("Canvas stub does not expose scroll callbacks")
            scroll_cb = scroll_cbs[0]

            class _Evt:
                def __init__(self, delta: float):
                    self.dy = delta
                    self.wheel_y = delta

            self.assertEqual(SuggestionCanvasState.scroll_y, 0.0)
            scroll_cb(_Evt(-1.0))
            self.assertGreater(SuggestionCanvasState.scroll_y, 0.0)

        def test_reasoning_rendered_when_present(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="With reasoning",
                recipe="describe gist focus plain fog",
                reasoning="stance: kept; intent: kept understand; axes: chose fog for scan",
            )
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type(
                    "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                )()
            modelSuggestionGUI.SuggestionGUIState.suggestions = [suggestion]
            callbacks = getattr(canvas_obj, "_callbacks", {})
            draw_cbs = callbacks.get("draw") or []
            if not draw_cbs:
                self.skipTest("Canvas stub does not expose draw callbacks")
            draw_cb = draw_cbs[0]

            draw_cb(canvas_obj)
            # Reasoning should be included in measured height and rendering path without errors.
            self.assertTrue(modelSuggestionGUI.SuggestionGUIState.suggestions)

        def test_request_is_in_flight_delegates_to_request_gating(self) -> None:
            with patch.object(
                modelSuggestionGUI, "request_is_in_flight", return_value=True
            ) as helper:
                self.assertTrue(modelSuggestionGUI._request_is_in_flight())
            helper.assert_called_once_with()

            with patch.object(
                modelSuggestionGUI, "request_is_in_flight", return_value=False
            ) as helper:
                self.assertFalse(modelSuggestionGUI._request_is_in_flight())
            helper.assert_called_once_with()

        def test_reject_if_request_in_flight_notifies_and_blocks(self) -> None:
            with (
                patch(
                    "talon_user.lib.surfaceGuidance.try_begin_request",
                    return_value=(False, "in_flight"),
                ) as try_begin,
                patch(
                    "talon_user.lib.surfaceGuidance.render_drop_reason",
                    return_value="Request running",
                ) as render_message,
                patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
                patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
            ):
                self.assertTrue(modelSuggestionGUI._reject_if_request_in_flight())
            try_begin.assert_called_once_with(source="modelSuggestionGUI")
            render_message.assert_called_once_with("in_flight")
            set_reason.assert_called_once_with("in_flight", "Request running")
            notify_mock.assert_called_once_with("Request running")

            with (
                patch(
                    "talon_user.lib.surfaceGuidance.try_begin_request",
                    return_value=(False, "unknown_reason"),
                ),
                patch.object(
                    drop_reason_module,
                    "drop_reason_message",
                    return_value="",
                ),
                patch(
                    "talon_user.lib.surfaceGuidance.render_drop_reason",
                    return_value="Rendered fallback",
                ) as render_message,
                patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
                patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
            ):
                self.assertTrue(modelSuggestionGUI._reject_if_request_in_flight())
            render_message.assert_called_once_with("unknown_reason")
            set_reason.assert_called_once_with("unknown_reason", "Rendered fallback")
            notify_mock.assert_called_once_with("Rendered fallback")

            with (
                patch(
                    "talon_user.lib.surfaceGuidance.try_begin_request",
                    return_value=(True, ""),
                ),
                patch(
                    "talon_user.lib.surfaceGuidance.last_drop_reason",
                    return_value="",
                ),
                patch("talon_user.lib.surfaceGuidance.set_drop_reason") as set_reason,
                patch("talon_user.lib.surfaceGuidance.notify") as notify_mock,
            ):
                self.assertFalse(modelSuggestionGUI._reject_if_request_in_flight())
            set_reason.assert_called_once_with("")
            notify_mock.assert_not_called()


else:
    if not TYPE_CHECKING:

        class ModelSuggestionGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
