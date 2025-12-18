import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib import requestHistoryActions
    from talon_user.lib import requestLog

    class AxisSnapshotAlignmentTests(unittest.TestCase):
        def test_request_history_actions_snapshot_matches_request_log_snapshot(
            self,
        ) -> None:
            axes = {
                "completeness": ["full"],
                "scope": ["focus", "unknown-scope"],
                "method": ["steps", "Important: hydrated"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
                # Ensure passthrough keys remain stable.
                "extra": ["keep"],
            }

            self.assertEqual(
                requestHistoryActions.axis_snapshot_from_axes(axes),
                requestLog.axis_snapshot_from_axes(axes),
            )

else:
    if not TYPE_CHECKING:

        class AxisSnapshotAlignmentTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
