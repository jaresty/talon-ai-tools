import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.staticPromptConfig import (
        STATIC_PROMPT_CONFIG,
        get_static_prompt_axes,
        get_static_prompt_profile,
    )

    class StaticPromptConfigDomainTests(unittest.TestCase):
        def test_get_static_prompt_profile_returns_profile_when_present(self) -> None:
            profile = get_static_prompt_profile("todo")
            self.assertIsNotNone(profile)
            # Sanity-check a couple of known fields so this stays aligned with
            # the configuration but does not over-specify it.
            self.assertEqual(profile["description"], "Format this as a todo list.")
            self.assertEqual(profile["completeness"], "gist")

        def test_get_static_prompt_profile_returns_none_for_unknown_prompt(
            self,
        ) -> None:
            self.assertIsNone(get_static_prompt_profile("nonexistent-static-prompt"))

        def test_get_static_prompt_axes_returns_axes_subset_for_profile(
            self,
        ) -> None:
            axes = get_static_prompt_axes("todo")
            # "todo" has a full axis profile in the configuration.
            self.assertEqual(
                axes,
                {
                    "completeness": "gist",
                    "method": "steps",
                    "style": "checklist",
                    "scope": "focus",
                },
            )

        def test_get_static_prompt_axes_is_empty_for_description_only_profile(
            self,
        ) -> None:
            # "describe" only has a description, no axis fields.
            self.assertIn("describe", STATIC_PROMPT_CONFIG)
            axes = get_static_prompt_axes("describe")
            self.assertEqual(axes, {})

        def test_get_static_prompt_axes_is_empty_for_unknown_prompt(self) -> None:
            self.assertEqual(get_static_prompt_axes("nonexistent-static-prompt"), {})

else:
    if not TYPE_CHECKING:
        class StaticPromptConfigDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

