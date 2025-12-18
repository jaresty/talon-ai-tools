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
        last_drop_reason_code,
    )
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
