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

    class GptAxisCatalogFallbackTests(unittest.TestCase):
        def test_axis_catalog_fallback_includes_axes(self):
            catalog = gpt.axis_catalog()
            self.assertIsInstance(catalog, dict)
            axes = catalog.get("axes", {})
            self.assertIsInstance(axes, dict)
            self.assertTrue(axes, "Expected fallback axis catalog to include axes")
else:
    if not TYPE_CHECKING:
        class GptAxisCatalogFallbackTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
