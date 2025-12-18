import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is None:

    class StreamingSessionTests(unittest.TestCase):
        @unittest.skip("Talon runtime placeholder")
        def test_placeholder(self):
            pass

else:
    from talon_user.lib.modelState import GPTState
    import talon_user.lib.streamingCoordinator as streaming
    from talon_user.lib.streamingCoordinator import new_streaming_session

    class StreamingSessionTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.last_streaming_snapshot = {}
            GPTState.last_streaming_events = []

        def test_session_records_chunks_and_snapshot(self) -> None:
            session = new_streaming_session("rid-session")
            session.record_chunk("Hello")

            snap = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertEqual(snap.get("request_id"), "rid-session")
            self.assertEqual(snap.get("text"), "Hello")
            self.assertFalse(snap.get("completed"))
            self.assertFalse(snap.get("errored"))
            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual([e.get("kind") for e in events], ["chunk"])

        def test_session_complete_after_error_keeps_error(self) -> None:
            session = new_streaming_session("rid-error")
            session.record_chunk("Partial")
            session.record_error("boom")
            session.record_complete()

            snap = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertTrue(snap.get("errored"))
            self.assertFalse(snap.get("completed"))
            self.assertEqual(snap.get("error_message"), "boom")

        def test_session_complete_sets_completed(self) -> None:
            session = new_streaming_session("rid-complete")
            session.record_chunk("Done")
            session.record_complete()

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual([e.get("kind") for e in events], ["chunk", "complete"])

            snap = getattr(GPTState, "last_streaming_snapshot", {})
            self.assertTrue(snap.get("completed"))
            self.assertFalse(snap.get("errored"))
            self.assertEqual(snap.get("text"), "Done")

        def test_session_log_entry_emits_event(self) -> None:
            session = new_streaming_session("rid-log")

            self.assertIs(getattr(GPTState, "last_streaming_session", None), session)

            original = streaming.append_entry_from_request
            streaming.append_entry_from_request = lambda **kwargs: "prompt"  # type: ignore[assignment]
            self.addCleanup(
                lambda: setattr(streaming, "append_entry_from_request", original)
            )

            result = session.record_log_entry(request_id="rid-log")
            self.assertEqual(result, "prompt")

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual(
                [e.get("kind") for e in events],
                ["history_write_requested", "log_entry"],
            )
            self.assertEqual(events[0].get("axes_keys"), [])
            self.assertNotIn("require_directional", events[0])

        def test_session_ui_refresh_records_event(self) -> None:
            session = new_streaming_session("rid-ui")
            session.record_ui_refresh_requested(forced=True, reason="canvas_refresh")
            session.record_ui_refresh_executed(
                forced=True, reason="canvas_refresh", success=True
            )

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual(
                [e.get("kind") for e in events],
                ["ui_refresh_requested", "ui_refresh_executed"],
            )
            self.assertTrue(events[0].get("forced"))
            self.assertEqual(events[0].get("reason"), "canvas_refresh")
            self.assertTrue(events[1].get("success"))

        def test_session_cancel_requested_records_event(self) -> None:
            session = new_streaming_session("rid-cancel")

            class State:
                cancel_requested = True
                phase = "streaming"

            self.assertTrue(session.cancel_requested(State(), source="test"))
            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual([e.get("kind") for e in events], ["cancel_requested"])
            self.assertEqual(events[0].get("source"), "test")
            self.assertEqual(events[0].get("phase"), "streaming")
            self.assertEqual(events[0].get("detail"), "")

        def test_session_cancel_executed_records_event(self) -> None:
            session = new_streaming_session("rid-cancel-ex")
            session.record_cancel_executed(source="iter_lines", emitted=True)

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual([e.get("kind") for e in events], ["cancel_executed"])
            self.assertEqual(events[0].get("source"), "iter_lines")
            self.assertTrue(events[0].get("emitted"))

        def test_session_history_saved_records_event(self) -> None:
            session = new_streaming_session("rid-history")
            session.record_history_saved("/tmp/file.md", success=True)

            events = getattr(GPTState, "last_streaming_events", [])
            self.assertEqual([e.get("kind") for e in events], ["history_saved"])
            self.assertEqual(events[0].get("path"), "/tmp/file.md")
            self.assertTrue(events[0].get("success"))

        def test_session_axes_from_request_filters_unknown_tokens(self) -> None:
            session = new_streaming_session("rid-axes")

            def fake_axis_catalog():
                return {
                    "axes": {
                        "scope": {"focus": {}, "bound": {}},
                        "directional": {"fog": {}, "jog": {}},
                    }
                }

            original_axis_catalog = streaming.axis_catalog
            streaming.axis_catalog = fake_axis_catalog  # type: ignore[assignment]
            self.addCleanup(
                lambda: setattr(streaming, "axis_catalog", original_axis_catalog)
            )

            session.set_axes_from_request(
                {
                    "axes": {
                        "scope": ["focus", "unknown"],
                        "directional": ["fog", "bogus"],
                        "method": ["steps"],
                    }
                }
            )

            self.assertEqual(
                session.run.axes,
                {
                    "scope": ["focus"],
                    "directional": ["fog"],
                },
            )
