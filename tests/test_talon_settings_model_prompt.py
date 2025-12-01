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
    from talon_user.lib.talonSettings import modelPrompt

    class ModelPromptModifiersTests(unittest.TestCase):
        def test_no_modifiers_uses_static_prompt_profile_when_present(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            # With no explicit completeness modifier and no completeness profile for "fix",
            # the composed prompt should just be the base plus directional modifier.
            self.assertEqual(result, "fixGOALDIR")

        def test_explicit_completeness_modifier_is_used_as_is(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
                completenessModifier="COMP",
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            self.assertTrue(result.startswith("fixGOAL"))
            self.assertIn("COMP", result)
            self.assertTrue(result.endswith("DIR"))

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

            # Check that all parts are present and ordered.
            self.assertTrue(result.startswith("fixGOAL"))
            self.assertIn("COMP", result)
            self.assertIn("SCOPE", result)
            self.assertIn("METHOD", result)
            self.assertIn("STYLE", result)
            self.assertTrue(result.endswith("DIR"))

            self.assertLess(result.index("COMP"), result.index("SCOPE"))
            self.assertLess(result.index("SCOPE"), result.index("METHOD"))
            self.assertLess(result.index("METHOD"), result.index("STYLE"))

        def test_missing_scope_method_style_do_not_add_text(self):
            m = SimpleNamespace(
                staticPrompt="fix",
                goalModifier="GOAL",
                completenessModifier="COMP",
                # scope/method/style omitted on purpose; per-prompt profile is only for
                # completeness on "fix", so no extra method/style text should appear.
                directionalModifier="DIR",
            )

            result = modelPrompt(m)

            self.assertTrue(result.startswith("fixGOAL"))
            self.assertIn("COMP", result)
            # No placeholder text should appear for scope/method/style when omitted.
            self.assertNotIn("SCOPE", result)
            self.assertNotIn("METHOD", result)
            self.assertNotIn("STYLE", result)
            self.assertTrue(result.endswith("DIR"))

else:
    if not TYPE_CHECKING:
        class ModelPromptModifiersTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
