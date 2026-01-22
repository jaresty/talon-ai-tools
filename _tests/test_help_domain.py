import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    import talon_user.lib.helpDomain as help_domain_module
    import lib.helpDomain as help_domain_local

    from talon_user.lib.helpDomain import (
        help_index,
        help_search,
        help_focusable_items,
        help_next_focus_label,
        help_activation_target,
        help_edit_filter_text,
        help_metadata_snapshot,
        help_metadata_summary_lines,
        HelpMetadataSnapshot,
        HelpIntentMetadata,
        HelpPersonaMetadata,
    )
    from talon_user.lib.helpHub import HubButton
    from talon_user.lib.helpHub import build_search_index as hub_build_search_index

    class HelpDomainTests(unittest.TestCase):
        def test_help_index_uses_persona_orchestrator(self) -> None:
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
                persona_aliases={"mentor": "mentor"},
                intent_aliases={"understand": "understand"},
                intent_synonyms={"understand": "understand"},
                canonical_persona_key=lambda alias: "mentor" if alias else "",
                canonical_intent_key=lambda alias: "understand" if alias else "",
                canonical_axis_token=lambda axis, alias: {
                    "voice": "as teacher",
                    "audience": "to programmer",
                    "tone": "kindly",
                }.get(axis, alias),
            )

            def read_list_items(_: str):
                return []

            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.get_persona_intent_orchestrator",
                        return_value=orchestrator,
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.get_persona_intent_orchestrator",
                        return_value=orchestrator,
                    )
                )
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.persona_intent_maps",
                        side_effect=RuntimeError("maps unavailable"),
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.persona_intent_maps",
                        side_effect=RuntimeError("maps unavailable"),
                    )
                )
                entries = help_index([], [], [], read_list_items, catalog=None)

            labels = {entry.label for entry in entries}
            self.assertIn("Persona preset: Mentor (say: persona mentor spoken)", labels)
            self.assertIn(
                "Intent preset: Understand display (say: intent understand)", labels
            )

        def test_help_focusable_items_matches_help_hub_semantics(self) -> None:
            buttons = [
                HubButton(
                    label="Quick help",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
                HubButton(
                    label="Patterns",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
            ]
            results = [
                HubButton(
                    label="Hub: Quick help",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
            ]

            items = help_focusable_items("", buttons, results)
            self.assertEqual(
                items,
                [
                    ("btn", "Quick help"),
                    ("btn", "Patterns"),
                    ("res", "Hub: Quick help"),
                ],
            )

            # With a filter, only results should be focusable.
            items_filtered = help_focusable_items("quick", buttons, results)
            self.assertEqual(items_filtered, [("res", "Hub: Quick help")])

        def test_help_next_focus_label_delegates_to_navigation_core(self) -> None:
            items = [
                ("btn", "Quick help"),
                ("btn", "Patterns"),
                ("res", "Docs"),
            ]

            self.assertEqual(
                help_next_focus_label("", 1, items),
                "btn:Quick help",
            )
            self.assertEqual(
                help_next_focus_label("res:Docs", 1, items),
                "btn:Quick help",
            )
            self.assertEqual(
                help_next_focus_label("btn:Quick help", -1, items),
                "res:Docs",
            )

        def test_help_search_matches_label_substring_semantics(self) -> None:
            index = [
                HubButton(
                    label="Quick help",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
                HubButton(
                    label="Patterns",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
            ]

            # Empty or whitespace-only queries return no results.
            self.assertEqual(help_search("", index), [])
            self.assertEqual(help_search("   ", index), [])

            # Case-insensitive substring match on labels only.
            results = help_search("quick", index)
            self.assertEqual([item.label for item in results], ["Quick help"])

            results = help_search("PAT", index)
            self.assertEqual([item.label for item in results], ["Patterns"])

        def test_help_edit_filter_text_matches_help_hub_semantics(self) -> None:
            # Single-character backspace without modifiers removes one character.
            self.assertEqual(
                help_edit_filter_text("hello", "backspace", alt=False, cmd=False),
                "hell",
            )

            # Alt+backspace/delete trims the last word (or clears when only one).
            self.assertEqual(
                help_edit_filter_text(
                    "history drawer filter", "backspace", alt=True, cmd=False
                ),
                "history drawer",
            )
            self.assertEqual(
                help_edit_filter_text("single", "delete", alt=True, cmd=False),
                "",
            )

            # Cmd+backspace/delete clears the entire filter.
            self.assertEqual(
                help_edit_filter_text("some text", "backspace", alt=False, cmd=True),
                "",
            )
            self.assertEqual(
                help_edit_filter_text("some text", "delete", alt=False, cmd=True),
                "",
            )

            # Printable characters append to the filter.
            self.assertEqual(
                help_edit_filter_text("help", " ", alt=False, cmd=False),
                "help ",
            )
            self.assertEqual(
                help_edit_filter_text("help", "x", alt=False, cmd=False),
                "helpx",
            )

            # Non-editing keys leave the filter unchanged.
            self.assertEqual(
                help_edit_filter_text("help", "enter", alt=False, cmd=False),
                "help",
            )

        def test_help_activation_target_matches_help_hub_semantics(self) -> None:
            buttons = [
                HubButton(
                    label="Quick help",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
                HubButton(
                    label="Patterns",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
            ]
            results = [
                HubButton(
                    label="Hub: Quick help",
                    description="",
                    handler=lambda: None,
                    voice_hint="",
                ),
            ]

            # Button focus labels resolve to the correct button object.
            target = help_activation_target("btn:Quick help", buttons, results)
            self.assertIs(target, buttons[0])

            # Result focus labels resolve to the correct result object.
            target = help_activation_target("res:Hub: Quick help", buttons, results)
            self.assertIs(target, results[0])

            # Unknown labels return None.
            self.assertIsNone(
                help_activation_target("btn:Does not exist", buttons, results)
            )

            # Single-character backspace without modifiers removes one character.
            self.assertEqual(
                help_edit_filter_text("hello", "backspace", alt=False, cmd=False),
                "hell",
            )

            # Alt+backspace/delete trims the last word (or clears when only one).
            self.assertEqual(
                help_edit_filter_text(
                    "history drawer filter", "backspace", alt=True, cmd=False
                ),
                "history drawer",
            )
            self.assertEqual(
                help_edit_filter_text("single", "delete", alt=True, cmd=False),
                "",
            )

            # Cmd+backspace/delete clears the entire filter.
            self.assertEqual(
                help_edit_filter_text("some text", "backspace", alt=False, cmd=True),
                "",
            )
            self.assertEqual(
                help_edit_filter_text("some text", "delete", alt=False, cmd=True),
                "",
            )

            # Printable characters append to the filter.
            self.assertEqual(
                help_edit_filter_text("help", " ", alt=False, cmd=False),
                "help ",
            )
            self.assertEqual(
                help_edit_filter_text("help", "x", alt=False, cmd=False),
                "helpx",
            )

            # Non-editing keys leave the filter unchanged.
            self.assertEqual(
                help_edit_filter_text("help", "enter", alt=False, cmd=False),
                "help",
            )

        def test_help_index_matches_help_hub_build_search_index(self) -> None:
            buttons = [
                HubButton(
                    label="Quick help",
                    description="Open quick help",
                    handler=lambda: None,
                    voice_hint="Say: model quick help",
                )
            ]

            def fake_read_list_items(name: str) -> list[str]:
                if name == "staticPrompt.talon-list":
                    return ["todo"]
                if name == "completenessModifier.talon-list":
                    return ["full"]
                return []

            index_via_help_domain = help_index(
                buttons,
                patterns=[],
                presets=[],
                read_list_items=fake_read_list_items,
            )
            index_via_help_hub = hub_build_search_index(
                buttons,
                patterns=[],
                presets=[],
                read_list_items=fake_read_list_items,
            )

            self.assertEqual(
                [b.label for b in index_via_help_domain],
                [b.label for b in index_via_help_hub],
            )

        def test_help_index_prefers_catalog_tokens(self) -> None:
            """Catalog-provided vocab should be used even if list files are empty."""

            buttons = [
                HubButton(
                    label="Quick help",
                    description="Open quick help",
                    handler=lambda: None,
                    voice_hint="Say: model quick help",
                )
            ]

            catalog = {
                "static_prompts": {
                    "profiled": [{"name": "catalog_static"}],
                    "talon_list_tokens": ["catalog_static"],
                },
                "axes": {
                    "scope": {"focus": "desc"},
                },
                "axis_list_tokens": {
                    "scope": ["focus"],
                },
            }

            def empty_read_list_items(_name: str) -> list[str]:
                return []

            index = help_index(
                buttons,
                patterns=[],
                presets=[],
                read_list_items=empty_read_list_items,
                catalog=catalog,
            )

            labels = {entry.label for entry in index}
            self.assertIn("Prompt: catalog_static", labels)
            self.assertIn("Axis (Scope): focus", labels)

        def test_help_index_persona_intent_entries_use_snapshot_aliases(self) -> None:
            """Persona/intent entries should mirror snapshot-backed alias metadata."""
            from lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)

            index = help_index(
                [],
                patterns=[],
                presets=[],
                read_list_items=lambda _name: [],
                catalog={},
            )

            persona_entries = [
                entry for entry in index if entry.label.startswith("Persona preset: ")
            ]
            self.assertTrue(persona_entries, "Persona presets missing from help index")

            for key, preset in maps.persona_presets.items():
                label = (getattr(preset, "label", "") or key).strip()
                entry = next(
                    (
                        e
                        for e in persona_entries
                        if e.label.startswith(f"Persona preset: {label}")
                    ),
                    None,
                )
                self.assertIsNotNone(entry, f"Persona preset entry missing for {key}")
                spoken = (getattr(preset, "spoken", "") or "").strip()
                if not spoken:
                    spoken = label or key
                spoken_alias = spoken.strip()
                self.assertIn(
                    f"(say: persona {spoken_alias}".lower(), entry.label.lower()
                )
                self.assertEqual(entry.voice_hint, f"Say: persona {spoken_alias}")
                axes_parts = [
                    (getattr(preset, attr, "") or "").strip()
                    for attr in ("voice", "audience", "tone")
                ]
                axes_parts = [part for part in axes_parts if part]
                if axes_parts:
                    for token in axes_parts:
                        self.assertIn(token, entry.description)
                else:
                    self.assertIn("No explicit axes", entry.description)

            intent_entries = [
                entry for entry in index if entry.label.startswith("Intent preset: ")
            ]
            self.assertTrue(intent_entries, "Intent presets missing from help index")

            for key, preset in maps.intent_presets.items():
                display = (
                    maps.intent_display_map.get(key)
                    or getattr(preset, "label", "")
                    or key
                ).strip()
                entry = next(
                    (
                        e
                        for e in intent_entries
                        if e.label.startswith(f"Intent preset: {display}")
                    ),
                    None,
                )
                self.assertIsNotNone(entry, f"Intent preset entry missing for {key}")
                spoken_alias = next(
                    (
                        alias
                        for alias, canonical in maps.intent_preset_aliases.items()
                        if canonical == key and alias != key.lower()
                    ),
                    "",
                )
                if not spoken_alias:
                    spoken_alias = display or getattr(preset, "intent", "") or key
                self.assertIn(
                    f"(say: intent {spoken_alias}".lower(), entry.label.lower()
                )
                self.assertEqual(entry.voice_hint, f"Say: intent {spoken_alias}")
                canonical_intent = (getattr(preset, "intent", "") or key).strip()
                if canonical_intent:
                    self.assertIn(canonical_intent, entry.description)

        def test_help_index_persona_entries_include_metadata(self) -> None:
            from lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            index = help_index(
                [],
                patterns=[],
                presets=[],
                read_list_items=lambda _name: [],
                catalog={},
            )

            persona_entries = {
                (entry.metadata or {}).get("persona_key"): entry
                for entry in index
                if entry.label.startswith("Persona preset: ")
            }
            self.assertTrue(persona_entries, "Persona metadata missing from help index")

            for key in maps.persona_presets.keys():
                entry = persona_entries.get(key)
                self.assertIsNotNone(
                    entry, f"Missing help index entry for persona {key}"
                )
                metadata = entry.metadata or {}
                self.assertEqual(metadata.get("kind"), "persona")
                self.assertEqual(metadata.get("persona_key"), key)
                axes_summary = metadata.get("axes_summary", "")
                self.assertTrue(axes_summary, f"Missing axes summary for persona {key}")
                axes_tokens = metadata.get("axes_tokens", []) or []
                self.assertTrue(
                    all(str(token or "").strip() for token in axes_tokens),
                    f"Axes tokens missing for persona {key}",
                )
                voice_hint = (entry.voice_hint or "").lower()
                if "say: persona" in voice_hint:
                    hinted_alias = voice_hint.split("say: persona", 1)[1].strip()
                    self.assertEqual(
                        metadata.get("spoken_alias"),
                        hinted_alias,
                        f"Persona metadata mismatch for {key}",
                    )
                self.assertTrue(
                    metadata.get("spoken_alias"),
                    f"Spoken alias missing for persona {key}",
                )

            intent_entries = {
                (entry.metadata or {}).get("intent_key"): entry
                for entry in index
                if entry.label.startswith("Intent preset: ")
            }
            self.assertTrue(intent_entries, "Intent metadata missing from help index")

            for key in maps.intent_presets.keys():
                entry = intent_entries.get(key)
                self.assertIsNotNone(
                    entry, f"Missing help index entry for intent {key}"
                )
                metadata = entry.metadata or {}
                self.assertEqual(metadata.get("kind"), "intent")
                self.assertEqual(metadata.get("intent_key"), key)
                canonical_intent = metadata.get("canonical_intent", "")
                self.assertTrue(
                    canonical_intent,
                    f"Canonical intent missing for {key}",
                )
                display_value = metadata.get("display_label", "").strip()
                self.assertTrue(
                    display_value, f"Display label missing for intent {key}"
                )
                voice_hint = (entry.voice_hint or "").lower()
                if "say: intent" in voice_hint:
                    hinted_alias = voice_hint.split("say: intent", 1)[1].strip()
                    self.assertEqual(
                        metadata.get("spoken_alias"),
                        hinted_alias,
                        f"Intent metadata mismatch for {key}",
                    )
                self.assertTrue(
                    metadata.get("spoken_alias"),
                    f"Spoken alias missing for intent {key}",
                )

        def test_help_index_catalog_fallback_without_maps(self) -> None:
            catalog_persona = SimpleNamespace(
                key="mentor",
                label="Catalog Mentor",
                spoken="catalog mentor",
                voice="Catalog Voice",
                audience="Catalog Audience",
                tone="Catalog Tone",
            )
            catalog_intent = SimpleNamespace(
                key="decide",
                label="Catalog Plan",
                intent="plan",
                spoken="catalog plan alias",
            )
            catalog_snapshot = SimpleNamespace(
                persona_presets={"mentor": catalog_persona},
                persona_spoken_map={"catalog mentor": "mentor"},
                persona_axis_tokens={
                    "voice": ["Catalog Voice"],
                    "audience": ["Catalog Audience"],
                    "tone": ["Catalog Tone"],
                },
                intent_presets={"decide": catalog_intent},
                intent_spoken_map={"catalog plan alias": "decide"},
                intent_axis_tokens={"intent": ["decide"]},
                intent_buckets={"assist": ["decide"]},
                intent_display_map={"decide": "Catalog Plan Display"},
            )

            legacy_persona = SimpleNamespace(
                key="mentor",
                label="Legacy Mentor",
                spoken="legacy mentor",
                voice="Legacy Voice",
                audience="Legacy Audience",
                tone="Legacy Tone",
            )
            legacy_intent = SimpleNamespace(
                key="decide",
                label="Legacy Plan",
                intent="legacy-plan",
                spoken="legacy plan alias",
            )
            legacy_maps = SimpleNamespace(
                persona_presets={"mentor": legacy_persona},
                persona_preset_aliases={"legacy mentor": "mentor"},
                persona_axis_tokens={
                    "voice": {"legacy voice": "Legacy Voice"},
                    "audience": {"legacy audience": "Legacy Audience"},
                    "tone": {"legacy tone": "Legacy Tone"},
                },
                intent_presets={"decide": legacy_intent},
                intent_preset_aliases={"legacy plan alias": "decide"},
                intent_synonyms={"legacy plan alias": "decide"},
                intent_display_map={"decide": "Legacy Plan Display"},
            )

            def empty_read_list_items(_name: str) -> list[str]:
                return []

            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.get_persona_intent_orchestrator",
                        side_effect=RuntimeError("orchestrator unavailable"),
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.get_persona_intent_orchestrator",
                        side_effect=RuntimeError("orchestrator unavailable"),
                    )
                )
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.personaCatalog",
                        SimpleNamespace(
                            get_persona_intent_catalog=lambda: catalog_snapshot
                        ),
                        create=True,
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.personaCatalog",
                        SimpleNamespace(
                            get_persona_intent_catalog=lambda: catalog_snapshot
                        ),
                        create=True,
                    )
                )
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.persona_intent_maps",
                        return_value=legacy_maps,
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.persona_intent_maps",
                        return_value=legacy_maps,
                    )
                )
                index = help_index(
                    [],
                    patterns=[],
                    presets=[],
                    read_list_items=empty_read_list_items,
                    catalog={},
                )

            persona_entry = next(
                entry for entry in index if entry.label.startswith("Persona preset: ")
            )
            self.assertIn("Catalog Mentor", persona_entry.label)
            self.assertNotIn("Legacy Mentor", persona_entry.label)
            persona_metadata = persona_entry.metadata or {}
            axes_summary = persona_metadata.get("axes_summary", "")
            self.assertIn("Catalog Voice", axes_summary)
            self.assertNotIn("Legacy Voice", axes_summary)

            intent_entry = next(
                entry for entry in index if entry.label.startswith("Intent preset: ")
            )
            self.assertIn("Catalog Plan Display", intent_entry.label)
            self.assertNotIn("Legacy Plan Display", intent_entry.label)
            intent_metadata = intent_entry.metadata or {}
            self.assertEqual(intent_metadata.get("canonical_intent"), "plan")
            self.assertNotIn("legacy-plan", intent_entry.label.lower())

        def test_help_metadata_snapshot_aggregates_index_metadata(self) -> None:
            from lib.personaConfig import persona_intent_maps

            maps = persona_intent_maps(force_refresh=True)
            index = help_index(
                [],
                patterns=[],
                presets=[],
                read_list_items=lambda _name: [],
                catalog={},
            )

            with ExitStack() as stack:
                if hasattr(help_domain_local, "time"):
                    stack.enter_context(
                        patch.object(
                            help_domain_local.time,
                            "strftime",
                            lambda fmt, ts=None: "2025-12-25T17:00:00Z",
                        )
                    )
                if hasattr(help_domain_module, "time"):
                    stack.enter_context(
                        patch.object(
                            help_domain_module.time,
                            "strftime",
                            lambda fmt, ts=None: "2025-12-25T17:00:00Z",
                        )
                    )
                snapshot = help_metadata_snapshot(index)

            persona_keys = {persona.key for persona in snapshot.personas}
            intent_keys = {intent.key for intent in snapshot.intents}

            expected_persona_keys = {
                str(key or "").strip() for key in maps.persona_presets.keys()
            }
            expected_intent_keys = {
                str(key or "").strip() for key in maps.intent_presets.keys()
            }

            self.assertTrue(
                persona_keys.issuperset(expected_persona_keys),
                "Metadata snapshot missing persona entries",
            )
            self.assertTrue(
                intent_keys.issuperset(expected_intent_keys),
                "Metadata snapshot missing intent entries",
            )

            self.assertTrue(all(persona.spoken_alias for persona in snapshot.personas))
            self.assertTrue(all(persona.axes_summary for persona in snapshot.personas))
            self.assertTrue(all(intent.spoken_alias for intent in snapshot.intents))
            self.assertTrue(all(intent.canonical_intent for intent in snapshot.intents))

            summary_lines = help_domain_local.help_metadata_summary_lines(snapshot)
            self.assertIn(
                "Metadata schema version: help-hub.metadata.v1",
                summary_lines,
            )
            self.assertTrue(
                any(
                    "metadata generated at (utc): 2025-12-25t17:00:00z" in line.lower()
                    for line in summary_lines
                ),
                "Generated-at header missing from summary lines",
            )

        def test_help_metadata_snapshot_catalog_fallback_without_maps(self) -> None:
            catalog_persona = SimpleNamespace(
                key="mentor",
                label="Catalog Mentor",
                spoken="catalog mentor",
                voice="Catalog Voice",
                audience="Catalog Audience",
                tone="Catalog Tone",
            )
            catalog_intent = SimpleNamespace(
                key="decide",
                label="Catalog Plan",
                intent="plan",
                spoken="catalog plan alias",
            )
            catalog_snapshot = SimpleNamespace(
                persona_presets={"mentor": catalog_persona},
                persona_spoken_map={"catalog mentor": "mentor"},
                persona_axis_tokens={
                    "voice": ["Catalog Voice"],
                    "audience": ["Catalog Audience"],
                    "tone": ["Catalog Tone"],
                },
                intent_presets={"decide": catalog_intent},
                intent_spoken_map={"catalog plan alias": "decide"},
                intent_axis_tokens={"intent": ["decide"]},
                intent_buckets={"assist": ["decide"]},
                intent_display_map={"decide": "Catalog Plan Display"},
            )
            legacy_persona = SimpleNamespace(
                key="mentor",
                label="Legacy Mentor",
                spoken="legacy mentor",
                voice="Legacy Voice",
                audience="Legacy Audience",
                tone="Legacy Tone",
            )
            legacy_intent = SimpleNamespace(
                key="decide",
                label="Legacy Plan",
                intent="legacy-plan",
                spoken="legacy plan alias",
            )
            legacy_maps = SimpleNamespace(
                persona_presets={"mentor": legacy_persona},
                persona_preset_aliases={"legacy mentor": "mentor"},
                persona_axis_tokens={
                    "voice": {"legacy voice": "Legacy Voice"},
                    "audience": {"legacy audience": "Legacy Audience"},
                    "tone": {"legacy tone": "Legacy Tone"},
                },
                intent_presets={"decide": legacy_intent},
                intent_preset_aliases={"legacy plan alias": "decide"},
                intent_synonyms={"legacy plan alias": "decide"},
                intent_display_map={"decide": "Legacy Plan Display"},
            )

            with ExitStack() as stack:
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.get_persona_intent_orchestrator",
                        side_effect=RuntimeError("orchestrator unavailable"),
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.get_persona_intent_orchestrator",
                        side_effect=RuntimeError("orchestrator unavailable"),
                    )
                )
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.personaCatalog",
                        SimpleNamespace(
                            get_persona_intent_catalog=lambda: catalog_snapshot
                        ),
                        create=True,
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.personaCatalog",
                        SimpleNamespace(
                            get_persona_intent_catalog=lambda: catalog_snapshot
                        ),
                        create=True,
                    )
                )
                stack.enter_context(
                    patch(
                        "talon_user.lib.helpDomain.persona_intent_maps",
                        return_value=legacy_maps,
                    )
                )
                stack.enter_context(
                    patch(
                        "lib.helpDomain.persona_intent_maps",
                        return_value=legacy_maps,
                    )
                )
                snapshot = help_metadata_snapshot([])

            lines = help_metadata_summary_lines(snapshot)
            persona_line = next(
                line for line in lines if line.startswith("- persona mentor")
            )
            self.assertIn("Catalog Mentor", persona_line)
            self.assertNotIn("Legacy Mentor", persona_line)
            intent_line = next(
                line for line in lines if line.startswith("- intent plan")
            )
            self.assertIn("Catalog Plan Display", intent_line)
            self.assertNotIn("Legacy Plan Display", intent_line)

        def test_help_metadata_summary_lines_respects_headers(self) -> None:
            snapshot = HelpMetadataSnapshot(
                personas=(),
                intents=(),
                schema_version="help-hub.metadata.test",
                generated_at="2025-12-25T19:00:00Z",
                provenance=(
                    ("source", "lib.helpDomain.test"),
                    ("adr", "ADR-0062-test"),
                ),
                headers=("Metadata header sentinel",),
            )

            lines = help_domain_local.help_metadata_summary_lines(snapshot)
            self.assertIn("Metadata header sentinel", lines)

        def test_help_metadata_summary_lines_sorts_entries(self) -> None:
            snapshot = HelpMetadataSnapshot(
                personas=(
                    HelpPersonaMetadata(
                        key="mentor",
                        display_label="Echo Mentor",
                        spoken_display="Echo Mentor",
                        spoken_alias="echo",
                        axes_summary="Echo Axes",
                        axes_tokens=("echo",),
                        voice_hint="Say: persona echo",
                    ),
                    HelpPersonaMetadata(
                        key="analyst",
                        display_label="Alpha Analyst",
                        spoken_display="Alpha Analyst",
                        spoken_alias="alpha",
                        axes_summary="Alpha Axes",
                        axes_tokens=("alpha",),
                        voice_hint="Say: persona alpha",
                    ),
                ),
                intents=(
                    HelpIntentMetadata(
                        key="decide",
                        display_label="Zeta Plan",
                        canonical_intent="plan",
                        spoken_display="Zeta Plan",
                        spoken_alias="zeta plan",
                        voice_hint="Say: intent zeta plan",
                    ),
                    HelpIntentMetadata(
                        key="decide",
                        display_label="Beta Decide",
                        canonical_intent="decide",
                        spoken_display="Beta Decide",
                        spoken_alias="beta decide",
                        voice_hint="Say: intent beta decide",
                    ),
                ),
                headers=(),
            )

            lines = help_domain_local.help_metadata_summary_lines(snapshot)

            persona_lines = [line for line in lines if line.startswith("- persona ")]
            self.assertEqual(
                [
                    "- persona analyst (say: persona alpha): Alpha Analyst (Alpha Axes)",
                    "- persona mentor (say: persona echo): Echo Mentor (Echo Axes)",
                ],
                persona_lines,
            )

            intent_lines = [line for line in lines if line.startswith("- intent ")]
            self.assertEqual(
                [
                    "- intent decide (say: intent beta decide): Beta Decide (decide)",
                    "- intent plan (say: intent zeta plan): Zeta Plan (plan)",
                ],
                intent_lines,
            )


else:
    if not TYPE_CHECKING:

        class HelpDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
