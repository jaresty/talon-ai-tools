import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    from talon_user.lib.axisCatalog import axis_list_tokens
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE

    class AxisCatalogSkipListsTests(unittest.TestCase):
        def test_axis_list_tokens_catalog_only_when_no_lists_dir(self) -> None:
            """Catalog-only path should skip on-disk lists and return SSOT tokens."""

            catalog_tokens = set((AXIS_KEY_TO_VALUE.get("completeness") or {}).keys())
            result_tokens = set(axis_list_tokens("completeness", lists_dir=None))
            self.assertEqual(catalog_tokens, result_tokens)

        def test_axis_list_tokens_catalog_only_when_lists_dir_empty(self) -> None:
            """Catalog-only path should also skip when lists_dir is falsy/empty."""

            catalog_tokens = set((AXIS_KEY_TO_VALUE.get("completeness") or {}).keys())
            result_tokens = set(axis_list_tokens("completeness", lists_dir=""))
            self.assertEqual(catalog_tokens, result_tokens)

else:

    class AxisCatalogSkipListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
