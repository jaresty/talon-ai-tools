import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.talonSettings import _filter_axis_tokens
    from talon_user.lib.axisCatalog import axis_catalog

    class TalonSettingsAxisCatalogTests(unittest.TestCase):
        def test_filter_axis_tokens_accepts_catalog_tokens_and_drops_unknown(self) -> None:
            """Guardrail: talonSettings axis filtering aligns with axis_catalog tokens."""

            catalog = axis_catalog()
            directional_tokens = list((catalog["axes"]["directional"] or {}).keys())
            valid_directional = directional_tokens[:2]

            axes = {
                "scope": ["focus", "Important: expand scope"],
                "method": ["steps", "unknown-method"],
                "form": ["bullets"],
                "channel": ["jira", "unknown-channel"],
                "directional": valid_directional + ["unknown-direction"],
            }

            filtered = _filter_axis_tokens(axes)  # type: ignore[arg-type]

            self.assertEqual(filtered["scope"], ["focus"])
            self.assertEqual(filtered["method"], ["steps"])
            self.assertEqual(filtered["form"], ["bullets"])
            self.assertEqual(filtered["channel"], ["jira"])
            # Unknown directional should be dropped; known catalog tokens kept.
            self.assertEqual(filtered.get("directional"), valid_directional)

else:
    if not TYPE_CHECKING:

        class TalonSettingsAxisCatalogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
