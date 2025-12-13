import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestHistoryActions import history_axes_for
    from talon_user.lib.axisCatalog import axis_catalog

    class RequestHistoryActionsCatalogTests(unittest.TestCase):
        def test_history_axes_for_filters_using_catalog_tokens(self) -> None:
            """Guardrail: history axes normalisation keeps catalog tokens and drops unknowns."""

            catalog = axis_catalog()
            directional_tokens = list((catalog["axes"]["directional"] or {}).keys())
            valid_directional = directional_tokens[:1]

            axes = {
                "scope": ["focus", "unknown-scope"],
                "method": ["steps", "unknown-method"],
                "form": ["bullets", "unknown-form"],
                "channel": ["slack", "unknown-channel"],
                "directional": valid_directional + ["unknown-direction"],
            }

            filtered = history_axes_for(axes)

            self.assertEqual(filtered["scope"], ["focus"])
            self.assertEqual(filtered["method"], ["steps"])
            self.assertEqual(filtered["form"], ["bullets"])
            self.assertEqual(filtered["channel"], ["slack"])
            self.assertEqual(filtered["directional"], valid_directional)
            self.assertNotIn("style", filtered)

else:
    if not TYPE_CHECKING:

        class RequestHistoryActionsCatalogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
