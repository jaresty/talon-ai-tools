import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_VALUE
    from talon_user.lib.talonSettings import (
        _AXIS_INCOMPATIBILITIES,
        _axis_recipe_token,
        _axis_string_to_tokens,
        _axis_tokens_to_string,
        _map_axis_tokens,
        _canonicalise_axis_tokens,
        _read_axis_default_from_list,
        _read_axis_value_to_key_map,
    )
    from talon_user.lib.axisMappings import (
        axis_hydrate_token,
        axis_hydrate_tokens,
        axis_key_to_value_map_for,
        axis_value_to_key_map_for,
    )
    from talon_user.lib.axisCatalog import axis_catalog

    class AxisMappingTests(unittest.TestCase):
        def test_value_to_key_returns_tokens_only(self) -> None:
            mapping = _read_axis_value_to_key_map("methodModifier.talon-list")
            self.assertIn("rigor", mapping)
            self.assertEqual(mapping["rigor"], "rigor")
            # Descriptions should no longer appear in value->key map.
            self.assertFalse(
                any("Important:" in key for key in mapping.keys()),
                "Value->key map should contain tokens only",
            )

        def test_value_to_key_missing_file_returns_empty_dict(self) -> None:
            mapping = _read_axis_value_to_key_map("nonexistent-axis-file.talon-list")
            self.assertEqual(mapping, {})

        def test_axis_recipe_token_returns_token_identity(self) -> None:
            """_axis_recipe_token should be identity on token inputs."""
            key, _desc = next(iter(AXIS_KEY_TO_VALUE["completeness"].items()))
            self.assertEqual(_axis_recipe_token("completeness", key), key)

        def test_axis_recipe_token_preserves_multi_token_values(self) -> None:
            """Multi-token axis lists should round-trip."""
            token = _axis_recipe_token("method", "plan xp")  # type: ignore[arg-type]
            self.assertEqual(token, "plan xp")
            self.assertEqual(_map_axis_tokens("method", ["plan", "xp"]), ["plan", "xp"])

        def test_axis_recipe_token_falls_back_for_unknown_axis(self) -> None:
            self.assertEqual(
                _axis_recipe_token("unknown-axis", "some-value"),
                "some-value",
            )

        def _assert_axis_round_trip(self, axis: str) -> None:
            key, _desc = next(iter(AXIS_KEY_TO_VALUE[axis].items()))
            token_from_desc = _axis_recipe_token(axis, key)  # type: ignore[arg-type]
            self.assertEqual(token_from_desc, key)
            token_from_key = _axis_recipe_token(axis, key)  # type: ignore[arg-type]
            self.assertEqual(token_from_key, key)

        def test_scope_axis_recipe_token_uses_value_to_key_map(self) -> None:
            self._assert_axis_round_trip("scope")

        def test_method_axis_recipe_token_uses_value_to_key_map(self) -> None:
            self._assert_axis_round_trip("method")

        def test_read_axis_default_from_list_returns_list_value(self) -> None:
            """Ensure _read_axis_default_from_list returns the token when present."""
            # Lists now store token:token entries; expect the token back.
            value = _read_axis_default_from_list(
                "completenessModifier.talon-list",
                "full",
                "fallback-value",
            )
            self.assertEqual(value, "full")

        def test_read_axis_default_from_list_falls_back_when_missing(self) -> None:
            value = _read_axis_default_from_list(
                "nonexistent-list.talon-list",
                "full",
                "fallback-value",
            )
            self.assertEqual(value, "fallback-value")

        def test_canonicalise_axis_tokens_deduplicates_and_sorts(self) -> None:
            """Axis token canonicalisation should dedupe and canonicalise order."""
            tokens = ["jira", "slack", "jira", "slack", "jira"]

            canonical = _canonicalise_axis_tokens("channel", tokens)

            # Channel cap is 1; only the last token should survive.
            self.assertEqual(canonical, ["slack"])

        def test_canonicalise_axis_tokens_applies_soft_caps_with_last_wins(self) -> None:
            """Soft caps should keep the most recent tokens for an axis."""
            # For scope, the soft cap is 2. Providing three distinct tokens
            # should result in at most two surviving, and they should be a
            # subset of the originals.
            tokens = ["narrow", "focus", "bound"]

            canonical = _canonicalise_axis_tokens("scope", tokens)

            # The scope soft cap is 2; more than that should be trimmed.
            self.assertEqual(len(canonical), 2)
            for token in canonical:
                self.assertIn(token, tokens)

            serialised = _axis_tokens_to_string(canonical)
            round_tripped = _axis_string_to_tokens(serialised)
            self.assertEqual(round_tripped, canonical)

        def test_canonicalise_axis_tokens_respects_method_soft_cap(self) -> None:
            """Method axis canonicalisation should enforce a cap of 3 tokens."""
            # For method, the soft cap is 3. Providing four distinct tokens
            # should result in exactly three surviving, all drawn from the
            # original set.
            tokens = ["steps", "plan", "rigor", "rewrite"]

            canonical = _canonicalise_axis_tokens("method", tokens)

            self.assertEqual(len(canonical), 3)
            for token in canonical:
                self.assertIn(token, tokens)

            serialised = _axis_tokens_to_string(canonical)
            round_tripped = _axis_string_to_tokens(serialised)
            self.assertEqual(round_tripped, canonical)

        def test_talon_list_tokens_match_axis_config(self) -> None:
            """Guardrail: Talon list tokens must match axisConfig tokens (token-only ingress)."""
            catalog = axis_catalog()
            axis_lists = catalog.get("axis_list_tokens", {}) or {}
            for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
                with self.subTest(axis=axis):
                    config_tokens = set(AXIS_KEY_TO_VALUE[axis].keys())
                    list_tokens = set(axis_lists.get(axis, []))
                    self.assertTrue(list_tokens, f"Expected tokens for axis {axis} in axis_list_tokens")
                    self.assertEqual(
                        list_tokens,
                        config_tokens,
                        f"Talon list tokens for axis {axis} must match axisConfig",
                    )

        def test_map_axis_tokens_rejects_legacy_style_axis(self) -> None:
            """Guardrail: style axis should be blocked post form/channel split."""
            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                _map_axis_tokens("style", ["plain"])

        def test_axis_mapping_helpers_reject_legacy_style_axis(self) -> None:
            """Guardrail: axis mapping/hydration helpers should reject style axis."""
            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                axis_value_to_key_map_for("style")
            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                axis_key_to_value_map_for("style")
            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                axis_hydrate_tokens("style", ["plain"])
            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                axis_hydrate_token("style", "plain")

else:
    if not TYPE_CHECKING:
        class AxisMappingTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
