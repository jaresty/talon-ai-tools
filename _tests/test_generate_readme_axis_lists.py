import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from scripts.tools.generate_readme_axis_lists import render_readme_axis_lines
    from talon_user.lib.axisCatalog import axis_catalog

    class GenerateReadmeAxisListsTests(unittest.TestCase):
        def test_generator_matches_catalog_axis_tokens(self) -> None:
            lines = render_readme_axis_lines().strip().splitlines()
            catalog = axis_catalog()
            axes = catalog.get("axes", {}) or {}
            for line in lines:
                label, tokens = line.split(":", 1)
                axis = label.split()[0].lower()
                expected_tokens = set((axes.get(axis) or {}).keys())
                rendered_tokens = set(token.strip("` ") for token in tokens.split(","))
                self.assertEqual(
                    expected_tokens,
                    rendered_tokens,
                    f"Rendered tokens for {axis} did not match catalog",
                )

        def test_lists_dir_merges_tokens(self) -> None:
            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                lists_dir.mkdir(parents=True, exist_ok=True)
                scope_list = lists_dir / "scopeModifier.talon-list"
                scope_list.write_text(
                    "list: user.scopeModifier\nfocus: focus\n", encoding="utf-8"
                )
                lines = (
                    render_readme_axis_lines(lists_dir=lists_dir).strip().splitlines()
                )
            scope_line = next((line for line in lines if line.startswith("Scope ")), "")
            self.assertIn("`focus`", scope_line)

        def test_generator_normalises_tokens_via_axis_snapshot(self) -> None:
            snapshots = {
                "axes": {
                    "completeness": {"Full": "desc"},
                    "scope": {"Focus": "desc"},
                    "method": {},
                    "form": {},
                    "channel": {},
                    "directional": {"Fog": "desc"},
                },
                "axis_list_tokens": {
                    "completeness": ["Full", "full", "Important: extra"],
                    "scope": ["Focus"],
                    "method": [],
                    "form": [],
                    "channel": [],
                    "directional": ["Fog"],
                },
            }
            with patch(
                "scripts.tools.generate_readme_axis_lists.axis_catalog",
                return_value=snapshots,
            ):
                lines = render_readme_axis_lines().strip().splitlines()
            completeness_line = next(
                (line for line in lines if line.startswith("Completeness")),
                "",
            )
            scope_line = next(
                (line for line in lines if line.startswith("Scope")),
                "",
            )
            directional_line = next(
                (line for line in lines if line.startswith("Directional")),
                "",
            )
            self.assertIn("`full`", completeness_line)
            self.assertNotIn("Full", completeness_line)
            self.assertNotIn("Important:", completeness_line)
            self.assertIn("`focus`", scope_line)
            self.assertIn("`fog`", directional_line)

else:

    class GenerateReadmeAxisListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            pass
