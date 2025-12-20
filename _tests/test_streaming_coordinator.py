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
        new_streaming_session,
        canvas_view_from_snapshot,
        current_streaming_snapshot,
        record_streaming_snapshot,
        current_streaming_gating_summary,
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

        def test_new_streaming_session_resets_gating_summary(self) -> None:
            GPTState.last_streaming_snapshot = {
                "request_id": "req-old",
                "gating_drop_counts": {"in_flight": 2},
                "gating_drop_total": 2,
                "gating_drop_last": {"reason": "in_flight", "reason_count": 2},
            }

            session = new_streaming_session("req-new")
            self.assertEqual(session.request_id, "req-new")

            summary = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(summary, {})

        def test_current_streaming_gating_summary_returns_counts(self) -> None:
            session = new_streaming_session("req-gating")
            session.record_gating_drop(reason="in_flight", phase="SENDING")
            summary = current_streaming_gating_summary()
            self.assertEqual(summary.get("total"), 1)
            self.assertEqual(summary.get("counts", {}).get("in_flight"), 1)
            self.assertEqual(
                summary.get("counts_sorted"),
                [{"reason": "in_flight", "count": 1}],
            )
            self.assertEqual(
                summary.get("last"),
                {"reason": "in_flight", "reason_count": 1},
            )

            session.record_gating_drop(reason="history_save_failed", phase="SAVE")
            summary = current_streaming_gating_summary()
            self.assertEqual(summary.get("total"), 2)
            counts = summary.get("counts", {})
            self.assertEqual(counts.get("in_flight"), 1)
            self.assertEqual(counts.get("history_save_failed"), 1)
            self.assertEqual(
                summary.get("counts_sorted"),
                [
                    {"reason": "history_save_failed", "count": 1},
                    {"reason": "in_flight", "count": 1},
                ],
            )
            self.assertEqual(
                summary.get("last"),
                {"reason": "history_save_failed", "reason_count": 1},
            )

        def test_record_complete_emits_gating_summary_event(self) -> None:
            session = new_streaming_session("req-gating-complete")
            session.record_gating_drop(
                reason="in_flight", phase="SENDING", source="gpt.apply"
            )
            session.record_gating_drop(
                reason="history_save_failed", phase="SAVE", source="history"
            )
            session.record_gating_drop(
                reason="in_flight", phase="STREAMING", source="gpt.apply"
            )

            snapshot = session.record_complete()
            self.assertTrue(snapshot.get("completed"))
            self.assertFalse(snapshot.get("errored"))

            self.assertGreaterEqual(len(session.events), 2)
            self.assertEqual(session.events[-2].get("kind"), "complete")

            summary_event = session.events[-1]
            self.assertEqual(summary_event.get("kind"), "gating_summary")
            self.assertEqual(summary_event.get("status"), "completed")
            self.assertEqual(summary_event.get("total"), 3)

            counts = summary_event.get("counts", {})
            self.assertEqual(counts.get("in_flight"), 2)
            self.assertEqual(counts.get("history_save_failed"), 1)

            self.assertEqual(
                summary_event.get("counts_sorted"),
                [
                    {"reason": "in_flight", "count": 2},
                    {"reason": "history_save_failed", "count": 1},
                ],
            )

            sources = summary_event.get("sources", {})
            self.assertEqual(sources.get("gpt.apply"), 2)
            self.assertEqual(sources.get("history"), 1)

            self.assertEqual(
                summary_event.get("sources_sorted"),
                [
                    {"source": "gpt.apply", "count": 2},
                    {"source": "history", "count": 1},
                ],
            )

            last_drop = summary_event.get("last", {})
            self.assertEqual(last_drop.get("reason"), "in_flight")
            self.assertEqual(last_drop.get("reason_count"), 2)

            last_source = summary_event.get("last_source", {})
            self.assertEqual(last_source.get("source"), "gpt.apply")
            self.assertEqual(last_source.get("count"), 2)

            summary_snapshot = current_streaming_gating_summary()
            self.assertEqual(summary_snapshot.get("status"), "completed")

        def test_record_error_emits_gating_summary_event(self) -> None:
            session = new_streaming_session("req-gating-error")

            snapshot = session.record_error("timeout")
            self.assertTrue(snapshot.get("errored"))
            self.assertFalse(snapshot.get("completed"))

            self.assertGreaterEqual(len(session.events), 2)
            self.assertEqual(session.events[-2].get("kind"), "error")

            summary_event = session.events[-1]
            self.assertEqual(summary_event.get("kind"), "gating_summary")
            self.assertEqual(summary_event.get("status"), "errored")
            self.assertEqual(summary_event.get("total"), 0)
            self.assertEqual(summary_event.get("counts"), {})
            self.assertEqual(summary_event.get("counts_sorted"), [])
            self.assertEqual(summary_event.get("sources"), {})
            self.assertEqual(summary_event.get("sources_sorted"), [])
            self.assertEqual(summary_event.get("last"), {})
            self.assertEqual(summary_event.get("last_source"), {})

            summary_snapshot = current_streaming_gating_summary()
            self.assertEqual(summary_snapshot.get("status"), "errored")


else:
    if not TYPE_CHECKING:

        class StreamingCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
