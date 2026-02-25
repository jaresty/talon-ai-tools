"""Specifying validation for ADR-0146 Phase 2: AXIS_KEY_TO_ROUTING_CONCEPT data.

Tests:
  RC1 — AXIS_KEY_TO_ROUTING_CONCEPT is importable from lib/axisConfig.py
  RC2 — scope tokens that share a routing concept (thing+struct) have identical phrases
  RC3 — form tokens that share a routing concept (actions+checklist, walkthrough+recipe)
        have identical phrases
  RC4 — all scope tokens that appear in the hardcoded Choosing Scope section have a
        routing concept entry
  RC5 — all form tokens that appear in the hardcoded Choosing Form section have a
        routing concept entry
  RC6 — routing concept phrases are non-empty strings
  RC7 — axis_key_to_routing_concept_map accessor returns correct data
"""
import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import (
        AXIS_KEY_TO_ROUTING_CONCEPT,
        axis_key_to_routing_concept_map,
    )

    # Scope tokens that must have routing concepts (from hardcoded Choosing Scope section)
    _REQUIRED_SCOPE_TOKENS = {
        "thing", "struct", "time", "mean", "act", "good",
        "fail", "view", "assume", "motifs", "stable", "cross",
    }
    # Form tokens that must have routing concepts (from hardcoded Choosing Form section)
    _REQUIRED_FORM_TOKENS = {
        "actions", "checklist", "variants", "walkthrough", "recipe",
        "table", "scaffold", "case",
    }

    class RoutingConceptTests(unittest.TestCase):
        def test_RC1_importable(self) -> None:
            """AXIS_KEY_TO_ROUTING_CONCEPT is a dict."""
            self.assertIsInstance(AXIS_KEY_TO_ROUTING_CONCEPT, dict)
            self.assertIn("scope", AXIS_KEY_TO_ROUTING_CONCEPT)
            self.assertIn("form", AXIS_KEY_TO_ROUTING_CONCEPT)

        def test_RC2_scope_multi_token_groups_share_phrase(self) -> None:
            """thing and struct map to the same concept phrase."""
            scope = AXIS_KEY_TO_ROUTING_CONCEPT.get("scope", {})
            self.assertEqual(
                scope.get("thing"), scope.get("struct"),
                "thing and struct must share the same routing concept phrase",
            )

        def test_RC3_form_multi_token_groups_share_phrase(self) -> None:
            """actions+checklist and walkthrough+recipe each share a concept phrase."""
            form = AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {})
            self.assertEqual(
                form.get("actions"), form.get("checklist"),
                "actions and checklist must share the same routing concept phrase",
            )
            self.assertEqual(
                form.get("walkthrough"), form.get("recipe"),
                "walkthrough and recipe must share the same routing concept phrase",
            )

        def test_RC4_all_hardcoded_scope_tokens_have_concept(self) -> None:
            """All scope tokens from the hardcoded Choosing Scope section are covered."""
            scope = AXIS_KEY_TO_ROUTING_CONCEPT.get("scope", {})
            for token in _REQUIRED_SCOPE_TOKENS:
                self.assertIn(
                    token, scope,
                    f"scope:{token} must have a routing concept (ADR-0146 Phase 2)",
                )

        def test_RC5_all_hardcoded_form_tokens_have_concept(self) -> None:
            """All form tokens from the hardcoded Choosing Form section are covered."""
            form = AXIS_KEY_TO_ROUTING_CONCEPT.get("form", {})
            for token in _REQUIRED_FORM_TOKENS:
                self.assertIn(
                    token, form,
                    f"form:{token} must have a routing concept (ADR-0146 Phase 2)",
                )

        def test_RC6_all_phrases_are_non_empty_strings(self) -> None:
            """Every routing concept value is a non-empty string."""
            for axis, tokens in AXIS_KEY_TO_ROUTING_CONCEPT.items():
                for token, phrase in tokens.items():
                    self.assertIsInstance(phrase, str, f"{axis}:{token} phrase must be str")
                    self.assertTrue(phrase.strip(), f"{axis}:{token} phrase must not be empty")

        def test_RC7_accessor_returns_correct_data(self) -> None:
            """axis_key_to_routing_concept_map returns the same data as direct dict access."""
            for axis in ("scope", "form"):
                self.assertEqual(
                    axis_key_to_routing_concept_map(axis),
                    AXIS_KEY_TO_ROUTING_CONCEPT.get(axis, {}),
                )
            self.assertEqual(axis_key_to_routing_concept_map("nonexistent"), {})


if __name__ == "__main__":
    unittest.main()
