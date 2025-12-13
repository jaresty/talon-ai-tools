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
            axis_to_list = {
                "completeness": "completenessModifier.talon-list",
                "scope": "scopeModifier.talon-list",
                "method": "methodModifier.talon-list",
                "form": "formModifier.talon-list",
                "channel": "channelModifier.talon-list",
                "directional": "directionalModifier.talon-list",
            }

            def _list_tokens(filename: str) -> set[str]:
                path = Path(__file__).resolve().parent.parent / "GPT" / "lists" / filename
                tokens: set[str] = set()
                with path.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if (
                            not line
                            or line.startswith("#")
                            or line.startswith("list:")
                            or line == "-"
                        ):
                            continue
                        if ":" not in line:
                            continue
                        key, _value = line.split(":", 1)
                        token = key.strip()
                        if token:
                            tokens.add(token)
                return tokens

            for axis, filename in axis_to_list.items():
                with self.subTest(axis=axis):
                    self.assertEqual(set(registry[axis]), _list_tokens(filename))

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

else:
    if not TYPE_CHECKING:

        class AxisRegistryDriftTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
