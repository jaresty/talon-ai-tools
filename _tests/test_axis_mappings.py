import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import axisMappings

    class AxisMappingsTests(unittest.TestCase):
        def test_axis_docs_map_returns_descriptions(self) -> None:
            mapping = axisMappings.axis_docs_map("completeness")
            self.assertIn("full", mapping)
            self.assertIn("The response", mapping["full"])

        def test_axis_hydrate_token_prefers_description_and_passthrough(self) -> None:
            hydrated = axisMappings.axis_hydrate_token("scope", "focus")
            self.assertNotEqual(hydrated, "")
            self.assertNotEqual(hydrated, "focus")
            # Unknown tokens should pass through unchanged.
            self.assertEqual(
                axisMappings.axis_hydrate_token("scope", "unknown"), "unknown"
            )

else:
    if not TYPE_CHECKING:

        class AxisMappingsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
