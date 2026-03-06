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

            # Validate execution safety - check for unexpected global variables
            expected_globals = {"AXIS_KEY_TO_VALUE", "__builtins__"}
            allowed_helpers = {
                'AXIS_KEY_TO_LABEL', 'AXIS_KEY_TO_GUIDANCE', 'AXIS_KEY_TO_USE_WHEN',
                'AXIS_KEY_TO_KANJI', 'AXIS_KEY_TO_CATEGORY', 'AXIS_KEY_TO_ROUTING_CONCEPT',
                'AXIS_KEY_TO_AXIS_DESC', 'CROSS_AXIS_COMPOSITION', 'FORM_DEFAULT_COMPLETENESS',
                'USAGE_PATTERNS', 'AxisDoc', 'axis_key_to_value_map', 'axis_key_to_label_map',
                'axis_key_to_guidance_map', 'axis_key_to_use_when_map', 'axis_key_to_kanji_map',
                'axis_key_to_category_map', 'axis_key_to_routing_concept_map',
                'axis_key_to_axis_desc', 'get_cross_axis_composition', 'axis_docs_for',
                'axis_docs_index', 'get_usage_patterns', 'dataclass', 'field', 'Any', 'Dict',
                'FrozenSet', 'TypedDict', 'Union', 'annotations', '__doc__', '__annotations__',
                '__conditional_annotations__',
                # ADR-0155: axis token structured metadata
                'AxisTokenDistinction', 'AxisTokenMetadata', 'AXIS_TOKEN_METADATA', 'axis_token_metadata',
            }
            unexpected_globals = set(globals_dict.keys()) - expected_globals - allowed_helpers
            if unexpected_globals:
                self.fail(
                    f"Generated code created unexpected global variables: {unexpected_globals}. "
                    "This indicates potential side effects or namespace pollution."
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
