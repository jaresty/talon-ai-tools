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
            self.assertEqual(
                profile["description"],
                "The response formats the content as a todo list.",
            )
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
            done_axes = get_static_prompt_axes("done")
            self.assertEqual(done_axes.get("form"), ["checklist"])
            self.assertEqual(done_axes.get("scope"), ["actions"])

            wardley_axes = get_static_prompt_axes("wardley")
            self.assertEqual(wardley_axes.get("form"), ["table"])
            self.assertEqual(wardley_axes.get("method"), ["steps"])

            context_axes = get_static_prompt_axes("context")
            self.assertEqual(context_axes.get("method"), ["contextualise"])

        def test_ticket_static_prompt_is_migrated_to_form_channel_axes(self) -> None:
            """The former 'ticket' prompt now lives on form/channel axes (ADR 050)."""
            axes = get_static_prompt_axes("ticket")
            self.assertEqual(axes, {})
            self.assertNotIn("ticket", STATIC_PROMPT_CONFIG)

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

        def test_static_prompt_descriptions_remain_declarative(self) -> None:
            banned_patterns = (
                " apply",
                " applies",
                " applying",
                " outline",
                " outlines",
                " plan ",
                " plan.",
                " plans",
                " process",
                " sequence",
                " step",
                " steps",
                " recommend",
            )
            for name, profile in STATIC_PROMPT_CONFIG.items():
                description = profile.get("description", "")
                self.assertTrue(
                    description.startswith("The response "),
                    f"Static prompt {name!r} must start descriptions with 'The response'.",
                )
                lower = description.lower()
                for pattern in banned_patterns:
                    self.assertNotIn(
                        pattern,
                        lower,
                        f"Static prompt {name!r} description should avoid procedural phrasing containing {pattern.strip()}.",
                    )

        def test_static_prompt_names_do_not_overlap_methods(self) -> None:
            method_tokens = set(AXIS_KEY_TO_VALUE["method"].keys())
            overlap = method_tokens & set(STATIC_PROMPT_CONFIG.keys())
            self.assertFalse(
                overlap,
                f"Static prompt tokens must not overlap method axis tokens (found {sorted(overlap)})",
            )


else:
    if not TYPE_CHECKING:

        class StaticPromptConfigDomainTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
