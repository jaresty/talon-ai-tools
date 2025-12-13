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
        static_prompt_settings_catalog,
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
            self.assertEqual(axes["completeness"], "gist")
            self.assertEqual(axes["method"], ["steps"])
            self.assertEqual(axes["form"], ["checklist"])
            self.assertEqual(axes["scope"], ["actions"])

        def test_get_static_prompt_axes_is_empty_for_description_only_profile(
            self,
        ) -> None:
            # "describe" only has a description, no axis fields.
            self.assertIn("describe", STATIC_PROMPT_CONFIG)
            axes = get_static_prompt_axes("describe")
            self.assertEqual(axes, {})

        def test_get_static_prompt_axes_is_empty_for_unknown_prompt(self) -> None:
            self.assertEqual(get_static_prompt_axes("nonexistent-static-prompt"), {})

        def test_static_prompt_axes_include_clustered_tokens(self) -> None:
            # Spot-check a few prompts that use clustered axis tokens introduced by ADR 014.
            bridge_axes = get_static_prompt_axes("bridge")
            self.assertEqual(bridge_axes.get("completeness"), "path")

            effects_axes = get_static_prompt_axes("effects")
            self.assertEqual(effects_axes.get("scope"), ["dynamics"])

            context_axes = get_static_prompt_axes("context")
            self.assertEqual(context_axes.get("method"), ["contextualise"])

        def test_ticket_static_prompt_uses_multi_tag_axes(self) -> None:
            """Static prompt 'ticket' should expose multi-tag axis defaults."""
            axes = get_static_prompt_axes("ticket")
            self.assertIsNotNone(axes)
            self.assertEqual(axes.get("completeness"), "full")
            self.assertEqual(axes.get("scope"), ["actions"])
            self.assertEqual(axes.get("method"), ["structure"])
            # Form/channel defaults should include story form and jira channel tokens.
            form_values = axes.get("form")
            channel_values = axes.get("channel")
            self.assertEqual(form_values, ["story"])
            self.assertEqual(channel_values, ["jira"])

        def test_static_prompt_settings_catalog_matches_profiles(self) -> None:
            catalog = static_prompt_settings_catalog()
            for name, profile in STATIC_PROMPT_CONFIG.items():
                self.assertIn(name, catalog)
                entry = catalog[name]
                self.assertEqual(
                    entry["description"],
                    profile.get("description", "").strip(),
                )
                self.assertEqual(entry["axes"], get_static_prompt_axes(name))


else:
    if not TYPE_CHECKING:

        class StaticPromptConfigDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
