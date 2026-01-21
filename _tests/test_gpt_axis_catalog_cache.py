"""Tests for GPT axis_catalog caching per ADR 0082."""

import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import importlib
    gpt = importlib.import_module("talon_user.GPT.gpt")

    class GptAxisCatalogCacheTests(unittest.TestCase):
        """Validate axis_catalog caching prevents repeated allocations (ADR 0082 Phase 3)."""

        def setUp(self):
            """Clear cache before each test."""
            gpt.invalidate_help_axis_catalog()

        def test_axis_catalog_returns_same_object_on_repeated_calls(self):
            """First call populates cache, subsequent calls return same object."""
            catalog1 = gpt.axis_catalog()
            catalog2 = gpt.axis_catalog()

            self.assertIsInstance(catalog1, dict)
            self.assertIsInstance(catalog2, dict)
            self.assertIs(catalog1, catalog2, "Expected axis_catalog() to return cached object")

        def test_axis_catalog_cache_includes_expected_keys(self):
            """Cached catalog should have axes, axis_list_tokens, static_prompts."""
            catalog = gpt.axis_catalog()

            self.assertIn("axes", catalog)
            self.assertIn("axis_list_tokens", catalog)
            self.assertIn("static_prompts", catalog)
            self.assertIn("static_prompt_descriptions", catalog)
            self.assertIn("static_prompt_profiles", catalog)

        def test_invalidate_help_axis_catalog_clears_cache(self):
            """Invalidation forces reload on next call."""
            catalog1 = gpt.axis_catalog()
            self.assertIsInstance(catalog1, dict)

            gpt.invalidate_help_axis_catalog()
            catalog2 = gpt.axis_catalog()

            self.assertIsInstance(catalog2, dict)
            self.assertIsNot(catalog1, catalog2, "Expected new object after invalidation")

        def test_multiple_calls_without_invalidation_reuse_cache(self):
            """Many calls should return same cached object without repeated allocations."""
            first = gpt.axis_catalog()

            for _ in range(10):
                current = gpt.axis_catalog()
                self.assertIs(first, current, "Expected cache reuse across multiple calls")

else:
    if not TYPE_CHECKING:
        class GptAxisCatalogCacheTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
