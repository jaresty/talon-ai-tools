import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestHistoryDrawer import (
        HistoryDrawerState,
        UserActions as DrawerActions,
        history_drawer_entries_from,
    )
    import talon_user.lib.requestHistoryDrawer as history_drawer  # type: ignore
    from talon_user.lib.requestLog import (
        append_entry,
        clear_history,
        consume_last_drop_reason_record,
        last_drop_reason_code,
    )
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.personaConfig import persona_intent_maps_reset
    from talon import canvas

    class RequestHistoryDrawerTests(unittest.TestCase):
        def setUp(self):
            clear_history()
            HistoryDrawerState.showing = False
            HistoryDrawerState.entries = []

        def test_open_close_drawer(self):
            DrawerActions.request_history_drawer_open()
            self.assertTrue(HistoryDrawerState.showing)
            DrawerActions.request_history_drawer_close()
            self.assertFalse(HistoryDrawerState.showing)

        def test_drawer_actions_respect_in_flight_guard(self):
            import sys

            module = sys.modules["talon_user.lib.requestHistoryDrawer"]
            with patch.object(
                module, "_reject_if_request_in_flight", return_value=True
            ):
                DrawerActions.request_history_drawer_open()
                DrawerActions.request_history_drawer_toggle()
                DrawerActions.request_history_drawer_close()
                DrawerActions.request_history_drawer_prev_entry()
                DrawerActions.request_history_drawer_next_entry()
                DrawerActions.request_history_drawer_open_selected()
            # Guarded actions should not flip showing state.
            self.assertFalse(HistoryDrawerState.showing)

        def test_open_populates_entries(self):
            append_entry(
                "rid-1",
                "prompt text",
                "resp",
                "meta",
                duration_ms=42,
                axes={"directional": ["fog"]},
            )
            DrawerActions.request_history_drawer_open()
            self.assertGreaterEqual(len(HistoryDrawerState.entries), 1)
            # Ensure duration is included in the label.
            label, _ = HistoryDrawerState.entries[0]
            self.assertIn("42", label)

        def test_selection_navigation(self):
            append_entry("rid-1", "p1", "resp1", "meta1", axes={"directional": ["fog"]})
            append_entry("rid-2", "p2", "resp2", "meta2", axes={"directional": ["fog"]})
            DrawerActions.request_history_drawer_open()
            self.assertEqual(HistoryDrawerState.selected_index, 0)
            DrawerActions.request_history_drawer_next_entry()
            self.assertEqual(HistoryDrawerState.selected_index, 1)
            DrawerActions.request_history_drawer_prev_entry()
            self.assertEqual(HistoryDrawerState.selected_index, 0)

        def test_history_drawer_entries_from_matches_label_and_body(self):
            class DummyEntry:
                def __init__(self):
                    self.request_id = "rid-1"
                    self.prompt = "prompt one\nsecond line"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 42
                    self.recipe = "infer · full · rigor"
                    self.provider_id = "gemini"
                    self.axes = {"directional": ["fog"]}

            rendered = history_drawer_entries_from([DummyEntry()])

            self.assertEqual(len(rendered), 1)
            label, body = rendered[0]
            self.assertEqual(label, "rid-1 (42ms) [gemini]")
            self.assertEqual(body, "infer · fog · prompt one · provider=gemini")

        def test_history_drawer_includes_persona_and_intent_metadata(self):
            persona_intent_maps_reset()
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plan · plain · fog"
            GPTState.last_static_prompt = "describe"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "focus"
            GPTState.last_method = "plan"
            GPTState.last_form = "plain"
            GPTState.last_channel = "slack"
            GPTState.last_directional = "fog"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["plan"],
                "form": ["plain"],
                "channel": ["slack"],
                "directional": ["fog"],
            }
            GPTState.last_suggest_context = {
                "persona_preset_key": "teach_junior_dev",
                "intent_preset_key": "decide",
            }

            append_entry(
                "rid-persona",
                "prompt text",
                "response",
                "meta",
                recipe="describe · full · focus · plan · plain · fog",
                axes={
                    "completeness": ["full"],
                    "scope": ["focus"],
                    "method": ["plan"],
                    "form": ["plain"],
                    "channel": ["slack"],
                    "directional": ["fog"],
                },
            )

            DrawerActions.request_history_drawer_open()
            try:
                self.assertGreaterEqual(len(HistoryDrawerState.entries), 1)
                _, body = HistoryDrawerState.entries[0]
                lower_body = body.lower()
                self.assertIn("persona mentor", lower_body)
                self.assertIn("key=teach_junior_dev", lower_body)
                self.assertIn("say: persona mentor", lower_body)
                self.assertIn("intent for deciding", lower_body)
                self.assertIn("key=decide", lower_body)
                self.assertIn("say: intent for deciding", lower_body)
            finally:
                DrawerActions.request_history_drawer_close()

        def test_history_drawer_alias_only_metadata_normalises_via_catalog(self):
            persona_intent_maps_reset()
            GPTState.reset_all()
            append_entry(
                "rid-alias",
                "prompt text",
                "response",
                "meta",
                axes={"directional": ["fog"]},
                persona={
                    "persona_preset_spoken": "mentor",
                    "intent_display": "For deciding",
                },
            )

            DrawerActions.request_history_drawer_open()
            try:
                self.assertGreaterEqual(len(HistoryDrawerState.entries), 1)
                _, body = HistoryDrawerState.entries[0]
                lower_body = body.lower()
                self.assertIn("persona mentor", lower_body)
                self.assertIn("key=teach_junior_dev", lower_body)
                self.assertIn("intent for deciding", lower_body)
                self.assertIn("key=decide", lower_body)
            finally:
                DrawerActions.request_history_drawer_close()

        def test_drawer_save_latest_source_refreshes_entries(self):
            from talon_user.lib import requestLog as requestlog  # type: ignore
            from talon import actions

            requestlog.clear_history()
            HistoryDrawerState.entries = []
            HistoryDrawerState.showing = False
            with patch.object(
                actions.user, "gpt_request_history_save_latest_source"
            ) as save_mock:

                def _save():
                    append_entry(
                        "rid-new",
                        "prompt",
                        "resp",
                        "meta",
                        axes={"directional": ["fog"]},
                    )
                    return "/tmp/file.md"

                save_mock.side_effect = _save
                DrawerActions.request_history_drawer_save_latest_source()

            save_mock.assert_called()
            self.assertTrue(HistoryDrawerState.showing)
            self.assertGreaterEqual(len(HistoryDrawerState.entries), 1)
            label, _ = HistoryDrawerState.entries[0]
            self.assertIn("rid-new", label)

        def test_drawer_key_s_triggers_save_latest_source(self):
            from talon_user.lib import requestLog as requestlog  # type: ignore
            from talon import actions

            requestlog.clear_history()
            HistoryDrawerState.entries = []
            HistoryDrawerState.showing = False
            with (
                patch.object(
                    actions.user, "request_history_drawer_save_latest_source"
                ) as save_mock,
                patch.object(
                    actions.user, "gpt_request_history_save_latest_source"
                ) as gpt_save,
            ):
                gpt_save.return_value = "/tmp/file.md"
                save_mock.side_effect = (
                    DrawerActions.request_history_drawer_save_latest_source
                )
                DrawerActions.request_history_drawer_open()
                actions.user.request_history_drawer_save_latest_source()
                save_mock.assert_called()
                gpt_save.assert_called()
                self.assertTrue(HistoryDrawerState.showing)

        def test_drawer_save_latest_respects_inflight_guard(self):
            from talon_user.lib import requestLog as requestlog  # type: ignore
            from talon import actions

            requestlog.clear_history()
            HistoryDrawerState.entries = []
            HistoryDrawerState.showing = False
            with (
                patch.object(
                    history_drawer, "_reject_if_request_in_flight", return_value=True
                ),
                patch.object(
                    actions.user, "gpt_request_history_save_latest_source"
                ) as save_mock,
            ):
                result = DrawerActions.request_history_drawer_save_latest_source()
            self.assertIsNone(result)
            save_mock.assert_not_called()
            self.assertFalse(HistoryDrawerState.showing)

        def test_reject_if_request_in_flight_surfaces_drop_reason(self):
            message = (
                "GPT: Cannot save history source; entry is missing a directional lens."
            )
            with (
                patch.object(
                    history_drawer,
                    "try_begin_request",
                    return_value=(False, "history_save_missing_directional"),
                ) as try_begin,
                patch.object(
                    history_drawer, "drop_reason_message", return_value=message
                ),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                result = history_drawer._reject_if_request_in_flight()
            try_begin.assert_called_once_with(source="requestHistoryDrawer")
            set_reason.assert_called_once_with("history_save_missing_directional")
            notify_mock.assert_called_once_with(message)
            self.assertTrue(result)

        def test_history_drawer_open_surfaces_drop_message(self):
            message = (
                "GPT: Cannot save history source; entry is missing a directional lens."
            )
            HistoryDrawerState.showing = False
            HistoryDrawerState.entries = []
            HistoryDrawerState.last_message = ""
            with (
                patch.object(
                    history_drawer,
                    "try_begin_request",
                    return_value=(False, "history_save_missing_directional"),
                ),
                patch.object(
                    history_drawer, "drop_reason_message", return_value=message
                ),
                patch.object(history_drawer, "set_drop_reason") as set_reason,
                patch.object(history_drawer, "notify") as notify_mock,
            ):
                DrawerActions.request_history_drawer_open()
            set_reason.assert_called_once_with("history_save_missing_directional")
            notify_mock.assert_called_once_with(message)
            self.assertFalse(HistoryDrawerState.showing)
            self.assertEqual(HistoryDrawerState.last_message, message)

        def test_history_drawer_guard_records_fallback_message(self):
            HistoryDrawerState.last_message = ""
            with (
                patch.object(
                    history_drawer,
                    "try_begin_request",
                    return_value=(False, "history_save_missing_directional"),
                ),
                patch.object(history_drawer, "drop_reason_message", return_value=""),
                patch.object(history_drawer, "notify"),
            ):
                history_drawer._reject_if_request_in_flight()
            record = consume_last_drop_reason_record()
            self.assertEqual(
                record.message,
                "GPT: Request blocked; reason=history_save_missing_directional.",
            )
            self.assertEqual(record.code, "history_save_missing_directional")

        def test_drawer_refresh_noop_when_hidden(self):
            HistoryDrawerState.showing = False
            with patch.object(history_drawer, "_refresh_entries") as refresh_mock:
                DrawerActions.request_history_drawer_refresh()
            refresh_mock.assert_not_called()

        def test_drawer_refresh_respects_inflight_guard(self):
            HistoryDrawerState.showing = True
            with (
                patch.object(
                    history_drawer, "_reject_if_request_in_flight", return_value=True
                ) as guard_mock,
                patch.object(history_drawer, "_refresh_entries") as refresh_mock,
            ):
                DrawerActions.request_history_drawer_refresh()
            guard_mock.assert_called()
            refresh_mock.assert_not_called()

        def test_drawer_refresh_updates_entries_when_showing(self):
            HistoryDrawerState.showing = True
            HistoryDrawerState.entries = []

            class DummyCanvas:
                def __init__(self):
                    self.shown = False

                def show(self):
                    self.shown = True

            dummy_canvas = DummyCanvas()
            with (
                patch.object(
                    history_drawer, "_ensure_canvas", return_value=dummy_canvas
                ),
                patch.object(history_drawer, "_refresh_entries") as refresh_mock,
            ):

                def _refresh():
                    HistoryDrawerState.entries.append(("rid-new", "body"))

                refresh_mock.side_effect = _refresh
                DrawerActions.request_history_drawer_refresh()

            refresh_mock.assert_called_once()
            self.assertTrue(dummy_canvas.shown)
            self.assertIn(("rid-new", "body"), HistoryDrawerState.entries)

        def test_drawer_reports_drop_reason_when_no_directional_entries(self):
            # Append an entry without directional; guardrail should drop and surface the reason.
            append_entry("rid-nd", "p1", "r1", "m1", axes={"scope": ["focus"]})
            HistoryDrawerState.showing = True
            HistoryDrawerState.entries = []
            with patch.object(history_drawer, "_ensure_canvas") as ensure_canvas:

                class DummyCanvas:
                    def show(self):
                        pass

                ensure_canvas.return_value = DummyCanvas()
                DrawerActions.request_history_drawer_refresh()
            self.assertEqual(HistoryDrawerState.entries, [])
            self.assertIn("directional lens", HistoryDrawerState.last_message)
            # Showing the message should consume the underlying drop reason.
            self.assertEqual(last_drop_reason_code(), "")

        def test_drawer_surfaces_unknown_axis_errors(self):
            HistoryDrawerState.showing = True
            HistoryDrawerState.entries = []
            error_message = (
                "HistoryQuery received unknown axis keys: mystery (entry=rid-old)"
            )
            with (
                patch.object(history_drawer, "_ensure_canvas") as ensure_canvas,
                patch.object(
                    history_drawer,
                    "history_drawer_entries_from",
                    side_effect=ValueError(error_message),
                ),
            ):

                class DummyCanvas:
                    def show(self):
                        pass

                ensure_canvas.return_value = DummyCanvas()
                DrawerActions.request_history_drawer_refresh()

            self.assertEqual(HistoryDrawerState.entries, [])
            message_lines = HistoryDrawerState.last_message.splitlines()
            self.assertGreaterEqual(len(message_lines), 3)
            self.assertIn("unsupported axis keys", HistoryDrawerState.last_message)
            self.assertTrue(any("mystery" in line for line in message_lines))
            self.assertTrue(
                any("history-axis-validate.py" in line for line in message_lines),
                HistoryDrawerState.last_message,
            )
            self.assertEqual(last_drop_reason_code(), "")

        def test_drawer_escape_closes(self):
            from types import SimpleNamespace
            import talon_user.lib.requestHistoryDrawer as history_drawer  # type: ignore

            HistoryDrawerState.showing = False
            DrawerActions.request_history_drawer_open()
            self.assertTrue(HistoryDrawerState.showing)
            key_evt = SimpleNamespace(down=True, key="escape")
            handler = getattr(history_drawer, "_last_key_handler", None)
            if handler:
                handler(key_evt)
            self.assertFalse(HistoryDrawerState.showing)
else:
    if not TYPE_CHECKING:

        class RequestHistoryDrawerTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
