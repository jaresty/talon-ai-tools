import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestLog import _filter_axes_payload, axis_snapshot_from_axes

    class RequestLogAxisFilterTests(unittest.TestCase):
        def test_keeps_only_known_axis_tokens_and_drops_hydrated(self) -> None:
            axes = {
                "scope": ["bound", "unknown", "Important: hydrated value"],
                "method": ["steps", ""],
            }

            filtered = _filter_axes_payload(axes)

            self.assertEqual(filtered["scope"], ["bound"])
            self.assertEqual(filtered["method"], ["steps"])

        def test_drops_unknown_axis_keys(self) -> None:
            axes = {"custom": ["value", ""]}

            filtered = _filter_axes_payload(axes)

            self.assertNotIn("custom", filtered)

        def test_axis_snapshot_matches_filtered_axes_payload(self) -> None:
            axes = {
                "scope": ["bound", "edges"],
                "method": ["rigor", "steps"],
                "form": ["code"],
                "channel": ["slack"],
                "directional": ["fog"],
                "custom": ["value", ""],
            }

            filtered = _filter_axes_payload(axes)
            snapshot = axis_snapshot_from_axes(axes)

            self.assertEqual(snapshot.as_dict(), filtered)
            self.assertNotIn("custom", snapshot)

        def test_axis_snapshot_is_immutable(self) -> None:
            axes = {
                "scope": ["focus"],
                "method": ["steps"],
                "directional": ["fog"],
            }

            snapshot = axis_snapshot_from_axes(axes)

            self.assertIsInstance(snapshot.axes["scope"], tuple)
            with self.assertRaises(TypeError):
                snapshot.axes["scope"] += ("bound",)

            mutated = snapshot.as_dict()
            mutated["scope"].append("extra")
            self.assertEqual(snapshot.get("scope"), ["focus"])
            self.assertNotIn("custom", snapshot)

        def test_caps_and_style_rejection(self) -> None:
            axes = {
                "scope": ["bound", "edges", "focus"],
                "method": ["rigor", "xp", "steps", "plan"],
                "form": ["code", "table"],
                "channel": ["slack", "jira"],
                "directional": ["fog", "rog"],
                "style": ["plain"],
            }

            with self.assertRaisesRegex(ValueError, "style axis is removed"):
                _filter_axes_payload(axes)

else:
    if not TYPE_CHECKING:

        class RequestLogAxisFilterTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
