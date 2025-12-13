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

            filtered, legacy = _filter_axes_payload(axes)

            self.assertEqual(filtered["scope"], ["bound"])
            self.assertEqual(filtered["method"], ["steps"])
            self.assertFalse(legacy)

        def test_passthrough_unknown_axis_keys(self) -> None:
            axes = {"custom": ["value", ""]}

            filtered, legacy = _filter_axes_payload(axes)

            self.assertEqual(filtered["custom"], ["value"])
            self.assertFalse(legacy)

        def test_caps_and_style_rejection(self) -> None:
            axes = {
                "scope": ["bound", "edges", "focus"],
                "method": ["rigor", "xp", "steps", "plan"],
                "form": ["code", "table"],
                "channel": ["slack", "jira"],
                "directional": ["fog", "rog"],
                "style": ["plain"],
            }

            filtered, legacy = _filter_axes_payload(axes)

            self.assertEqual(filtered["scope"], ["edges", "focus"])
            self.assertEqual(filtered["method"], ["plan", "steps", "xp"])
            self.assertEqual(filtered["form"], ["table"])
            self.assertEqual(filtered["channel"], ["jira"])
            # Directional is now capped to a single value (last wins).
            self.assertEqual(filtered["directional"], ["rog"])
            self.assertNotIn("style", filtered)
            self.assertTrue(legacy)

else:
    if not TYPE_CHECKING:

        class RequestLogAxisFilterTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
