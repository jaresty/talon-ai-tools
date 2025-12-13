import re
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from pathlib import Path

    from talon_user.lib.axisCatalog import axis_catalog

    class ReadmeAxisListTests(unittest.TestCase):
        def setUp(self) -> None:
            self.root = Path(__file__).resolve().parents[1]
            self.readme_path = self.root / "GPT" / "readme.md"
            self.assertTrue(
                self.readme_path.is_file(),
                "GPT/readme.md should exist for this test",
            )

        def _read_axis_keys_from_readme_line(self, marker: str) -> set[str]:
            text = self.readme_path.read_text(encoding="utf-8")
            line = None
            for candidate in text.splitlines():
                if marker in candidate:
                    line = candidate
                    break
            self.assertIsNotNone(
                line, f"Expected to find a README line containing {marker!r}"
            )
            # Extract tokens wrapped in backticks.
            keys = set(re.findall(r"`([^`]+)`", line or ""))
            self.assertTrue(
                keys,
                f"Expected at least one backticked token in README line containing {marker!r}",
            )
            return keys

        def test_readme_axis_lists_match_catalog_for_core_axes(self) -> None:
            """README token lists should match the axis catalog for core axes."""
            catalog = axis_catalog()
            axis_markers = {
                "completeness": "Completeness (`completenessModifier`)",
                "scope": "Scope (`scopeModifier`)",
                "method": "Method (`methodModifier`)",
                "form": "Form (`formModifier`)",
                "channel": "Channel (`channelModifier`)",
            }
            for axis, marker in axis_markers.items():
                with self.subTest(axis=axis):
                    readme_keys = {
                        key
                        for key in self._read_axis_keys_from_readme_line(marker)
                        if "Modifier" not in key
                    }
                    catalog_keys = set((catalog.get("axes", {}).get(axis) or {}).keys())
                    # Presenterm moved to the channel axis; ignore legacy mentions under form.
                    if axis == "form":
                        readme_keys.discard("presenterm")
                    missing = sorted(catalog_keys - readme_keys)
                    extra = sorted(readme_keys - catalog_keys)
                    self.assertFalse(
                        missing,
                        f"{axis} tokens missing from README list: {missing}",
                    )
                    self.assertFalse(
                        extra,
                        f"{axis} README tokens not present in catalog: {extra}",
                    )

        def test_readme_does_not_reference_legacy_style_axis(self) -> None:
            """Guardrail: README should not reference the removed style axis."""
            text = self.readme_path.read_text(encoding="utf-8")
            self.assertNotIn("model set style", text)
            self.assertNotIn("model reset style", text)
            self.assertNotIn("style=", text)
            self.assertNotIn("style axis", text)

else:
    if not TYPE_CHECKING:
        class ReadmeAxisListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
