import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


@unittest.skipIf(bootstrap is None, "Tests disabled inside Talon runtime")
class HistoryLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        from talon_user.lib.historyLifecycle import (  # type: ignore
            axes_snapshot_from_axes,
            history_axes_for,
        )

        self._axes_snapshot_from_axes = axes_snapshot_from_axes
        self._history_axes_for = history_axes_for

    def test_axes_snapshot_normalises_tokens(self) -> None:
        snapshot = self._axes_snapshot_from_axes(
            {
                "completeness": [" full ", "FULL"],
                "scope": [" focus"],
                "method": ["plan", "Plan"],
                "form": ["plain", "Plain"],
                "channel": ["slack"],
                "directional": [" fog", "Fog"],
                "style": ["casual"],
            }
        )
        axes = snapshot.known_axes()
        self.assertEqual(
            axes,
            {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["plan"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            },
        )

    def test_history_axes_for_returns_known_axes(self) -> None:
        axes = self._history_axes_for(
            {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["plan"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
                "unknown": ["drop"],
            }
        )
        self.assertEqual(
            axes,
            {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["plan"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            },
        )
