import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.streamingCoordinator import (
        new_streaming_run,
        record_streaming_chunk,
        record_streaming_error,
        record_streaming_complete,
        canvas_view_from_snapshot,
    )

    class StreamingLifecyclePresenterTests(unittest.TestCase):
        def test_chunk_then_complete_sets_completed_snapshot(self) -> None:
            run = new_streaming_run("req-1")
            snap = record_streaming_chunk(run, "hi")
            self.assertEqual(snap["text"], "hi")
            snap = record_streaming_complete(run)
            self.assertTrue(snap["completed"])
            view = canvas_view_from_snapshot(snap)
            self.assertEqual(view["status"], "completed")

        def test_error_marks_errored_snapshot_and_preserves_text(self) -> None:
            run = new_streaming_run("req-2")
            record_streaming_chunk(run, "partial")
            snap = record_streaming_error(run, "boom")
            self.assertTrue(snap["errored"])
            self.assertEqual(snap["text"], "partial")
            view = canvas_view_from_snapshot(snap)
            self.assertEqual(view["status"], "errored")
            self.assertIn("boom", view["error_message"])

else:
    if not TYPE_CHECKING:

        class StreamingLifecyclePresenterTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
