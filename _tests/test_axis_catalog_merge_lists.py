import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    from talon_user.lib.axisCatalog import axis_list_tokens
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    class AxisCatalogMergeListsTests(unittest.TestCase):
        def test_axis_list_tokens_merge_list_and_ssot(self) -> None:
            """Guardrail: list tokens should merge with SSOT tokens (lists can be partial)."""

            ssot_tokens = set((AXIS_KEY_TO_VALUE.get("completeness") or {}).keys())
            self.assertTrue(ssot_tokens, "Expected completeness SSOT tokens")

            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                lists_dir.mkdir(parents=True, exist_ok=True)
                list_path = lists_dir / "completenessModifier.talon-list"
                list_path.write_text(
                    "list: user.completenessModifier\n-\nfull: full\n", encoding="utf-8"
                )

                tokens = set(axis_list_tokens("completeness", lists_dir=lists_dir))
                # Must contain list token(s)
                self.assertIn("full", tokens)
                # Must also include SSOT tokens even if missing from list
                self.assertTrue(ssot_tokens.issubset(tokens))

else:

    class AxisCatalogMergeListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
