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
            profile = get_static_prompt_profile("probe")
            self.assertIsNotNone(profile)
            # Sanity-check a couple of known fields so this stays aligned with
            # the configuration but does not over-specify it.
            self.assertEqual(
                profile["description"],
                "The response decomposes, reasons about, or interprets the subject to reveal structure or insight beyond restatement.",
            )
            self.assertEqual(profile["method"], "analysis")

        def test_get_static_prompt_profile_returns_none_for_unknown_prompt(
            self,
        ) -> None:
            self.assertIsNone(get_static_prompt_profile("nonexistent-static-prompt"))

        def test_get_static_prompt_axes_returns_axes_subset_for_profile(
            self,
        ) -> None:
            axes = get_static_prompt_axes("probe")
            # "probe" has an axis profile with method=analysis in the configuration.
            # get_static_prompt_axes normalizes axes to lists.
            self.assertEqual(axes["method"], ["analysis"])

        def test_get_static_prompt_axes_is_empty_for_description_only_profile(
            self,
        ) -> None:
            # "show" only has a description, no axis fields.
            self.assertIn("show", STATIC_PROMPT_CONFIG)
            axes = get_static_prompt_axes("show")
            self.assertEqual(axes, {})

        def test_get_static_prompt_axes_is_empty_for_unknown_prompt(self) -> None:
            self.assertEqual(get_static_prompt_axes("nonexistent-static-prompt"), {})

        def test_static_prompt_axes_include_single_axis_values(self) -> None:
            # Per ADR 0088: universal task taxonomy uses single axis values.
            # Note: get_static_prompt_axes normalizes all axes to lists.
            # Check that "probe" has a method axis value.
            probe_axes = get_static_prompt_axes("probe")
            self.assertEqual(probe_axes.get("method"), ["analysis"])

            # Check that "pick" has a method axis value.
            pick_axes = get_static_prompt_axes("pick")
            self.assertEqual(pick_axes.get("method"), ["converge"])

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
            # Per ADR 0088: universal task "plan" is exempt from this guardrail because
            # "sequence" and "steps" are definitional to what planning success means.
            exempt_tasks = {"plan"}

            for name, profile in STATIC_PROMPT_CONFIG.items():
                description = profile.get("description", "")
                self.assertTrue(
                    description.startswith("The response "),
                    f"Static prompt {name!r} must start descriptions with 'The response'.",
                )
                if name in exempt_tasks:
                    continue
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
