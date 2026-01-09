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

    class AxisDescriptionLanguageTests(unittest.TestCase):
        def test_axis_descriptions_start_with_the_response(self) -> None:
            for axis_name, tokens in AXIS_KEY_TO_VALUE.items():
                for token, description in tokens.items():
                    self.assertTrue(
                        description.startswith("The response "),
                        f"Axis {axis_name!r} token {token!r} must start descriptions with 'The response '.",
                    )

else:
    if not TYPE_CHECKING:

        class AxisDescriptionLanguageTests(
            unittest.TestCase
        ):  # pragma: no cover - Talon runtime shim
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
