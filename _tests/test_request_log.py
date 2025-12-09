import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestLog import (
        append_entry,
        latest,
        nth_from_latest,
        all_entries,
        clear_history,
    )

    class RequestLogTests(unittest.TestCase):
        def setUp(self):
            clear_history()

        def test_append_and_retrieve(self):
            append_entry("r1", "p1", "resp1", "meta1", recipe="recipe1", started_at_ms=1, duration_ms=2)
            append_entry("r2", "p2", "resp2", "meta2", started_at_ms=3, duration_ms=4)
            self.assertEqual(latest().request_id, "r2")  # type: ignore[union-attr]
            self.assertEqual(nth_from_latest(1).request_id, "r1")  # type: ignore[union-attr]
            ids = [e.request_id for e in all_entries()]
            self.assertEqual(ids, ["r1", "r2"])
            self.assertEqual(latest().duration_ms, 4)  # type: ignore[union-attr]
            self.assertEqual(nth_from_latest(1).recipe, "recipe1")  # type: ignore[union-attr]
else:
    if not TYPE_CHECKING:
        class RequestLogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
