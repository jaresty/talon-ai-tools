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
        consume_last_drop_reason,
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
            drop_reason = consume_last_drop_reason()
            self.assertIn("directional lens", drop_reason)

        def test_append_entry_normalises_axis_tokens_case_insensitive(self):
            """Guardrail: axis tokens should be accepted case-insensitively and stored canonicalised."""

            append_entry(
                "r6a",
                "prompt",
                "resp",
                "meta",
                recipe="recipe6a",
                axes={"directional": ["FOG"]},
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.request_id, "r6a")  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("directional"), ["fog"])  # type: ignore[union-attr]
            self.assertEqual(last_drop_reason(), "")

        def test_append_entry_normalises_all_axis_tokens_case_insensitive(self):
            """Guardrail: non-directional axis tokens are matched case-insensitively and canonicalised."""

            append_entry(
                "r6b",
                "prompt",
                "resp",
                "meta",
                recipe="recipe6b",
                axes={
                    "scope": ["FOCUS"],
                    "method": ["STEPS"],
                    "form": ["BULLETS"],
                    "channel": ["SLACK"],
                    "directional": ["FOG"],
                },
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.request_id, "r6b")  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("scope"), ["focus"])  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("method"), ["steps"])  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("form"), ["bullets"])  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("channel"), ["slack"])  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("directional"), ["fog"])  # type: ignore[union-attr]
            self.assertEqual(last_drop_reason(), "")

        def test_append_entry_can_opt_out_directional_requirement(self):
            """Guardrail: callers can explicitly allow missing directional axes when needed."""

            append_entry(
                "r7",
                "prompt",
                "resp",
                "meta",
                recipe="recipe7",
                axes={"scope": ["focus"]},
                require_directional=False,
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.request_id, "r7")  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("scope"), ["focus"])  # type: ignore[union-attr]
            self.assertEqual(last_drop_reason(), "")

        def test_append_entry_from_request_requires_directional(self):
            """Guardrail: append_entry_from_request should drop entries without directional unless opted out."""

            request = {"messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]}
            append_entry_from_request(
                request_id="r8",
                request=request,
                answer_text="resp",
                meta_text="meta",
                axes={"scope": ["focus"]},
            )

            self.assertEqual(all_entries(), [])
            drop_reason = consume_last_drop_reason()
            self.assertIn("directional lens", drop_reason)

        def test_append_entry_from_request_allows_directional_opt_out(self):
            """Guardrail: callers can opt out of directional enforcement in append_entry_from_request."""

            request = {"messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]}
            append_entry_from_request(
                request_id="r9",
                request=request,
                answer_text="resp",
                meta_text="meta",
                axes={"scope": ["focus"]},
                require_directional=False,
            )

            entry = latest()  # type: ignore[assignment]
            self.assertIsNotNone(entry)
            self.assertEqual(entry.request_id, "r9")  # type: ignore[union-attr]
            self.assertEqual(entry.axes.get("scope"), ["focus"])  # type: ignore[union-attr]
            self.assertEqual(last_drop_reason(), "")

        def test_append_entry_requires_request_id(self):
            """Guardrail: history entries must include a request id."""

            append_entry(
                "",
                "prompt",
                "resp",
                "meta",
                recipe="recipe-missing-id",
                axes={"directional": ["fog"]},
            )

            self.assertEqual(all_entries(), [])
            drop_reason = consume_last_drop_reason()
            self.assertIn("missing request id", drop_reason.lower())

        def test_append_entry_from_request_requires_request_id(self):
            """Guardrail: append_entry_from_request drops entries when request id is missing."""

            request = {"messages": [{"role": "user", "content": [{"type": "text", "text": "hi"}]}]}
            append_entry_from_request(
                request_id="",
                request=request,
                answer_text="resp",
                meta_text="meta",
                axes={"directional": ["fog"]},
            )

            self.assertEqual(all_entries(), [])
            drop_reason = consume_last_drop_reason()
            self.assertIn("missing request id", drop_reason.lower())

        def test_consume_last_drop_reason_clears_reason(self):
            append_entry(
                "r10",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertIn("directional lens", last_drop_reason())
            consumed = consume_last_drop_reason()
            self.assertIn("directional lens", consumed)
            self.assertEqual(last_drop_reason(), "")

        def test_last_drop_reason_is_peek_only(self):
            append_entry(
                "r11",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            peek1 = last_drop_reason()
            peek2 = last_drop_reason()
            self.assertIn("directional lens", peek1)
            self.assertIn("directional lens", peek2)

        def test_successful_append_clears_drop_reason(self):
            append_entry(
                "r12",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            self.assertIn("directional lens", last_drop_reason())
            append_entry(
                "r13",
                "prompt ok",
                "resp ok",
                "meta ok",
                axes={"directional": ["fog"]},
            )
            self.assertEqual(last_drop_reason(), "")
            self.assertEqual(consume_last_drop_reason(), "")

        def test_consume_last_drop_reason_is_idempotent(self):
            append_entry(
                "r14",
                "prompt",
                "resp",
                "meta",
                axes={"scope": ["focus"]},
            )
            first = consume_last_drop_reason()
            self.assertIn("directional lens", first)
            second = consume_last_drop_reason()
            self.assertEqual(second, "")
            self.assertEqual(last_drop_reason(), "")


else:
    if not TYPE_CHECKING:

        class RequestLogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
