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
        append_entry_from_request,
        latest,
        nth_from_latest,
        all_entries,
        clear_history,
    )

    class RequestLogTests(unittest.TestCase):
        def setUp(self):
            clear_history()

        def test_append_and_retrieve(self):
            append_entry(
                "r1",
                "p1",
                "resp1",
                "meta1",
                recipe="recipe1",
                started_at_ms=1,
                duration_ms=2,
                axes={"method": ["steps"]},
            )
            append_entry("r2", "p2", "resp2", "meta2", started_at_ms=3, duration_ms=4)
            self.assertEqual(latest().request_id, "r2")  # type: ignore[union-attr]
            self.assertEqual(nth_from_latest(1).request_id, "r1")  # type: ignore[union-attr]
            ids = [e.request_id for e in all_entries()]
            self.assertEqual(ids, ["r1", "r2"])
            self.assertEqual(latest().duration_ms, 4)  # type: ignore[union-attr]
            self.assertEqual(nth_from_latest(1).recipe, "recipe1")  # type: ignore[union-attr]
            self.assertEqual(nth_from_latest(1).axes.get("method"), ["steps"])  # type: ignore[union-attr]

        def test_append_entry_from_request_uses_request_structure(self):
            request = {
                "messages": [
                    {"role": "system", "content": "ignored"},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "line one"},
                            {"type": "text", "text": "line two"},
                        ],
                    },
                ]
            }
            axes = {"method": ["steps"]}
            append_entry_from_request(
                request_id="r3",
                request=request,
                answer_text="resp3",
                meta_text="meta3",
                recipe="recipe3",
                started_at_ms=5,
                duration_ms=6,
                axes=axes,
            )
            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.request_id, "r3")  # type: ignore[union-attr]
            self.assertEqual(entry.prompt, "line one\n\nline two")  # type: ignore[union-attr]
            self.assertEqual(entry.response, "resp3")  # type: ignore[union-attr]
            self.assertEqual(entry.meta, "meta3")  # type: ignore[union-attr]
            self.assertEqual(entry.recipe, "recipe3")  # type: ignore[union-attr]
            self.assertEqual(entry.duration_ms, 6)  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("method"), ["steps"])  # type: ignore[union-attr]
            # Mutating the original axes dict should not affect stored entry.
            axes["method"].append("extra")
            self.assertEqual(entry.axes.get("method"), ["steps"])  # type: ignore[union-attr]

        def test_append_entry_filters_hydrated_axis_values(self):
            axes = {
                "scope": ["focus", "Important: expand scope a lot"],
                "method": ["steps", "Important: do many things"],
            }

            append_entry(
                "r4",
                "prompt",
                "resp",
                "meta",
                recipe="recipe4",
                started_at_ms=7,
                duration_ms=8,
                axes=axes,
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            # Known axis tokens should be preserved.
            self.assertEqual(entry.axes.get("scope"), ["focus"])
            self.assertEqual(entry.axes.get("method"), ["steps"])
            # Hydrated values starting with 'Important:' should be dropped.
            self.assertNotIn(
                "Important: expand scope a lot", entry.axes.get("scope", [])
            )
            self.assertNotIn("Important: do many things", entry.axes.get("method", []))


else:
    if not TYPE_CHECKING:

        class RequestLogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
