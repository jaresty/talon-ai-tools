import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from unittest.mock import patch
    from talon_user.lib.suggestionCoordinator import (
        last_suggestions,
        record_suggestions,
        suggestion_entries,
        suggestion_source,
        set_last_recipe_from_selection,
        suggestion_grammar_phrase,
        last_recipe_snapshot,
        last_recap_snapshot,
        suggestion_entries_with_metadata,
        suggestion_context,
        suggestion_skip_counts,
    )
    from talon_user.lib.modelState import GPTState

    class SuggestionCoordinatorTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()

        def test_record_and_fetch_suggestions(self) -> None:
            suggestions = [
                {
                    "name": "Fix bugs",
                    "recipe": "fix · full · narrow · steps · plain · fog",
                }
            ]
            record_suggestions(suggestions, "clipboard")

            stored, source = last_suggestions()
            self.assertEqual(source, "clipboard")
            self.assertEqual(stored, suggestions)

        def test_record_sanitises_none_source(self) -> None:
            record_suggestions([], None)
            stored, source = last_suggestions()
            self.assertEqual(stored, [])
            self.assertEqual(source, "")

        def test_suggestion_entries_filters_invalid(self) -> None:
            record_suggestions(
                [
                    {"name": "Valid", "recipe": "fix · full · fog"},
                    {"name": "", "recipe": "bad"},
                ],
                "clipboard",
            )
            entries = suggestion_entries()
            self.assertEqual(entries, [{"name": "Valid", "recipe": "fix · full · fog"}])

        def test_suggestion_entries_with_metadata_preserves_extra_fields(self) -> None:
            record_suggestions(
                [
                    {
                        "name": "With stance",
                        "recipe": "fix · full · fog",
                        "stance_command": "model write as teacher …",
                        "why": "Kind stance for junior devs",
                    },
                ],
                "clipboard",
            )
            entries = suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["name"], "With stance")
            self.assertEqual(entry["recipe"], "fix · full · fog")
            self.assertEqual(entry.get("stance_command"), "model write as teacher …")
            self.assertEqual(entry.get("why"), "Kind stance for junior devs")

        def test_suggestion_source_falls_back(self) -> None:
            record_suggestions([], None)
            self.assertEqual(suggestion_source("default"), "default")
            record_suggestions([], "clipboard")
            self.assertEqual(suggestion_source("default"), "clipboard")

        def test_set_last_recipe_from_selection_updates_state(self) -> None:
            set_last_recipe_from_selection(
                static_prompt="fix",
                completeness="full",
                scope="narrow focus",
                method=["steps", "rigor"],
                form="adr",
                channel="slack",
                directional="fog",
            )
            self.assertEqual(GPTState.last_static_prompt, "fix")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_scope, "narrow focus")
            self.assertEqual(GPTState.last_method, "steps rigor")
            self.assertEqual(GPTState.last_form, "adr")
            self.assertEqual(GPTState.last_channel, "slack")
            self.assertEqual(GPTState.last_directional, "fog")
            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["narrow", "focus"],
                    "method": ["steps", "rigor"],
                    "form": ["adr"],
                    "channel": ["slack"],
                    "directional": ["fog"],
                },
            )
            self.assertIn("fog", GPTState.last_recipe)

        def test_set_last_recipe_from_selection_caps_directional_to_single_token(
            self,
        ) -> None:
            set_last_recipe_from_selection(
                static_prompt="fix",
                completeness="full",
                scope="narrow focus",
                method=["steps", "rigor"],
                form="adr",
                channel="slack",
                directional="fog rog",
            )

            self.assertEqual(GPTState.last_directional, "rog")
            self.assertEqual(GPTState.last_axes.get("directional"), ["rog"])
            self.assertTrue(GPTState.last_recipe.endswith("rog"))

        def test_suggestion_grammar_phrase_uses_spoken_source(self) -> None:
            phrase = suggestion_grammar_phrase(
                "fix · full · fog", "clipboard", {"clipboard": "clip"}
            )
            self.assertEqual(phrase, "model run clip fix full fog")
            no_source_phrase = suggestion_grammar_phrase("fix · full · fog", None, {})
            self.assertEqual(no_source_phrase, "model run fix full fog")

        def test_last_recipe_snapshot_uses_axes_when_present(self) -> None:
            GPTState.last_static_prompt = "fix"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["narrow", "focus"],
                "method": ["steps"],
                "form": ["adr"],
                "channel": ["slack"],
            }
            GPTState.last_directional = "fog"
            snapshot = last_recipe_snapshot()
            self.assertEqual(snapshot["static_prompt"], "fix")
            self.assertEqual(snapshot["completeness"], "full")
            self.assertEqual(snapshot["scope_tokens"], ["narrow", "focus"])
            self.assertEqual(snapshot["method_tokens"], ["steps"])
            self.assertEqual(snapshot["form_tokens"], ["adr"])
            self.assertEqual(snapshot["channel_tokens"], ["slack"])
            self.assertEqual(snapshot["directional"], "fog")

        def test_last_recap_snapshot_includes_response_and_meta(self) -> None:
            GPTState.last_recipe = "fix · full"
            GPTState.last_response = "result text"
            GPTState.last_meta = "meta text"
            GPTState.last_directional = "fog"
            recap = last_recap_snapshot()
            self.assertEqual(recap["recipe"], "fix · full")
            self.assertEqual(recap["response"], "result text")
            self.assertEqual(recap["meta"], "meta text")
            self.assertEqual(recap["directional"], "fog")

        def test_record_suggestions_skips_recipes_without_directional(self) -> None:
            GPTState.last_suggested_recipes = []
            actions.user.calls.clear()

            record_suggestions(
                [{"name": "No dir", "recipe": "fix · full · bound · rigor"}], "clip"
            )

            self.assertEqual(GPTState.last_suggested_recipes, [])
            notifications = [c for c in actions.user.calls if c[0] == "notify"]
            self.assertTrue(
                any(
                    "directional" in str(args[0]).lower()
                    for _, args, _ in notifications
                )
            )

        def test_record_suggestions_hydrates_persona_and_intent_aliases(self) -> None:
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
            self.assertTrue(display_alias)

            record_suggestions(
                [
                    {
                        "name": "Hydrate aliases",
                        "recipe": "describe · gist · focus · plain · fog",
                        "persona_voice": persona_preset.voice or "",
                        "persona_audience": persona_preset.audience or "",
                        "persona_tone": persona_preset.tone or "",
                        "intent_purpose": intent_preset.intent,
                    }
                ],
                "clipboard",
            )

            entries = suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            expected_persona_label = persona_preset.label or persona_preset.key
            expected_persona_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            expected_intent_label = intent_preset.label or intent_preset.key

            self.assertEqual(entry.get("persona_preset_key"), persona_preset.key)
            self.assertEqual(entry.get("persona_preset_label"), expected_persona_label)
            self.assertEqual(
                entry.get("persona_preset_spoken"), expected_persona_spoken
            )
            self.assertEqual(entry.get("persona_voice"), persona_preset.voice or "")
            self.assertEqual(
                entry.get("persona_audience"), persona_preset.audience or ""
            )
            self.assertEqual(entry.get("persona_tone"), persona_preset.tone or "")
            self.assertEqual(entry.get("intent_preset_key"), intent_preset.key)
            self.assertEqual(entry.get("intent_preset_label"), expected_intent_label)
            self.assertEqual(entry.get("intent_purpose"), intent_preset.intent)
            self.assertEqual(entry.get("intent_display"), display_alias)

        def test_record_suggestions_tracks_skip_counts(self) -> None:
            record_suggestions(
                [
                    {"name": "No dir", "recipe": "describe · gist"},
                    {
                        "name": "Unknown persona",
                        "recipe": "describe · gist · focus · fog",
                        "persona_preset_key": "mystery_persona",
                    },
                    {
                        "name": "Unknown intent",
                        "recipe": "describe · gist · focus · fog",
                        "intent_preset_key": "mystery_intent",
                    },
                    {
                        "name": "Valid",
                        "recipe": "describe · gist · focus · fog",
                    },
                ],
                "clipboard",
            )

            counts = suggestion_skip_counts()
            self.assertEqual(counts.get("missing_directional"), 1)
            self.assertEqual(counts.get("unknown_persona"), 1)
            self.assertEqual(counts.get("unknown_intent"), 1)
            self.assertFalse(counts.get("unknown"))

            stored, _ = last_suggestions()
            self.assertEqual(len(stored), 1)
            self.assertEqual(stored[0]["name"], "Valid")

        def test_record_suggestions_accepts_axis_persona_without_preset(self) -> None:
            axis_map = {
                "voice": {"mentor": "mentor"},
                "audience": {"students": "students"},
                "tone": {"encouraging": "encouraging"},
            }

            with patch(
                "talon_user.lib.suggestionCoordinator.persona_intent_maps",
                return_value=SimpleNamespace(
                    persona_presets={},
                    persona_preset_aliases={},
                    intent_presets={},
                    intent_preset_aliases={},
                    intent_synonyms={},
                    intent_display_map={},
                    persona_axis_tokens=axis_map,
                ),
            ):
                record_suggestions(
                    [
                        {
                            "name": "Axis persona",
                            "recipe": "describe · gist · focus · fog",
                            "persona_voice": "mentor",
                            "persona_audience": "students",
                            "persona_tone": "encouraging",
                        }
                    ],
                    "clipboard",
                )

            counts = suggestion_skip_counts() or {}
            self.assertNotIn("unknown_persona", counts)

            entries = suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry.get("persona_voice"), "mentor")
            self.assertEqual(entry.get("persona_audience"), "students")
            self.assertEqual(entry.get("persona_tone"), "encouraging")

        def test_record_suggestions_notifies_skip_summary(self) -> None:
            with patch("talon_user.lib.suggestionCoordinator.notify") as notify_mock:
                record_suggestions(
                    [
                        {"name": "No dir", "recipe": "describe · gist"},
                        {
                            "name": "Unknown persona",
                            "recipe": "describe · gist · focus · fog",
                            "persona_preset_key": "mystery_persona",
                        },
                        {
                            "name": "Unknown intent",
                            "recipe": "describe · gist · focus · fog",
                            "intent_preset_key": "mystery_intent",
                        },
                        {
                            "name": "Valid",
                            "recipe": "describe · gist · focus · fog",
                        },
                    ],
                    "clipboard",
                )

            messages = [call.args[0] for call in notify_mock.call_args_list]
            summary = [msg for msg in messages if "Skipped" in msg]
            self.assertEqual(len(summary), 1)
            self.assertIn("missing_directional=1", summary[0])
            self.assertIn("unknown_persona=1", summary[0])
            self.assertIn("unknown_intent=1", summary[0])

        def test_suggestion_context_hydrates_aliases_from_state(self) -> None:
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))

            GPTState.last_suggest_context = {
                "persona_preset_key": persona_preset.key,
                "intent_purpose": intent_preset.intent,
            }

            hydrated = suggestion_context()

            expected_persona_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            expected_intent_display = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
            )

            self.assertEqual(
                hydrated.get("persona_preset_label"),
                persona_preset.label or persona_preset.key,
            )
            self.assertEqual(
                hydrated.get("persona_preset_spoken"), expected_persona_spoken
            )
            self.assertEqual(hydrated.get("persona_voice"), persona_preset.voice or "")
            self.assertEqual(
                hydrated.get("persona_audience"), persona_preset.audience or ""
            )
            self.assertEqual(hydrated.get("persona_tone"), persona_preset.tone or "")
            self.assertEqual(hydrated.get("intent_preset_key"), intent_preset.key)
            self.assertEqual(
                hydrated.get("intent_preset_label"),
                intent_preset.label or intent_preset.key,
            )
            self.assertEqual(hydrated.get("intent_display"), expected_intent_display)

            GPTState.last_suggest_context = {}
            hydrated_default = suggestion_context({"foo": "bar"})
            self.assertEqual(hydrated_default.get("foo"), "bar")

        def test_last_recipe_snapshot_includes_aliases_from_context(self) -> None:
            from talon_user.lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            persona_preset = next(iter(maps.persona_presets.values()))
            intent_preset = next(iter(maps.intent_presets.values()))

            GPTState.last_recipe = "describe · gist · fog"
            GPTState.last_axes = {
                "completeness": ["gist"],
                "scope": ["focus"],
                "method": ["plain"],
                "form": [],
                "channel": [],
                "directional": ["fog"],
            }
            GPTState.last_static_prompt = "describe"
            GPTState.last_suggest_context = {
                "persona_preset_key": persona_preset.key,
                "intent_purpose": intent_preset.intent,
            }

            snapshot = last_recipe_snapshot()

            expected_persona_spoken = (
                persona_preset.spoken or persona_preset.label or persona_preset.key
            )
            expected_intent_display = (
                maps.intent_display_map.get(intent_preset.key)
                or maps.intent_display_map.get(intent_preset.intent)
                or intent_preset.label
                or intent_preset.key
            )

            self.assertEqual(snapshot.get("persona_preset_key"), persona_preset.key)
            self.assertEqual(
                snapshot.get("persona_preset_label"),
                persona_preset.label or persona_preset.key,
            )
            self.assertEqual(
                snapshot.get("persona_preset_spoken"), expected_persona_spoken
            )
            self.assertEqual(snapshot.get("persona_voice"), persona_preset.voice or "")
            self.assertEqual(
                snapshot.get("persona_audience"), persona_preset.audience or ""
            )
            self.assertEqual(snapshot.get("persona_tone"), persona_preset.tone or "")
            self.assertEqual(snapshot.get("intent_preset_key"), intent_preset.key)
            self.assertEqual(
                snapshot.get("intent_preset_label"),
                intent_preset.label or intent_preset.key,
            )
            self.assertEqual(snapshot.get("intent_display"), expected_intent_display)
            self.assertEqual(snapshot.get("intent_purpose"), intent_preset.intent)

            GPTState.last_suggest_context = {}

        def test_suggestion_coordinator_uses_persona_orchestrator(self) -> None:
            import talon_user.lib.personaOrchestrator as persona_orchestrator
            import talon_user.lib.suggestionCoordinator as suggestion_module

            self.assertIs(
                getattr(suggestion_module, "_get_persona_orchestrator"),
                persona_orchestrator.get_persona_intent_orchestrator,
            )

        def test_record_suggestions_uses_persona_orchestrator(self) -> None:
            persona_preset = SimpleNamespace(
                key="mentor",
                label="Mentor",
                spoken="mentor spoken",
                voice="as teacher",
                audience="to programmer",
                tone="kindly",
            )
            intent_preset = SimpleNamespace(
                key="understand",
                label="Understand",
                intent="understand",
            )

            orchestrator = SimpleNamespace(
                persona_presets={"mentor": persona_preset},
                intent_presets={"understand": intent_preset},
                intent_display_map={"understand": "Understand display"},
                canonical_axis_token=lambda axis, alias: {
                    "voice": "as teacher",
                    "audience": "to programmer",
                    "tone": "kindly",
                }.get(axis, "" if not alias else alias),
                canonical_persona_key=lambda alias: "mentor" if alias else "",
                canonical_intent_key=lambda alias: "understand" if alias else "",
            )

            def fake_axis_tokens(axis: str) -> list[str]:
                mapping = {
                    "directional": ["fog"],
                    "voice": ["as teacher"],
                    "audience": ["to programmer"],
                    "tone": ["kindly"],
                }
                return mapping.get(axis, [])

            with (
                patch(
                    "talon_user.lib.suggestionCoordinator._get_persona_orchestrator",
                    return_value=orchestrator,
                ) as get_orchestrator,
                patch(
                    "talon_user.lib.suggestionCoordinator.persona_intent_maps",
                    side_effect=RuntimeError("maps unavailable"),
                ),
                patch(
                    "talon_user.lib.suggestionCoordinator.axis_registry_tokens",
                    side_effect=fake_axis_tokens,
                ),
            ):
                record_suggestions(
                    [
                        {
                            "name": "Needs canonicalisation",
                            "recipe": "describe · gist · fog",
                            "persona_voice": "voice alias",
                            "persona_audience": "audience alias",
                            "persona_tone": "tone alias",
                            "intent_display": "intent alias",
                        }
                    ],
                    "clipboard",
                )

            get_orchestrator.assert_called_once()
            stored, _ = last_suggestions()
            self.assertEqual(len(stored), 1)
            entry = stored[0]
            self.assertEqual(entry.get("persona_preset_key"), "mentor")
            self.assertEqual(entry.get("persona_voice"), "as teacher")
            self.assertEqual(entry.get("persona_audience"), "to programmer")
            self.assertEqual(entry.get("persona_tone"), "kindly")
            self.assertEqual(entry.get("intent_preset_key"), "understand")
            self.assertEqual(entry.get("intent_display"), "Understand display")


else:
    if not TYPE_CHECKING:

        class SuggestionCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
