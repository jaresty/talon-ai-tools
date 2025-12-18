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
        last_drop_reason,
        last_drop_reason_code,
        consume_last_drop_reason,
        axis_snapshot_from_axes,
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
                axes={"method": ["steps"], "directional": ["fog"]},
            )
            append_entry(
                "r2",
                "p2",
                "resp2",
                "meta2",
                started_at_ms=3,
                duration_ms=4,
                axes={"directional": ["fog"]},
            )
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
                axes={**axes, "directional": ["fog"]},
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

        def test_stored_axes_match_axis_snapshot_helper(self) -> None:
            axes = {
                "completeness": ["full", "Important: hydrated"],
                "scope": ["focus", "Important: expanded"],
                "method": ["steps", "Important: method"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
                "custom": ["value", ""],
            }

            append_entry(
                "r-snapshot",
                "prompt",
                "resp",
                "meta",
                recipe="recipe-snapshot",
                axes=axes,
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)

            snapshot = axis_snapshot_from_axes(axes)
            self.assertEqual(entry.axes, snapshot.as_dict())

        def test_append_entry_filters_hydrated_axis_values(self):
            axes = {
                "scope": ["focus", "Important: expand scope a lot"],
                "method": ["steps", "Important: do many things"],
                "directional": ["fog"],
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

        def test_append_entry_uses_axis_catalog_tokens(self):
            """Guardrail: requestLog axis filtering honors catalog/list tokens."""

            axes = {
                # directional axis present in axisConfig/Talon lists
                "directional": ["bog", "unknown-direction"],
                # passthrough for unexpected keys should keep trimmed values
                "custom": [" keep_me "],
            }

            append_entry(
                "r5",
                "prompt",
                "resp",
                "meta",
                recipe="recipe5",
                started_at_ms=9,
                duration_ms=10,
                axes=axes,
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.axes.get("directional"), ["bog"])
            self.assertEqual(entry.axes.get("custom"), ["keep_me"])

        def test_append_entry_requires_directional_by_default(self):
            """Guardrail: history entries should be dropped if directional axis is missing."""

            append_entry(
                "r6",
                "prompt",
                "resp",
                "meta",
                recipe="recipe6",
                axes={"scope": ["focus"]},
            )

            self.assertEqual(all_entries(), [])
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            drop_reason = consume_last_drop_reason()
            self.assertIn("directional lens", drop_reason.lower())
            self.assertEqual(last_drop_reason_code(), "")

        def test_append_entry_from_request_requires_request_id(self):
            """Guardrail: append_entry_from_request drops entries when request id is missing."""

            request = {
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": "hi"}]}
                ]
            }
            append_entry_from_request(
                request_id="",
                request=request,
                answer_text="resp",
                meta_text="meta",
                axes={"directional": ["fog"]},
            )

            self.assertEqual(all_entries(), [])
            self.assertEqual(last_drop_reason_code(), "missing_request_id")
            drop_reason = consume_last_drop_reason()
            self.assertIn("missing request id", drop_reason.lower())
            self.assertEqual(last_drop_reason_code(), "")

        def test_consume_last_drop_reason_clears_reason(self):
            append_entry(
                "r10",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            self.assertIn("directional lens", last_drop_reason())
            consumed = consume_last_drop_reason()
            self.assertIn("directional lens", consumed)
            self.assertEqual(last_drop_reason(), "")
            self.assertEqual(last_drop_reason_code(), "")

        def test_last_drop_reason_is_peek_only(self):
            append_entry(
                "r11",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            peek1 = last_drop_reason()
            peek2 = last_drop_reason()
            self.assertIn("directional lens", peek1)
            self.assertIn("directional lens", peek2)
            self.assertEqual(last_drop_reason_code(), "missing_directional")

        def test_successful_append_clears_drop_reason(self):
            append_entry(
                "r12",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            self.assertIn("directional lens", last_drop_reason())
            append_entry(
                "r13",
                "prompt ok",
                "resp ok",
                "meta ok",
                axes={"directional": ["fog"]},
            )
            self.assertEqual(last_drop_reason(), "")
            self.assertEqual(last_drop_reason_code(), "")
            self.assertEqual(consume_last_drop_reason(), "")

        def test_consume_last_drop_reason_is_idempotent(self):
            append_entry(
                "r14",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            first = consume_last_drop_reason()
            self.assertIn("directional lens", first)
            self.assertEqual(last_drop_reason_code(), "")
            second = consume_last_drop_reason()
            self.assertEqual(second, "")
            self.assertEqual(last_drop_reason(), "")


else:
    if not TYPE_CHECKING:

        class RequestLogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
