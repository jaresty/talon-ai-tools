import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestHistory import RequestHistory, RequestLogEntry
    from talon_user.lib import requestLog

    class RequestHistoryTests(unittest.TestCase):
        def test_append_and_latest(self):
            hist = RequestHistory(max_entries=3)
            self.assertIsNone(hist.latest())
            hist.append(RequestLogEntry("r1", "p1", "resp1", "meta1"))
            self.assertEqual(hist.latest().request_id, "r1")  # type: ignore[union-attr]

            hist.append(RequestLogEntry("r2", "p2", "resp2", "meta2"))
            self.assertEqual(hist.latest().request_id, "r2")  # type: ignore[union-attr]

        def test_eviction_and_offset_lookup(self):
            hist = RequestHistory(max_entries=2)
            hist.append(RequestLogEntry("r1", "p1", "resp1"))
            hist.append(RequestLogEntry("r2", "p2", "resp2"))
            # At capacity: oldest is r1, latest is r2.
            self.assertEqual(hist.nth_from_latest(0).request_id, "r2")  # type: ignore[union-attr]
            self.assertEqual(hist.nth_from_latest(1).request_id, "r1")  # type: ignore[union-attr]

            hist.append(RequestLogEntry("r3", "p3", "resp3"))
            # r1 evicted
            self.assertEqual(len(hist), 2)
            self.assertIsNone(hist.nth_from_latest(2))
            self.assertEqual(hist.nth_from_latest(0).request_id, "r3")  # type: ignore[union-attr]
            self.assertEqual(hist.nth_from_latest(1).request_id, "r2")  # type: ignore[union-attr]

        def test_all_returns_oldest_to_newest(self):
            hist = RequestHistory(max_entries=3)
            hist.append(RequestLogEntry("r1", "p1", "resp1"))
            hist.append(RequestLogEntry("r2", "p2", "resp2"))
            hist.append(RequestLogEntry("r3", "p3", "resp3"))
            ids = [entry.request_id for entry in hist.all()]
            self.assertEqual(ids, ["r1", "r2", "r3"])

        def test_append_entry_from_request_captures_provider(self):
            requestLog.clear_history()
            request = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": "hello"}],
                    }
                ]
            }
            requestLog.append_entry_from_request(
                "req-1", request, "resp", provider_id="gemini"
            )
            latest = requestLog.latest()
            assert latest is not None
            self.assertEqual(latest.provider_id, "gemini")
else:
    if not TYPE_CHECKING:
        class RequestHistoryTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
