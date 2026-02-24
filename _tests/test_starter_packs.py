"""Specifying validation for ADR-0144 Phase 2: starter pack data.

Tests:
  SP1 — lib/starterPacks.py importable; STARTER_PACKS is a non-empty list of StarterPack
  SP2 — each StarterPack has name, framing, command (non-empty strings)
  SP3 — pack names are unique within STARTER_PACKS
  SP4 — pack names do not conflict with any token in the bar registry
  SP5 — prompt_grammar_payload() includes 'starter_packs' key with correct shape
  SP6 — pack command strings are valid bar build commands (start with 'bar build ')
"""
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.starterPacks import STARTER_PACKS, StarterPack
    from talon_user.lib.promptGrammar import prompt_grammar_payload
    from talon_user.lib.axisConfig import (
        AXIS_KEY_TO_VALUE,
        AXIS_KEY_TO_CATEGORY,
    )
    from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG

    def _all_token_names() -> set[str]:
        """All token values registered across every axis plus task tokens."""
        names: set[str] = set()
        for mapping in AXIS_KEY_TO_VALUE.values():
            names.update(mapping.keys())
        names.update(STATIC_PROMPT_CONFIG.keys())
        # Add axis names themselves
        names.update(["scope", "method", "form", "channel", "directional", "completeness",
                       "task", "persona", "voice", "audience", "tone", "intent"])
        return names

    class StarterPacksTests(unittest.TestCase):
        def test_SP1_starter_packs_importable_and_non_empty(self) -> None:
            self.assertIsInstance(STARTER_PACKS, list)
            self.assertGreater(len(STARTER_PACKS), 0)
            for pack in STARTER_PACKS:
                self.assertIsInstance(pack, StarterPack)

        def test_SP2_each_pack_has_required_fields(self) -> None:
            for pack in STARTER_PACKS:
                with self.subTest(pack=pack.name):
                    self.assertIsInstance(pack.name, str)
                    self.assertTrue(pack.name.strip(), "name must be non-empty")
                    self.assertIsInstance(pack.framing, str)
                    self.assertTrue(pack.framing.strip(), "framing must be non-empty")
                    self.assertIsInstance(pack.command, str)
                    self.assertTrue(pack.command.strip(), "command must be non-empty")

        def test_SP3_pack_names_are_unique(self) -> None:
            names = [p.name for p in STARTER_PACKS]
            self.assertEqual(len(names), len(set(names)), "pack names must be unique")

        def test_SP4_pack_names_do_not_conflict_with_tokens(self) -> None:
            token_names = _all_token_names()
            for pack in STARTER_PACKS:
                with self.subTest(pack=pack.name):
                    self.assertNotIn(
                        pack.name, token_names,
                        f"pack name '{pack.name}' conflicts with a registered token or axis name"
                    )

        def test_SP5_grammar_payload_includes_starter_packs(self) -> None:
            payload = prompt_grammar_payload()
            self.assertIn("starter_packs", payload)
            packs = payload["starter_packs"]
            self.assertIsInstance(packs, list)
            self.assertGreater(len(packs), 0)
            for item in packs:
                with self.subTest(item=item):
                    self.assertIn("name", item)
                    self.assertIn("framing", item)
                    self.assertIn("command", item)

        def test_SP6_pack_commands_start_with_bar_build(self) -> None:
            for pack in STARTER_PACKS:
                with self.subTest(pack=pack.name):
                    self.assertTrue(
                        pack.command.startswith("bar build "),
                        f"pack '{pack.name}' command must start with 'bar build ', got: {pack.command!r}"
                    )

else:
    if not TYPE_CHECKING:
        import unittest

        class StarterPacksTests(unittest.TestCase):  # type: ignore[no-redef]
            def test_skip_outside_talon(self) -> None:
                self.skipTest("bootstrap not available outside Talon runtime")
