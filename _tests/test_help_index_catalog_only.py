import unittest
from typing import TYPE_CHECKING, Any, List

if not TYPE_CHECKING:
    from talon_user.lib.helpDomain import help_index, HelpIndexEntry

    class HelpIndexCatalogOnlyTests(unittest.TestCase):
        def test_help_index_uses_catalog_tokens_when_lists_missing(self) -> None:
            """Guardrail: help index should use catalog tokens without requiring list files."""

            calls: List[str] = []

            def read_list_items(name: str) -> list[str]:
                calls.append(name)
                return []

            catalog = {
                "axes": {
                    "completeness": {"full": "Full", "gist": "Gist"},
                    "scope": {"narrow": "Narrow"},
                    "method": {"steps": "Steps"},
                    "form": {"bullets": "Bullets"},
                    "channel": {"slack": "Slack"},
                    "directional": {"fog": "Fog"},
                },
                "axis_list_tokens": {},  # Should fall back to axes tokens
                "static_prompts": {
                    "profiled": [
                        {"name": "describe", "description": "", "axes": {}},
                    ],
                    "talon_list_tokens": [],
                },
            }

            entries: list[HelpIndexEntry] = help_index(
                buttons=[],
                patterns=[],
                presets=[],
                read_list_items=read_list_items,
                catalog=catalog,
            )

            labels = {e.label for e in entries}
            # Static prompt from catalog
            self.assertIn("Prompt: describe", labels)
            # Axis tokens from catalog
            self.assertIn("Axis (Completeness): full", labels)
            self.assertIn("Axis (Completeness): gist", labels)
            self.assertIn("Axis (Scope): narrow", labels)
            self.assertIn("Axis (Method): steps", labels)
            self.assertIn("Axis (Form): bullets", labels)
            self.assertIn("Axis (Channel): slack", labels)
            self.assertIn("Axis (Directional): fog", labels)
            # Catalog path should not need to read list files.
            self.assertEqual(calls, [])

else:

    class HelpIndexCatalogOnlyTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
