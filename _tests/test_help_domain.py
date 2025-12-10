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


else:
    if not TYPE_CHECKING:

        class HelpDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
