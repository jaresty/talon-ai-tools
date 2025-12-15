import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    from talon_user.lib.staticPromptConfig import STATIC_PROMPT_CONFIG, static_prompt_catalog

    class StaticPromptCatalogMergeListsTests(unittest.TestCase):
        def test_static_prompt_catalog_merges_list_and_ssot(self) -> None:
            """Guardrail: static prompt list tokens merge list entries with SSOT tokens."""

            ssot_tokens = set(STATIC_PROMPT_CONFIG.keys())
            self.assertTrue(ssot_tokens, "Expected SSOT static prompt tokens")

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                list_path = tmp_path / "staticPrompt.talon-list"
                list_path.write_text(
                    "list: user.staticPrompt\n-\ninfer: infer\n", encoding="utf-8"
                )

                catalog = static_prompt_catalog(static_prompt_list_path=list_path)
                talon_tokens = set(catalog.get("talon_list_tokens", []))

                # List token should be present.
                self.assertIn("infer", talon_tokens)
                # All SSOT tokens should also be present even if missing from the list file.
                self.assertTrue(ssot_tokens.issubset(talon_tokens))

else:

    class StaticPromptCatalogMergeListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
