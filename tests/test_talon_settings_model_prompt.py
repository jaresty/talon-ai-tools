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
                goalModifier="GOAL",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # With no explicit axis modifiers, we should get a Task / Constraints
            # schema with a profile-driven completeness/scope hint and the lens
            # appended after a blank line.
            self.assertIn("Task:", result)
            self.assertIn("Constraints:", result)
            self.assertIn(
                "Fix grammar, spelling, and minor style issues while keeping meaning and tone; return only the modified text.GOAL",
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
                goalModifier="GOAL",
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
                goalModifier="GOAL",
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

        def test_missing_scope_method_style_do_not_add_text(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
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
                goalModifier="GOAL",
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
                goalModifier="",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "gist")
            self.assertEqual(GPTState.system_prompt.scope, "focus")
            self.assertEqual(GPTState.system_prompt.method, "steps")
            self.assertEqual(GPTState.system_prompt.style, "bullets")

        def test_model_prompt_applies_code_style_for_gherkin(self):
            m = SimpleNamespace(
                staticPrompt="gherkin",
                goalModifier="",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(GPTState.system_prompt.completeness, "full")
            self.assertEqual(GPTState.system_prompt.scope, "bound")
            self.assertEqual(GPTState.system_prompt.style, "code")

        def test_clear_all_resets_last_recipe_and_response(self):
            # Exercise the lifecycle: after a prompt, clear_all should drop
            # last_response/last_recipe so recap helpers don't show stale data.
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
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

        def test_model_prompt_updates_last_recipe_with_spoken_modifiers(self):
            # Spoken modifiers should be reflected in the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
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

        def test_model_prompt_updates_last_recipe_with_profile_axes(self):
            # When no spoken modifiers are provided, the per-prompt profile for
            # "todo" should drive the last_recipe summary.
            m = SimpleNamespace(
                staticPrompt="todo",
                goalModifier="",
                directionalModifier="DIR",
            )

            _ = modelPrompt(m)

            self.assertEqual(
                GPTState.last_recipe,
                "todo · gist · focus · steps · bullets",
            )

else:
    if not TYPE_CHECKING:
        class ModelPromptModifiersTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
