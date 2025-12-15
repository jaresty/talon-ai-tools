import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG, static_prompt_catalog

    class StaticPromptCatalogSkipListsTests(unittest.TestCase):
        def test_catalog_uses_ssot_when_list_missing(self) -> None:
            """Catalog should surface SSOT tokens even if staticPrompt.talon-list is absent."""

            catalog = static_prompt_catalog(static_prompt_list_path=None)
            profiled_names = {entry.get("name") for entry in catalog.get("profiled", [])}
            ssot_names = set(STATIC_PROMPT_CONFIG.keys())
            self.assertTrue(ssot_names, "Expected SSOT to contain static prompt keys")
            self.assertEqual(profiled_names, ssot_names)
            # Talon list tokens should include all SSOT names and no unprofiled tokens when list is missing.
            talon_tokens = set(catalog.get("talon_list_tokens", []))
            self.assertTrue(ssot_names.issubset(talon_tokens))
            self.assertFalse(catalog.get("unprofiled_tokens"), "Expected no unprofiled tokens when list is absent")

else:

    class StaticPromptCatalogSkipListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
