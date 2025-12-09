import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.axisMappings import axis_key_to_value_map_for
    from talon_user.lib.talonSettings import modelPrompt
    from talon_user.lib.modelState import GPTState

    class ModelPromptModifiersTests(unittest.TestCase):
        def setUp(self) -> None:
            # Ensure GPTState starts clean for tests that rely on derived axes.
            if bootstrap is not None:
                GPTState.reset_all()
                settings.set("user.model_default_completeness", "full")
                settings.set("user.model_default_scope", "")
                settings.set("user.model_default_method", "")
                settings.set("user.model_default_style", "")

        def test_no_modifiers_uses_static_prompt_profile_when_present(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # With no explicit axis modifiers, we should get a Task / Constraints
            # schema with a profile-driven completeness/scope hint and the lens
            # appended after a blank line.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn(
                "Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text.",
                result,
            )
            # Profile for "fix" biases completeness/scope conceptually.
            self.assertIn("Completeness:", result)
            self.assertIn("Scope:", result)
            # Directional lens appears after the schema.
            self.assertTrue(result.rstrip().endswith("DIR"))

        def test_explicit_completeness_modifier_is_used_as_is(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Explicit completeness should appear under the Completeness line.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn("Completeness: COMP", result)
            self.assertTrue(result.rstrip().endswith("DIR"))

        def test_scope_method_style_modifiers_appended_in_order(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                scopeModifier="SCOPE",
                methodModifier="METHOD",
                styleModifier="STYLE",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Check that all constraint lines are present under the schema.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn("Completeness: COMP", result)
            self.assertIn("Scope: SCOPE", result)
            self.assertIn("Method: METHOD", result)
            self.assertIn("Style: STYLE", result)
            self.assertTrue(result.rstrip().endswith("DIR"))

        def test_constraint_block_hydrates_axis_tokens(self):
            """Constraints should display hydrated axis descriptions while state stays tokenised."""
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="relations",
                methodModifier="steps",
                styleModifier="bullets",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            completeness_desc = axis_key_to_value_map_for("completeness").get(
                "skim", "skim"
            )
            scope_desc = axis_key_to_value_map_for("scope").get("relations", "relations")
            method_desc = axis_key_to_value_map_for("method").get("steps", "steps")
            style_desc = axis_key_to_value_map_for("style").get("bullets", "bullets")

            self.assertIn(f"Completeness: {completeness_desc}", result)
            self.assertIn(f"Scope: {scope_desc}", result)
            self.assertIn(f"Method: {method_desc}", result)
            self.assertIn(f"Style: {style_desc}", result)

        def test_missing_scope_method_style_do_not_add_text(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="COMP",
                # scope/method/style omitted on purpose; profiles may add hints,
                # but we should not see the test sentinel tokens.
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            self.assertIn("Task:", result)
            self.assertIn("Completeness: COMP", result)
            # No literal sentinel tokens should appear for scope/method/style.
            self.assertNotIn("SCOPE", result)
            self.assertNotIn("METHOD", result)
            self.assertNotIn("STYLE", result)
            self.assertTrue(result.rstrip().endswith("DIR"))

        def test_model_prompt_updates_system_prompt_axes(self):
            # Start from known defaults.
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            # Spoken modifiers should win over profiles and defaults.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="narrow",
                methodModifier="steps",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.scope, "narrow")
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "plain")

        def test_model_prompt_uses_profiles_for_system_axes_when_unset(self):
            # Defaults are present but profile should shape the effective axes
            # when no spoken modifier is given.
            # "todo" has a profile for completeness/method/style/scope.
            m = SimpleNamespace(
                staticPrompt="todo",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "gist")
            self.assertEqual(GPTState.system_prompt.scope, "actions")
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "checklist")

        def test_prefixed_token_reassigns_to_highest_priority_axis(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                # Intentionally mis-placed axis token with explicit prefix.
                styleModifier="Completeness:skim",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # Completeness should capture the prefixed token; style should stay empty.
            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.style, "")
            self.assertIn("Completeness:", result)
            self.assertNotIn("Style:", result.split("Constraints:", 1)[-1])

        def test_axis_map_recovers_method_token_from_wrong_axis(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                # "steps" belongs to method; provide it under style to test reassignment.
                styleModifier="steps",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # The method axis should capture the token; style should remain empty.
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "")

        def test_last_recipe_uses_resolved_axes(self):
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="infer",
                completenessModifier="full",
                # Misfile a method token under style.
                styleModifier="steps",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # Method absorbs the token; style remains empty; recipe reflects resolved axes.
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "")
            self.assertEqual(GPTState.last_recipe, "infer · full · steps")

        def test_ambiguous_token_uses_priority_order(self):
            """When a token is valid for multiple axes, the hierarchy should pick the higher-priority axis."""
            from talon_user.lib import axisMappings

            scope_map = axisMappings.AXIS_VALUE_TO_KEY_MAPS["scope"]
            method_map = axisMappings.AXIS_VALUE_TO_KEY_MAPS["method"]
            original_scope = scope_map.get("ambig")
            original_method = method_map.get("ambig")
            try:
                scope_map["ambig"] = "ambig"
                method_map["ambig"] = "ambig"

                m = SimpleNamespace(
                    staticPrompt="fix",
                    completenessModifier="full",
                    scopeModifier="ambig",
                    methodModifier="",
                    styleModifier="plain",
                    directionalModifier="DIR",
                )

                _ = modelPrompt(m)

                # Method outranks scope, so the ambiguous token should land on method.
                self.assertEqual(GPTState.system_prompt.method, "ambig")
                self.assertEqual(GPTState.system_prompt.scope, "")
            finally:
                if original_scope is None:
                    scope_map.pop("ambig", None)
                else:
                    scope_map["ambig"] = original_scope
                if original_method is None:
                    method_map.pop("ambig", None)
                else:
                    method_map["ambig"] = original_method

        def test_clear_all_resets_last_recipe_and_response(self):
            # Exercise the lifecycle: after a prompt, clear_all should drop
            # last_response/last_recipe so recap helpers don't show stale data.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="narrow",
                methodModifier="steps",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertNotEqual(GPTState.last_recipe, "")

            GPTState.clear_all()

            self.assertEqual(GPTState.last_recipe, "")
            self.assertEqual(GPTState.last_response, "")
            self.assertEqual(GPTState.last_meta, "")
            self.assertEqual(GPTState.last_directional, "")
            self.assertEqual(GPTState.last_static_prompt, "")
            self.assertEqual(GPTState.last_completeness, "")
            self.assertEqual(GPTState.last_scope, "")
            self.assertEqual(GPTState.last_method, "")
            self.assertEqual(GPTState.last_style, "")

        def test_model_prompt_updates_last_recipe_with_spoken_modifiers(self):
            # Spoken modifiers should be reflected in the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="narrow",
                methodModifier="steps",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(
                GPTState.last_recipe,
                "fix · skim · narrow · steps · plain",
            )
            self.assertEqual(GPTState.last_static_prompt, "fix")
            self.assertEqual(GPTState.last_completeness, "skim")
            self.assertEqual(GPTState.last_scope, "narrow")
            self.assertEqual(GPTState.last_method, "steps")
            self.assertEqual(GPTState.last_style, "plain")
            # Directional is stored as the short token when known; in this test
            # we use a sentinel "DIR" that is not in the Talon list, so it
            # should be preserved as-is.
            self.assertEqual(GPTState.last_directional, "DIR")

        def test_model_prompt_handles_multi_tag_scope_from_list(self):
            """Multi-tag scope from scopeModifier_list should be preserved and canonicalised."""
            # Start from known defaults.
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            # Simulate a Talon match object that exposes multiple scope
            # modifiers via the *_list attribute. Other axes remain single.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier_list=["narrow", "focus"],
                methodModifier="steps",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # System prompt should see the raw, spoken scope description.
            self.assertEqual(GPTState.system_prompt.completeness, "skim")
            self.assertEqual(GPTState.system_prompt.scope, "narrow focus")
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "plain")

            # last_scope should reflect a canonicalised set of scope tokens.
            self.assertNotEqual(GPTState.last_scope, "")
            scope_tokens = GPTState.last_scope.split()
            self.assertEqual(set(scope_tokens), {"narrow", "focus"})

            # last_recipe should include a multi-token scope segment.
            self.assertIn("fix · skim", GPTState.last_recipe)
            self.assertIn("steps", GPTState.last_recipe)
            # The exact order of scope tokens is canonicalised; assert by set.
            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            scope_part = recipe_parts[2]
            self.assertEqual(set(scope_part.split()), {"narrow", "focus"})

        def test_model_prompt_enforces_scope_soft_cap_from_list(self):
            """Over-cap multi-tag scope from scopeModifier_list should respect the soft cap."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            # Provide three distinct scope modifiers even though the soft cap
            # for scope is 2; the canonicaliser should enforce the cap.
            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier_list=["narrow", "focus", "bound"],
                methodModifier="steps",
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            # System prompt should see the raw, spoken scope description.
            self.assertEqual(GPTState.system_prompt.scope, "narrow focus bound")

            # last_scope should include at most 2 tokens drawn from the input set.
            scope_tokens = GPTState.last_scope.split()
            self.assertLessEqual(len(scope_tokens), 2)
            self.assertTrue(set(scope_tokens).issubset({"narrow", "focus", "bound"}))

            # last_recipe should reflect the capped, canonicalised scope tokens.
            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            # static, completeness, scope, method, style
            scope_part = recipe_parts[2]
            scope_part_tokens = scope_part.split()
            self.assertLessEqual(len(scope_part_tokens), 2)
            self.assertTrue(
                set(scope_part_tokens).issubset({"narrow", "focus", "bound"})
            )

        def test_model_prompt_handles_multi_tag_method_from_list(self):
            """Multi-tag method from methodModifier_list should be preserved and canonicalised."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="fix",
                completenessModifier="skim",
                scopeModifier="narrow",
                methodModifier_list=["structure", "flow"],
                styleModifier="plain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.method, "structure flow")
            self.assertNotEqual(GPTState.last_method, "")
            method_tokens = GPTState.last_method.split()
            self.assertEqual(set(method_tokens), {"structure", "flow"})

            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            # static, completeness, scope, method, style
            method_part = recipe_parts[3]
            self.assertEqual(set(method_part.split()), {"structure", "flow"})

        def test_model_prompt_handles_multi_tag_style_from_list(self):
            """Multi-tag style from styleModifier_list should be preserved and canonicalised."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            m = SimpleNamespace(
                staticPrompt="ticket",
                completenessModifier="full",
                scopeModifier="actions",
                methodModifier="structure",
                styleModifier_list=["jira", "faq"],
                directionalModifier="fog",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.style, "jira faq")
            self.assertNotEqual(GPTState.last_style, "")
            style_tokens = GPTState.last_style.split()
            self.assertEqual(set(style_tokens), {"jira", "faq"})

            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            style_part = recipe_parts[4]
            self.assertEqual(set(style_part.split()), {"jira", "faq"})

        def test_model_prompt_enforces_style_soft_cap_from_list(self):
            """Over-cap multi-tag style from styleModifier_list should respect the soft cap."""
            settings.set("user.model_default_completeness", "full")
            settings.set("user.model_default_scope", "")
            settings.set("user.model_default_method", "")
            settings.set("user.model_default_style", "")
            GPTState.reset_all()

            # Provide four distinct style modifiers even though the soft cap
            # for style is 3; the canonicaliser should enforce the cap.
            m = SimpleNamespace(
                staticPrompt="ticket",
                completenessModifier="full",
                scopeModifier="actions",
                methodModifier="structure",
                styleModifier_list=["jira", "story", "faq", "bullets"],
                directionalModifier="fog",
            )

            _ = modelPrompt(m)

            # System prompt should see the raw, spoken style description.
            self.assertEqual(
                GPTState.system_prompt.style, "jira story faq bullets"
            )

            # last_style should include at most 3 tokens drawn from the input set.
            style_tokens = GPTState.last_style.split()
            self.assertLessEqual(len(style_tokens), 3)
            self.assertTrue(
                set(style_tokens).issubset({"jira", "story", "faq", "bullets"})
            )

            # last_recipe should reflect the capped, canonicalised style tokens.
            recipe_parts = [p.strip() for p in GPTState.last_recipe.split("·")]
            style_part = recipe_parts[4]
            style_part_tokens = style_part.split()
            self.assertLessEqual(len(style_part_tokens), 3)
            self.assertTrue(
                set(style_part_tokens).issubset({"jira", "story", "faq", "bullets"})
            )

        def test_model_prompt_updates_last_recipe_with_profile_axes(self):
            # When no spoken modifiers are provided, the per-prompt profile for
            # "todo" should drive the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="todo",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(
                GPTState.last_recipe,
                "todo · gist · actions · steps · checklist",
            )
            self.assertEqual(GPTState.last_static_prompt, "todo")
            self.assertEqual(GPTState.last_completeness, "gist")
            self.assertEqual(GPTState.last_scope, "actions")
            self.assertEqual(GPTState.last_method, "steps")
            self.assertEqual(GPTState.last_style, "checklist")
            self.assertEqual(GPTState.last_directional, "DIR")

        def test_model_prompt_uses_profiles_for_filter_style_prompts(self):
            # Filter-style prompts like "pain" should drive method/style/scope
            # via their profiles when no spoken modifiers are present.
            m = SimpleNamespace(
                staticPrompt="pain",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "gist")
            self.assertEqual(GPTState.system_prompt.scope, "focus")
            self.assertEqual(GPTState.system_prompt.method, "filter")
            self.assertEqual(GPTState.system_prompt.style, "bullets")

        def test_model_prompt_uses_relations_scope_for_dependency_prompts(self):
            # Relationship-style prompts like "dependency" should use the
            # relational scope profile when present.
            m = SimpleNamespace(
                staticPrompt="dependency",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.scope, "relations")

else:
    if not TYPE_CHECKING:
        class ModelPromptModifiersTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
