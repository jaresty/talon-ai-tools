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
        static_prompt_catalog,
    )

    class StaticPromptCatalogConsistencyTests(unittest.TestCase):
        def test_catalog_unprofiled_tokens_match_talon_minus_profiles(self) -> None:
            """Guardrail: catalog's unprofiled_tokens should be talon list minus profiled names."""

            catalog = static_prompt_catalog()

            profiled_names = {entry["name"] for entry in catalog["profiled"]}
            talon_tokens = set(catalog["talon_list_tokens"])
            unprofiled_tokens = set(catalog["unprofiled_tokens"])

            self.assertEqual(
                unprofiled_tokens,
                talon_tokens - profiled_names,
                "unprofiled_tokens should exactly reflect talon list tokens not present in profiles",
            )

        def test_catalog_axes_match_get_static_prompt_axes(self) -> None:
            """Guardrail: catalog axes should match get_static_prompt_axes for each profiled prompt."""

            catalog = static_prompt_catalog()

            by_name = {entry["name"]: entry for entry in catalog["profiled"]}

            for name, _profile in STATIC_PROMPT_CONFIG.items():
                with self.subTest(static_prompt=name):
                    expected_axes = get_static_prompt_axes(name)
                    entry = by_name.get(name)
                    if not expected_axes and entry is None:
                        # No profile axes configured and no catalog entry; nothing to check.
                        continue
                    self.assertIsNotNone(
                        entry,
                        f"static_prompt_catalog is missing entry for profiled prompt {name!r}",
                    )
                    axes = entry["axes"]
                    self.assertEqual(
                        axes,
                        expected_axes,
                        f"Catalog axes for {name!r} do not match get_static_prompt_axes",
                    )

        def test_catalog_descriptions_match_static_prompt_config(self) -> None:
            """Guardrail: catalog descriptions mirror STATIC_PROMPT_CONFIG."""

            catalog = static_prompt_catalog()
            by_name = {entry["name"]: entry for entry in catalog["profiled"]}

            for name, profile in STATIC_PROMPT_CONFIG.items():
                entry = by_name.get(name)
                if entry is None:
                    # Some config-only prompts may not be exposed via the catalog; skip those.
                    continue

                expected_description = (profile or {}).get("description", "") or ""
                self.assertEqual(
                    entry.get("description", "") or "",
                    expected_description,
                    f"Catalog description for {name!r} does not match STATIC_PROMPT_CONFIG",
                )

else:
    if not TYPE_CHECKING:

        class StaticPromptCatalogConsistencyTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
