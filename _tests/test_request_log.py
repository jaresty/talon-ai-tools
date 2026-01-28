import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING, get_args
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    import talon_user.lib.requestLog as requestlog_module
    import talon_user.lib.dropReasonUtils as drop_reason_module
    from talon_user.lib.requestState import RequestDropReason
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
                axes={"method": ["flow"], "directional": ["fog"]},
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
            self.assertEqual(nth_from_latest(1).axes.get("method"), ["flow"])  # type: ignore[union-attr]

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
            axes = {"method": ["flow"]}
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
            self.assertEqual(entry.axes.get("method"), ["flow"])  # type: ignore[union-attr]
            # Mutating the original axes dict should not affect stored entry.
            axes["method"].append("extra")
            self.assertEqual(entry.axes.get("method"), ["flow"])  # type: ignore[union-attr]

        def test_stored_axes_match_axis_snapshot_helper(self) -> None:
            axes = {
                "completeness": ["full", "Important: hydrated"],
                "scope": ["struct", "Important: expanded"],
                "method": ["flow", "Important: method"],
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
                "scope": ["struct", "Important: expand scope a lot"],
                "method": ["flow", "Important: do many things"],
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
            self.assertEqual(entry.axes.get("scope"), ["struct"])
            self.assertEqual(entry.axes.get("method"), ["flow"])
            # Hydrated values starting with 'Important:' should be dropped.
            self.assertNotIn(
                "Important: expand scope a lot", entry.axes.get("scope", [])
            )
            self.assertNotIn("Important: do many things", entry.axes.get("method", []))

        def test_normalise_persona_snapshot_uses_persona_orchestrator(self) -> None:
            class OrchestratorStub:
                def __init__(self) -> None:
                    self.persona_aliases = {"friendly mentor": "mentor"}
                    self.intent_aliases = {"guide display": "guide"}
                    self.intent_synonyms = {}
                    self.intent_display_map = {"guide": "Guide Display"}
                    self.persona_presets = {
                        "mentor": SimpleNamespace(
                            key="mentor",
                            label="Mentor Label",
                            spoken="Mentor Spoken",
                            voice="mentor-voice",
                            audience="teams",
                            tone="supportive",
                        )
                    }
                    self.intent_presets = {
                        "guide": SimpleNamespace(
                            key="guide",
                            label="Guide Label",
                            intent="Guide Purpose",
                        )
                    }
                    self.axis_tokens = {}
                    self.axis_alias_map = {}

                def canonical_persona_key(self, alias: str | None) -> str:
                    alias_norm = (alias or "").strip().lower()
                    return self.persona_aliases.get(alias_norm, "")

                def canonical_intent_key(self, alias: str | None) -> str:
                    alias_norm = (alias or "").strip().lower()
                    return self.intent_aliases.get(
                        alias_norm
                    ) or self.intent_synonyms.get(
                        alias_norm,
                        "",
                    )

                def canonical_axis_token(self, axis: str, alias: str | None) -> str:
                    return ""

            orchestrator = OrchestratorStub()
            persona_snapshot = {
                "persona_preset_spoken": "Friendly Mentor",
                "intent_display": "Guide Display",
            }
            empty_maps = SimpleNamespace(
                persona_preset_aliases={},
                persona_presets={},
                intent_preset_aliases={},
                intent_synonyms={},
                intent_presets={},
                intent_display_map={},
            )

            with (
                patch.object(
                    requestlog_module,
                    "persona_intent_maps",
                    return_value=empty_maps,
                ),
                patch(
                    "talon_user.lib.personaOrchestrator.get_persona_intent_orchestrator",
                    return_value=orchestrator,
                ),
                patch.object(
                    requestlog_module,
                    "get_persona_intent_orchestrator",
                    return_value=orchestrator,
                    create=True,
                ),
                patch.object(
                    requestlog_module,
                    "canonical_persona_token",
                    side_effect=lambda domain, token: token,
                ),
            ):
                result = requestlog_module._normalise_persona_snapshot(persona_snapshot)

            self.assertEqual(result["persona_preset_key"], "mentor")
            self.assertEqual(result["persona_preset_label"], "Mentor Label")
            self.assertEqual(result["persona_preset_spoken"], "Mentor Spoken")
            self.assertEqual(result["persona_voice"], "mentor-voice")
            self.assertEqual(result["persona_audience"], "teams")
            self.assertEqual(result["persona_tone"], "supportive")
            self.assertEqual(result["intent_preset_key"], "guide")
            self.assertEqual(result["intent_display"], "Guide Display")
            self.assertEqual(result["intent_purpose"], "Guide Purpose")
            self.assertEqual(result["intent_preset_label"], "Guide Label")

        def test_append_entry_preserves_pending_drop_reason(self) -> None:
            axes = {"directional": ["fog"]}

            with (
                patch.object(
                    requestlog_module, "last_drop_reason", return_value="pending"
                ),
                patch.object(requestlog_module, "set_drop_reason") as set_reason,
            ):
                append_entry(
                    "r_pending",
                    "prompt",
                    "resp",
                    "meta",
                    axes=axes,
                )
            set_reason.assert_not_called()

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
            self.assertIsNone(entry.axes.get("custom"))

        def test_append_entry_requires_directional_by_default(self):
            """Guardrail: history entries should be dropped if directional axis is missing."""

            append_entry(
                "r6",
                "prompt",
                "resp",
                "meta",
                recipe="recipe6",
                axes={"scope": ["struct"]},
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
                axes={"scope": ["struct"]},
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
                axes={"scope": ["struct"]},
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
                axes={"scope": ["struct"]},
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
                axes={"scope": ["struct"]},
            )
            self.assertEqual(last_drop_reason_code(), "missing_directional")
            first = consume_last_drop_reason()
            self.assertIn("directional lens", first)
            self.assertEqual(last_drop_reason_code(), "")
            second = consume_last_drop_reason()
            self.assertEqual(second, "")
            self.assertEqual(last_drop_reason(), "")

        def test_drop_reason_message_covers_known_reasons(self) -> None:
            reasons = [reason for reason in get_args(RequestDropReason) if reason]
            missing: list[str] = []
            for reason in reasons:
                message = requestlog_module.drop_reason_message(reason)
                self.assertIsInstance(message, str)
                if not message.strip():
                    missing.append(reason)
            self.assertFalse(
                missing,
                f"Missing drop reason messages for: {', '.join(missing)}",
            )

        def test_render_drop_reason_uses_helper_and_fallback(self) -> None:
            reasons = [reason for reason in get_args(RequestDropReason) if reason]
            for reason in reasons:
                with patch.object(
                    drop_reason_module,
                    "drop_reason_message",
                    return_value="Rendered message",
                ) as drop_patch:
                    self.assertEqual(
                        drop_reason_module.render_drop_reason(reason),
                        "Rendered message",
                    )
                drop_patch.assert_called_once_with(reason)

            with patch.object(
                drop_reason_module,
                "drop_reason_message",
                side_effect=lambda _: "",
            ):
                self.assertEqual(
                    drop_reason_module.render_drop_reason("streaming_disabled"),
                    "GPT: Request blocked; reason=streaming_disabled.",
                )


else:
    if not TYPE_CHECKING:

        class RequestLogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
