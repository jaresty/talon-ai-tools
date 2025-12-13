import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpCanvas import (
        static_prompt_settings_catalog,
        COMPLETENESS_KEYS,
        SCOPE_KEYS,
        METHOD_KEYS,
        FORM_KEYS,
        CHANNEL_KEYS,
    )
    from talon_user.lib.axisCatalog import axis_catalog

    class ModelHelpCanvasCatalogTests(unittest.TestCase):
        def test_static_prompt_settings_catalog_matches_axis_catalog_profiled(self) -> None:
            """Guardrail: quick-help static prompt settings catalog matches axis catalog profiled list."""

            catalog = axis_catalog()
            profiled_names = {entry["name"] for entry in catalog["static_prompts"]["profiled"]}
            settings_catalog = static_prompt_settings_catalog()

            missing = profiled_names - set(settings_catalog.keys())
            self.assertFalse(
                missing,
                f"static_prompt_settings_catalog missing profiled prompts from axis_catalog: {sorted(missing)}",
            )

        def test_axis_keys_match_catalog_axes(self) -> None:
            """Guardrail: quick-help axis key lists follow axis_catalog tokens."""

            catalog = axis_catalog()
            axes = catalog["axes"]
            self.assertEqual(set(COMPLETENESS_KEYS), set(axes["completeness"].keys()))
            self.assertEqual(set(SCOPE_KEYS), set(axes["scope"].keys()))
            self.assertEqual(set(METHOD_KEYS), set(axes["method"].keys()))
            self.assertEqual(set(FORM_KEYS), set(axes["form"].keys()))
            self.assertEqual(set(CHANNEL_KEYS), set(axes["channel"].keys()))
else:
    if not TYPE_CHECKING:

        class ModelHelpCanvasCatalogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
