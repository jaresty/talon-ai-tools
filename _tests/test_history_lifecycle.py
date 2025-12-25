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
            consume_gating_drop_stats,
            history_axes_for,
            history_validation_stats,
            record_gating_drop,
        )

        self._axes_snapshot_from_axes = axes_snapshot_from_axes
        self._history_axes_for = history_axes_for
        self._consume_gating_drop_stats = consume_gating_drop_stats
        self._history_validation_stats = history_validation_stats
        self._record_gating_drop = record_gating_drop

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

    def test_history_validation_stats_exposes_gating_counts(self) -> None:
        self._consume_gating_drop_stats()
        self._record_gating_drop("in_flight", source="history_lifecycle_test")
        stats = self._history_validation_stats()
        summary = stats.get("streaming_gating_summary", {}) or {}
        counts = summary.get("counts", {}) or {}
        self.assertEqual(counts.get("in_flight"), 1)
        self.assertEqual(summary.get("total"), 1)
        self.assertEqual(stats.get("gating_drop_total"), 1)
        self._consume_gating_drop_stats()
