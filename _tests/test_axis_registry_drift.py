import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE
    from talon_user.lib.axisMappings import axis_registry
    from talon_user.lib.axisCatalog import axis_catalog

    class AxisRegistryDriftTests(unittest.TestCase):
        def setUp(self) -> None:
            self._tmp_dir = tempfile.TemporaryDirectory()

        def tearDown(self) -> None:
            try:
                self._tmp_dir.cleanup()
            except Exception:
                pass

        def test_registry_matches_axis_config_tokens(self) -> None:
            registry = axis_registry()
            for axis, mapping in AXIS_KEY_TO_VALUE.items():
                with self.subTest(axis=axis):
                    self.assertIn(axis, registry)
                    self.assertEqual(set(registry[axis]), set(mapping.keys()))

        def test_registry_tokens_match_talon_lists(self) -> None:
            registry = axis_registry()
            catalog = axis_catalog()
            axis_lists = catalog.get("axis_list_tokens", {}) or {}
            for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
                with self.subTest(axis=axis):
                    list_tokens = set(axis_lists.get(axis, []))
                    self.assertTrue(list_tokens, f"Expected tokens for axis {axis} from catalog axis_list_tokens")
                    self.assertEqual(set(registry[axis]), list_tokens)

        def test_style_axis_and_lists_are_removed(self) -> None:
            """Guardrail: legacy style axis/list must not reappear after form/channel split."""
            registry = axis_registry()
            self.assertNotIn("style", registry)

            style_list_path = (
                Path(__file__).resolve().parent.parent / "GPT" / "lists" / "styleModifier.talon-list"
            )
            self.assertFalse(
                style_list_path.exists(),
                "styleModifier.talon-list should be removed after form/channel migration",
            )

        def test_axis_catalog_rejects_legacy_style_list(self) -> None:
            """Guardrail: axis_catalog should fail fast when a style list reappears."""
            tmp = Path(self._tmp_dir.name)
            lists_dir = tmp / "lists"
            lists_dir.mkdir(parents=True, exist_ok=True)
            style_path = lists_dir / "styleModifier.talon-list"
            style_path.write_text("list: user.styleModifier\n-\nplain: plain\n", encoding="utf-8")

            from talon_user.lib.axisCatalog import axis_catalog

            with self.assertRaises(ValueError):
                axis_catalog(lists_dir=lists_dir)

        def test_axis_catalog_falls_back_when_lists_missing(self) -> None:
            """Guardrail: catalog should surface axis tokens even without list files."""
            tmp = Path(self._tmp_dir.name)
            empty_lists_dir = tmp / "no_lists"
            empty_lists_dir.mkdir(parents=True, exist_ok=True)

            from talon_user.lib.axisCatalog import axis_catalog

            catalog = axis_catalog(lists_dir=empty_lists_dir)
            axis_lists = catalog.get("axis_list_tokens", {}) or {}
            for axis, mapping in AXIS_KEY_TO_VALUE.items():
                with self.subTest(axis=axis):
                    config_tokens = set(mapping.keys())
                    catalog_tokens = set(axis_lists.get(axis, []))
                    self.assertTrue(
                        catalog_tokens,
                        f"Expected catalog axis tokens for {axis} even when lists are missing",
                    )
                    self.assertEqual(
                        catalog_tokens,
                        config_tokens,
                        f"Catalog axis tokens should fall back to axisConfig when lists are absent for {axis}",
                    )

        def test_axis_catalog_merges_partial_list_with_config_tokens(self) -> None:
            """Guardrail: partial list files should not hide SSOT tokens."""
            tmp = Path(self._tmp_dir.name)
            lists_dir = tmp / "lists_partial"
            lists_dir.mkdir(parents=True, exist_ok=True)

            # Write a subset list for completeness (only 'full').
            completeness_path = lists_dir / "completenessModifier.talon-list"
            completeness_path.write_text(
                "list: user.completenessModifier\n-\nfull: full\n",
                encoding="utf-8",
            )

            from talon_user.lib.axisCatalog import axis_catalog

            catalog = axis_catalog(lists_dir=lists_dir)
            axis_lists = catalog.get("axis_list_tokens", {}) or {}
            config_tokens = set(AXIS_KEY_TO_VALUE["completeness"].keys())
            catalog_tokens = set(axis_lists.get("completeness", []))
            self.assertTrue(
                config_tokens.issubset(catalog_tokens),
                "Completeness axis tokens from config should still be present when list is partial",
            )
            self.assertIn(
                "full",
                catalog_tokens,
                "List-provided token should remain present after merge",
            )

else:
    if not TYPE_CHECKING:

        class AxisRegistryDriftTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
