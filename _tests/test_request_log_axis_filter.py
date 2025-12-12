import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestLog import _filter_axes_payload

    class RequestLogAxisFilterTests(unittest.TestCase):
        def test_keeps_only_known_axis_tokens_and_drops_hydrated(self) -> None:
            axes = {
                "scope": ["bound", "unknown", "Important: hydrated value"],
                "method": ["steps", ""],
            }

            filtered = _filter_axes_payload(axes)

            self.assertEqual(filtered["scope"], ["bound"])
            self.assertEqual(filtered["method"], ["steps"])

        def test_passthrough_unknown_axis_keys(self) -> None:
            axes = {"custom": ["value", ""]}

            filtered = _filter_axes_payload(axes)

            self.assertEqual(filtered["custom"], ["value"])

else:
    if not TYPE_CHECKING:

        class RequestLogAxisFilterTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
