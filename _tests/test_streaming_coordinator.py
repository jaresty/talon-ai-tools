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
    )

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


else:
    if not TYPE_CHECKING:

        class StreamingCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
