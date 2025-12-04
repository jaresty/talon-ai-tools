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

    class ReadmeAxisListTests(unittest.TestCase):
        def setUp(self) -> None:
            self.root = Path(__file__).resolve().parents[1]
            self.readme_path = self.root / "GPT" / "readme.md"
            self.assertTrue(
                self.readme_path.is_file(),
                "GPT/readme.md should exist for this test",
            )

        def _read_axis_keys_from_list(self, filename: str) -> set[str]:
            lists_dir = self.root / "GPT" / "lists"
            path = lists_dir / filename
            self.assertTrue(
                path.is_file(),
                f"Axis list file {filename!r} should exist for this test",
            )
            keys: set[str] = set()
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if (
                        not s
                        or s.startswith("#")
                        or s.startswith("list:")
                        or s == "-"
                    ):
                        continue
                    if ":" not in s:
                        continue
                    key, _ = s.split(":", 1)
                    keys.add(key.strip())
            return keys

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

        def test_readme_method_axis_list_matches_method_modifier_list(self) -> None:
            """Ensure README method axis tokens stay aligned with methodModifier.talon-list."""
            list_keys = self._read_axis_keys_from_list("methodModifier.talon-list")
            readme_keys = self._read_axis_keys_from_readme_line(
                "Method (`methodModifier`)"
            )

            missing = sorted(list_keys - readme_keys)
            self.assertFalse(
                missing,
                f"Method tokens missing from README method axis list: {missing}",
            )

        def test_readme_style_axis_list_matches_style_modifier_list(self) -> None:
            """Ensure README style axis tokens stay aligned with styleModifier.talon-list."""
            list_keys = self._read_axis_keys_from_list("styleModifier.talon-list")
            readme_keys = self._read_axis_keys_from_readme_line(
                "Style (`styleModifier`)"
            )

            missing = sorted(list_keys - readme_keys)
            self.assertFalse(
                missing,
                f"Style tokens missing from README style axis list: {missing}",
            )

else:
    if not TYPE_CHECKING:
        class ReadmeAxisListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

