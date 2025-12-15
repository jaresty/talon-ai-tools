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
    from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines

    class ReadmeAxisListTests(unittest.TestCase):
        def setUp(self) -> None:
            self.root = Path(__file__).resolve().parents[1]
            self.readme_path = self.root / "GPT" / "readme.md"
            self.assertTrue(
                self.readme_path.is_file(),
                "GPT/readme.md should exist for this test",
            )

        def test_readme_does_not_reference_legacy_style_axis(self) -> None:
            """Guardrail: README should not reference the removed style axis."""
            text = self.readme_path.read_text(encoding="utf-8")
            self.assertNotIn("model set style", text)
            self.assertNotIn("model reset style", text)
            self.assertNotIn("style=", text)
            self.assertNotIn("style axis", text)

        def test_readme_axis_lines_match_generator_snapshot(self) -> None:
            """README axis lines should match the catalog-driven generator."""

            expected_lines = render_readme_axis_lines().strip().splitlines()
            readme_lines = self.readme_path.read_text(encoding="utf-8").splitlines()
            for expected in expected_lines:
                label = expected.split(":", 1)[0]
                readme_line = next((line for line in readme_lines if line.startswith(label)), "")
                self.assertEqual(
                    expected,
                    readme_line,
                    f"Mismatch for README axis line {label!r}",
                )

else:
    if not TYPE_CHECKING:
        class ReadmeAxisListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
