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
    import tempfile

    from talon_user.lib.talonSettings import (
        _axis_recipe_token,
        _read_axis_default_from_list,
        _read_axis_value_to_key_map,
    )

    class AxisMappingTests(unittest.TestCase):
        def setUp(self) -> None:
            # Create a temporary Talon list file under GPT/lists for these tests.
            root = Path(__file__).resolve().parents[1]
            lists_dir = root / "GPT" / "lists"
            lists_dir.mkdir(parents=True, exist_ok=True)
            self.tests_axis_path = lists_dir / "testsAxisMapping.talon-list"
            self.tests_axis_path.write_text(
                "\n".join(
                    [
                        "list: user.testsAxisMapping",
                        "#",
                        "-",
                        "",
                        "# Well-formed entries",
                        "short1: Long description one that should map back to short1.",
                        "short2: Another description that should map back to short2.",
                        "",
                        "# Malformed / ignored entries",
                        "just-some-text-without-colon",
                        "-",
                    ]
                ),
                encoding="utf-8",
            )

        def tearDown(self) -> None:
            try:
                self.tests_axis_path.unlink()
            except FileNotFoundError:
                pass

        def test_builds_mapping_from_keys_and_descriptions(self) -> None:
            mapping = _read_axis_value_to_key_map("testsAxisMapping.talon-list")

            # Both the short key and the long description should map back
            # to the short token.
            self.assertEqual(mapping["short1"], "short1")
            self.assertEqual(
                mapping["Long description one that should map back to short1."],
                "short1",
            )
            self.assertEqual(mapping["short2"], "short2")
            self.assertEqual(
                mapping["Another description that should map back to short2."],
                "short2",
            )

        def test_ignores_comments_headers_and_malformed_lines(self) -> None:
            mapping = _read_axis_value_to_key_map("testsAxisMapping.talon-list")

            # Header, comments, bare dashes, and lines without a colon should
            # not appear in the mapping.
            self.assertNotIn("list: user.testsAxisMapping", mapping)
            self.assertNotIn("just-some-text-without-colon", mapping)
            # We only expect the four mappings from the two well-formed lines.
            self.assertEqual(len(mapping), 4)

        def test_missing_file_returns_empty_dict(self) -> None:
            mapping = _read_axis_value_to_key_map("nonexistent-axis-file.talon-list")
            self.assertEqual(mapping, {})

        def test_axis_recipe_token_maps_description_back_to_short_key(self) -> None:
            """Ensure _axis_recipe_token uses the underlying value→key maps."""
            # Parse one real entry from the completeness list so the test
            # stays aligned with the repository configuration.
            root = Path(__file__).resolve().parents[1]
            completeness_path = root / "GPT" / "lists" / "completenessModifier.talon-list"
            key = None
            desc = None
            with completeness_path.open("r", encoding="utf-8") as f:
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
                    key, value = line.split(":", 1)
                    key = key.strip()
                    desc = value.strip()
                    break

            self.assertIsNotNone(key)
            self.assertIsNotNone(desc)

            # Description should map back to the short key.
            token_from_desc = _axis_recipe_token("completeness", desc)  # type: ignore[arg-type]
            self.assertEqual(token_from_desc, key)

            # Short key should map idempotently to itself.
            token_from_key = _axis_recipe_token("completeness", key)  # type: ignore[arg-type]
            self.assertEqual(token_from_key, key)

        def test_axis_recipe_token_falls_back_for_unknown_axis(self) -> None:
            self.assertEqual(
                _axis_recipe_token("unknown-axis", "some-value"),
                "some-value",
            )

        def test_directional_axis_recipe_token_uses_value_to_key_map(self) -> None:
            """Directional axis values should also round-trip through the mapping."""
            root = Path(__file__).resolve().parents[1]
            directional_path = root / "GPT" / "lists" / "directionalModifier.talon-list"
            key = None
            desc = None
            with directional_path.open("r", encoding="utf-8") as f:
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
                    key, value = line.split(":", 1)
                    key = key.strip()
                    desc = value.strip()
                    break

            self.assertIsNotNone(key)
            self.assertIsNotNone(desc)

            # Description should map back to the short key.
            token_from_desc = _axis_recipe_token(  # type: ignore[arg-type]
                "directional",
                desc,
            )
            self.assertEqual(token_from_desc, key)

            # Short key should map idempotently to itself.
            token_from_key = _axis_recipe_token(  # type: ignore[arg-type]
                "directional",
                key,
            )
            self.assertEqual(token_from_key, key)

        def _assert_axis_round_trip(self, filename: str, axis: str) -> None:
            root = Path(__file__).resolve().parents[1]
            path = root / "GPT" / "lists" / filename
            key = None
            desc = None
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
                    key, value = line.split(":", 1)
                    key = key.strip()
                    desc = value.strip()
                    break

            self.assertIsNotNone(key)
            self.assertIsNotNone(desc)

            token_from_desc = _axis_recipe_token(axis, desc)  # type: ignore[arg-type]
            self.assertEqual(token_from_desc, key)

            token_from_key = _axis_recipe_token(axis, key)  # type: ignore[arg-type]
            self.assertEqual(token_from_key, key)

        def test_scope_axis_recipe_token_uses_value_to_key_map(self) -> None:
            self._assert_axis_round_trip("scopeModifier.talon-list", "scope")

        def test_method_axis_recipe_token_uses_value_to_key_map(self) -> None:
            self._assert_axis_round_trip("methodModifier.talon-list", "method")

        def test_style_axis_recipe_token_uses_value_to_key_map(self) -> None:
            self._assert_axis_round_trip("styleModifier.talon-list", "style")

        def test_read_axis_default_from_list_returns_list_value(self) -> None:
            """Ensure _read_axis_default_from_list returns the list value when present."""
            # For the completeness list, the value for "full" is a long
            # description; the helper should return that description rather
            # than the fallback.
            value = _read_axis_default_from_list(
                "completenessModifier.talon-list",
                "full",
                "fallback-value",
            )
            self.assertIn("Important:", value)

        def test_read_axis_default_from_list_falls_back_when_missing(self) -> None:
            value = _read_axis_default_from_list(
                "nonexistent-list.talon-list",
                "full",
                "fallback-value",
            )
            self.assertEqual(value, "fallback-value")

else:
    if not TYPE_CHECKING:
        class AxisMappingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
