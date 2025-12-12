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
    from talon_user.scripts.tools.generate_axis_config import (
        render_axis_config,
        render_axis_markdown,
    )

    class AxisConfigGeneratorTests(unittest.TestCase):
        def test_render_matches_current_axis_config_mapping(self) -> None:
            rendered = render_axis_config()
            globals_dict: dict[str, object] = {}
            exec(rendered, globals_dict)
            generated = globals_dict.get("AXIS_KEY_TO_VALUE")
            self.assertEqual(
                generated,
                AXIS_KEY_TO_VALUE,
                "Generated axis config map must match current axisConfig AXIS_KEY_TO_VALUE",
            )

        def test_markdown_includes_all_axes_and_tokens(self) -> None:
            markdown = render_axis_markdown()
            for axis, mapping in AXIS_KEY_TO_VALUE.items():
                with self.subTest(axis=axis):
                    self.assertIn(f"## {axis}", markdown)
                    for token in mapping.keys():
                        self.assertIn(f"- {token}", markdown)

else:
    if not TYPE_CHECKING:

        class AxisConfigGeneratorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
