import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.historyLifecycle import (
        filter_axes_payload,
        axis_snapshot_from_axes,
    )

    class RequestLogAxisFilterTests(unittest.TestCase):
        def test_keeps_only_known_axis_tokens_and_drops_hydrated(self) -> None:
            axes = {
                "scope": ["struct", "unknown", "Important: hydrated value"],
                "method": ["flow", ""],
            }

            filtered = filter_axes_payload(axes)

            self.assertEqual(filtered["scope"], ["struct"])
            self.assertEqual(filtered["method"], ["flow"])

        def test_drops_unknown_axis_keys(self) -> None:
            axes = {"custom": ["value", ""]}

            filtered = filter_axes_payload(axes)

            self.assertNotIn("custom", filtered)

        def test_axis_snapshot_matches_filtered_axes_payload(self) -> None:
            axes = {
                "scope": ["struct", "time"],
                "method": ["rigor", "flow"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
                "custom": ["value", ""],
            }

            filtered = filter_axes_payload(axes)
            snapshot = axis_snapshot_from_axes(axes)

            self.assertEqual(snapshot.as_dict(), filtered)
            self.assertNotIn("custom", snapshot)

        def test_axis_snapshot_is_immutable(self) -> None:
            axes = {
                "scope": ["struct"],
                "method": ["flow"],
                "directional": ["fog"],
            }

            snapshot = axis_snapshot_from_axes(axes)

            self.assertIsInstance(snapshot.axes["scope"], tuple)
            with self.assertRaises(TypeError):
                snapshot.axes["scope"] += ("time",)

            mutated = snapshot.as_dict()
            mutated["scope"].append("extra")
            self.assertEqual(snapshot.get("scope"), ["struct"])
            self.assertNotIn("custom", snapshot)

        def test_caps_and_style_rejection(self) -> None:
            axes = {
                "scope": ["struct", "time", "act"],
                "method": ["rigor", "flow", "analysis", "diagnose"],
                "form": ["bullets", "table"],
                "channel": ["slack", "jira"],
                "directional": ["fog", "rog"],
                "style": ["plain"],
            }

            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                filter_axes_payload(axes)

else:
    if not TYPE_CHECKING:

        class RequestLogAxisFilterTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
