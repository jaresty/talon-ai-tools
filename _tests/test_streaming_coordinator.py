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
        StreamingRun,
        new_streaming_run,
        canvas_view_from_snapshot,
        current_streaming_snapshot,
        record_streaming_snapshot,
    )
    from talon_user.lib.modelState import GPTState

    class StreamingCoordinatorTests(unittest.TestCase):
        def test_accumulates_chunks_and_marks_complete(self) -> None:
            run = new_streaming_run("req-1")

            run.on_chunk("hello ")
            run.on_chunk("world")
            run.on_complete()

            self.assertEqual(run.request_id, "req-1")
            self.assertEqual(run.text, "hello world")
            self.assertTrue(run.completed)
            self.assertFalse(run.errored)

            snap = run.snapshot()
            self.assertEqual(snap["request_id"], "req-1")
            self.assertEqual(snap["text"], "hello world")
            self.assertTrue(snap["completed"])
            self.assertFalse(snap["errored"])
            self.assertEqual(snap["error_message"], "")

        def test_error_preserves_chunks_and_blocks_further_appends(self) -> None:
            run = StreamingRun("req-2")
            run.axes = {"method": ["rigor"]}

            run.on_chunk("partial")
            run.on_error("boom")
            # Further chunks should be ignored once errored.
            run.on_chunk(" ignored")

            self.assertTrue(run.errored)
            self.assertFalse(run.completed)
            self.assertEqual(run.error_message, "boom")
            self.assertEqual(run.text, "partial")

            snap = run.snapshot()
            self.assertEqual(snap["text"], "partial")
            self.assertTrue(snap["errored"])
            self.assertFalse(snap["completed"])
            self.assertEqual(snap.get("axes"), {"method": ["rigor"]})

        def test_empty_or_none_chunks_are_ignored(self) -> None:
            run = new_streaming_run("req-3")

            run.on_chunk("")
            run.on_chunk(" ")
            run.on_chunk("ok")

            self.assertEqual(run.text, "ok")

        def test_complete_without_chunks_produces_empty_text(self) -> None:
            run = new_streaming_run("req-4")

            run.on_complete()

            self.assertTrue(run.completed)
            self.assertFalse(run.errored)
            self.assertEqual(run.text, "")
            snap = run.snapshot()
            self.assertEqual(snap["text"], "")
            self.assertTrue(snap["completed"])
            self.assertFalse(snap["errored"])

        def test_error_without_chunks_records_error_and_no_text(self) -> None:
            run = new_streaming_run("req-5")

            run.on_error("timeout")

            self.assertTrue(run.errored)
            self.assertFalse(run.completed)
            self.assertEqual(run.text, "")
            self.assertEqual(run.error_message, "timeout")
            snap = run.snapshot()
            self.assertEqual(snap["text"], "")
            self.assertEqual(snap["error_message"], "timeout")

        def test_complete_after_error_does_not_override_error_state(self) -> None:
            run = new_streaming_run("req-6")

            run.on_chunk("partial")
            run.on_error("cancelled")
            run.on_complete()

            self.assertTrue(run.errored)
            self.assertFalse(run.completed)
            self.assertEqual(run.text, "partial")
            self.assertEqual(run.error_message, "cancelled")

        def test_canvas_view_from_snapshot_maps_status_and_text(self) -> None:
            # Inflight snapshot
            inflight = new_streaming_run("req-inflight")
            inflight.on_chunk("hello ")
            inflight.on_chunk("world")
            inflight_view = canvas_view_from_snapshot(inflight.snapshot())
            self.assertEqual(inflight_view["text"], "hello world")
            self.assertEqual(inflight_view["status"], "inflight")
            self.assertEqual(inflight_view["error_message"], "")

            # Completed snapshot
            completed = new_streaming_run("req-complete")
            completed.on_chunk("done")
            completed.on_complete()
            completed_view = canvas_view_from_snapshot(completed.snapshot())
            self.assertEqual(completed_view["text"], "done")
            self.assertEqual(completed_view["status"], "completed")
            self.assertEqual(completed_view["error_message"], "")

            # Errored snapshot with message
            errored = new_streaming_run("req-error")
            errored.on_chunk("partial")
            errored.on_error("timeout")
            errored_view = canvas_view_from_snapshot(errored.snapshot())
            self.assertEqual(errored_view["text"], "partial")
            self.assertEqual(errored_view["status"], "errored")
            self.assertEqual(errored_view["error_message"], "timeout")

        def test_current_streaming_snapshot_returns_copy(self) -> None:
            GPTState.last_streaming_snapshot = {"text": "abc", "errored": False}
            snap = current_streaming_snapshot()
            self.assertEqual(snap, {"text": "abc", "errored": False})
            # Mutating the returned snapshot should not affect GPTState.
            snap["text"] = "mutated"
            self.assertEqual(
                getattr(GPTState, "last_streaming_snapshot", {}),
                {"text": "abc", "errored": False},
            )

        def test_record_streaming_snapshot_updates_gptstate(self) -> None:
            run = new_streaming_run("req-record")
            run.on_chunk("hello")
            snap = record_streaming_snapshot(run)
            self.assertEqual(snap["text"], "hello")
            self.assertEqual(
                getattr(GPTState, "last_streaming_snapshot", {}),
                snap,
            )


else:
    if not TYPE_CHECKING:

        class StreamingCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
