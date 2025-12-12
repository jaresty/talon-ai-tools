import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import axisCatalog
    from talon_user.lib.staticPromptConfig import static_prompt_catalog

    class AxisCatalogTests(unittest.TestCase):
        def test_axis_list_tokens_align_with_axis_config(self) -> None:
            """Guardrail: Talon list tokens for axes must match axisConfig tokens."""

            catalog = axisCatalog.axis_catalog()
            axis_map = catalog["axes"]

            for axis_name, tokens in catalog["axis_list_tokens"].items():
                with self.subTest(axis=axis_name):
                    self.assertIn(
                        axis_name,
                        axis_map,
                        f"Axis {axis_name!r} from Talon lists is missing in AXIS_KEY_TO_VALUE",
                    )
                    for token in tokens:
                        self.assertIn(
                            token,
                            axis_map[axis_name],
                            f"Talon list token {token!r} for axis {axis_name!r} missing in AXIS_KEY_TO_VALUE",
                        )

        def test_static_prompt_catalog_passthrough(self) -> None:
            """Guardrail: axis_catalog exposes the same static prompt catalog as staticPromptConfig."""

            catalog = axisCatalog.axis_catalog()
            self.assertEqual(
                catalog["static_prompts"],
                static_prompt_catalog(),
                "axis_catalog static_prompts should mirror static_prompt_catalog()",
            )

else:
    if not TYPE_CHECKING:

        class AxisCatalogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
