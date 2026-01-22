import unittest
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    try:
        from bootstrap import bootstrap
    except ModuleNotFoundError:
        bootstrap = None
    else:
        bootstrap()

    from talon_user.lib import talonSettings

    class TalonSettingsCatalogListsTests(unittest.TestCase):
        def test_runtime_lists_populated_from_catalog(self) -> None:
            """Guardrail: runtime lists populate from catalog even without on-disk Talon lists."""

            # Clear lists before repopulating.
            if hasattr(talonSettings.ctx, "lists"):
                talonSettings.ctx.lists.clear()

            talonSettings._populate_runtime_lists_from_catalog()

            # Expect staticPrompt and core axes to be populated from catalog tokens.
            lists = getattr(talonSettings.ctx, "lists", {})
            self.assertIn("user.staticPrompt", lists)
            self.assertIn("user.completenessModifier", lists)
            self.assertIn("user.scopeModifier", lists)
            self.assertIn("user.methodModifier", lists)
            self.assertIn("user.formModifier", lists)
            self.assertIn("user.channelModifier", lists)
            self.assertIn("user.directionalModifier", lists)

            # Spot-check a few known tokens from the catalog.
            self.assertIn("make", lists["user.staticPrompt"])
            self.assertIn("full", lists["user.completenessModifier"])
            self.assertIn("steps", lists["user.methodModifier"])

        def test_runtime_lists_merge_axis_tokens_from_catalog(self) -> None:
            """Guardrail: runtime lists should include SSOT axis tokens even if list tokens are partial."""

            fake_catalog = {
                "axes": {
                    "completeness": {"full": "Full", "gist": "Gist"},
                    "scope": {"narrow": "Narrow"},
                    "method": {"steps": "Steps"},
                    "form": {"bullets": "Bullets"},
                    "channel": {"slack": "Slack"},
                    "directional": {"fog": "Fog"},
                },
                # Simulate partial list tokens (missing gist).
                "axis_list_tokens": {"completeness": ["full"]},
                "static_prompts": {"profiled": [{"name": "describe", "axes": {}, "description": ""}]},
            }

            # Clear lists before repopulating.
            if hasattr(talonSettings.ctx, "lists"):
                talonSettings.ctx.lists.clear()

            # Patch axis_catalog to return the fake catalog during this test.
            original_axis_catalog = talonSettings.axis_catalog
            talonSettings.axis_catalog = lambda: fake_catalog  # type: ignore[assignment]
            try:
                talonSettings._populate_runtime_lists_from_catalog()
            finally:
                talonSettings.axis_catalog = original_axis_catalog  # type: ignore[assignment]

            lists = getattr(talonSettings.ctx, "lists", {})
            self.assertIn("gist", lists["user.completenessModifier"], "Expected SSOT tokens to appear even if missing from list tokens")

else:

    class TalonSettingsCatalogListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
