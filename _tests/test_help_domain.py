import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.helpDomain import (
        help_index,
        help_search,
        help_focusable_items,
        help_next_focus_label,
        help_activation_target,
        help_edit_filter_text,
    )
    from talon_user.lib.helpHub import HubButton
    from talon_user.lib.helpHub import build_search_index as hub_build_search_index

    class HelpDomainTests(unittest.TestCase):
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


else:
    if not TYPE_CHECKING:

        class HelpDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
