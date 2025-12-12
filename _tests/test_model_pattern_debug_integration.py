import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import modelPatternGUI

    class _DummyPattern:
        def __init__(self, name, description, recipe, domain="coding", axes=None):
            self.name = name
            self.description = description
            self.recipe = recipe
            self.domain = domain
            self.axes = axes or {}

    class ModelPatternDebugIntegrationTests(unittest.TestCase):
        def setUp(self) -> None:
            self._orig_patterns = modelPatternGUI.PATTERNS

        def tearDown(self) -> None:
            modelPatternGUI.PATTERNS = self._orig_patterns

        def test_pattern_debug_catalog_uses_coordinator_views(self) -> None:
            modelPatternGUI.PATTERNS = [
                _DummyPattern("pat1", "desc1", "infer · full · focus"),
                _DummyPattern("pat2", "desc2", "infer · full · rigor", axes={"method": ["rigor"]}),
            ]

            catalog = modelPatternGUI.pattern_debug_catalog()
            names = {entry.get("name") for entry in catalog}
            self.assertEqual(names, {"pat1", "pat2"})
            axes = {entry.get("name"): entry.get("axes") for entry in catalog}
            self.assertEqual(axes["pat2"]["method"], ["rigor"])

        def test_pattern_debug_catalog_filters_by_domain(self) -> None:
            modelPatternGUI.PATTERNS = [
                _DummyPattern("pat1", "desc1", "infer · full", domain="coding"),
                _DummyPattern("pat2", "desc2", "infer · full", domain="writing"),
            ]

            coding = modelPatternGUI.pattern_debug_catalog(domain="coding")
            names = {entry.get("name") for entry in coding}
            self.assertEqual(names, {"pat1"})

else:
    if not TYPE_CHECKING:

        class ModelPatternDebugIntegrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
