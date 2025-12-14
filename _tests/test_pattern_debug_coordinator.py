import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.patternDebugCoordinator import (
        pattern_debug_snapshot,
        pattern_debug_view,
        pattern_debug_catalog,
    )

    class _DummyPattern:
        def __init__(self, name, description, recipe, domain="coding", axes=None):
            self.name = name
            self.description = description
            self.recipe = recipe
            self.domain = domain
            self.axes = axes or {}

    class PatternDebugCoordinatorTests(unittest.TestCase):
        def test_pattern_debug_snapshot_parses_recipe_axes(self) -> None:
            patterns = [
                _DummyPattern("pat1", "desc1", "infer · full · focus · rigor · fog"),
            ]

            snap = pattern_debug_snapshot("pat1", patterns=patterns)

            self.assertEqual(snap["name"], "pat1")
            self.assertEqual(snap["description"], "desc1")
            self.assertEqual(snap["static_prompt"], "infer")
            self.assertEqual(snap["axes"]["completeness"], "full")
            self.assertEqual(snap["axes"]["scope"], ["focus"])
            self.assertEqual(snap["axes"]["method"], ["rigor"])
            self.assertEqual(snap["axes"]["directional"], "fog")

        def test_pattern_debug_view_prefers_axes_attr(self) -> None:
            patterns = [
                _DummyPattern(
                    "pat2",
                    "desc2",
                    "infer · full · focus · steps · fog",
                    axes={"method": ["rigor"]},
                ),
            ]
            view = pattern_debug_view("pat2", patterns=patterns)
            self.assertEqual(view["name"], "pat2")
            self.assertEqual(view["description"], "desc2")
            self.assertEqual(view.get("recipe_line"), "infer · full · focus · steps · fog")
            self.assertEqual(
                view.get("axes"),
                {
                    "completeness": "full",
                    "scope": ["focus"],
                    "method": ["rigor"],
                    "form": [],
                    "channel": [],
                    "directional": "fog",
                },
            )

        def test_pattern_debug_catalog_filters_by_domain(self) -> None:
            patterns = [
                _DummyPattern("pat1", "desc1", "infer · full · focus · fog", domain="coding"),
                _DummyPattern("pat2", "desc2", "infer · full · focus · rog", domain="writing"),
            ]
            catalog = pattern_debug_catalog(patterns=patterns, domain="coding")
            names = {entry.get("name") for entry in catalog}
            self.assertEqual(names, {"pat1"})

        def test_pattern_debug_canonicalises_axes(self) -> None:
            patterns = [
                _DummyPattern(
                    "pat3",
                    "desc3",
                    "infer · full · actions edges system · steps plan rigor filter · bullets table · slack jira · rog fog",
                ),
            ]

            snap = pattern_debug_snapshot("pat3", patterns=patterns)
            axes = snap["axes"]

            self.assertEqual(axes["completeness"], "full")
            # Scope/method capped and canonicalised.
            self.assertEqual(axes["scope"], ["edges", "system"])
            self.assertEqual(axes["method"], ["filter", "plan", "rigor"])
            # Form/channel singletons.
            self.assertEqual(axes["form"], ["table"])
            self.assertEqual(axes["channel"], ["jira"])
            # Directional last-wins single token.
            self.assertEqual(axes["directional"], "fog")

else:
    if not TYPE_CHECKING:

        class PatternDebugCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
