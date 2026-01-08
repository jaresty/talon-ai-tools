import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisCatalog import axis_catalog, serialize_axis_config
    from scripts.tools.generate_axis_config import render_axis_catalog_json

    class AxisCatalogSerializerTests(unittest.TestCase):
        def test_serializes_axes_without_style(self):
            payload = serialize_axis_config(include_axis_lists=False)
            self.assertIn("axes", payload)
            axes = payload["axes"]
            self.assertNotIn("style", axes)
            self.assertEqual(axes, axis_catalog()["axes"])
            self.assertNotIn("axis_list_tokens", payload)

        def test_serializes_axis_lists_from_talon_files(self):
            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                lists_dir.mkdir(parents=True, exist_ok=True)
                completeness_list = lists_dir / "completenessModifier.talon-list"
                completeness_list.write_text(
                    "list: user.completenessModifier\nfocus: focus\n", encoding="utf-8"
                )
                axis_map = axis_catalog()["axes"]
                payload = serialize_axis_config(lists_dir=lists_dir)
                axis_lists = payload.get("axis_list_tokens", {})
                self.assertIn("completeness", axis_lists)
                # Custom list token is present and SSOT tokens are merged.
                self.assertIn("focus", axis_lists["completeness"])
                for token in axis_map["completeness"].keys():
                    self.assertIn(token, axis_lists["completeness"])

        def test_render_axis_catalog_json_includes_axes_and_lists(self):
            with tempfile.TemporaryDirectory() as tmpdir:
                lists_dir = Path(tmpdir)
                lists_dir.mkdir(parents=True, exist_ok=True)
                scope_list = lists_dir / "scopeModifier.talon-list"
                scope_list.write_text(
                    "list: user.scopeModifier\nfocus: focus\n", encoding="utf-8"
                )
                text = render_axis_catalog_json(lists_dir=lists_dir)
                self.assertIn('"axes":', text)
                self.assertIn("axis_list_tokens", text)
                self.assertIn("focus", text)
else:
    if not TYPE_CHECKING:

        class AxisCatalogSerializerTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
