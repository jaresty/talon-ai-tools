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
    from talon_user.lib.requestLog import append_entry, clear_history
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
            with patch.object(module, "_reject_if_request_in_flight", return_value=True):
                DrawerActions.request_history_drawer_open()
                DrawerActions.request_history_drawer_toggle()
                DrawerActions.request_history_drawer_close()
                DrawerActions.request_history_drawer_prev_entry()
                DrawerActions.request_history_drawer_next_entry()
                DrawerActions.request_history_drawer_open_selected()
            # Guarded actions should not flip showing state.
            self.assertFalse(HistoryDrawerState.showing)

        def test_open_populates_entries(self):
            append_entry("rid-1", "prompt text", "resp", "meta", duration_ms=42)
            DrawerActions.request_history_drawer_open()
            self.assertGreaterEqual(len(HistoryDrawerState.entries), 1)
            # Ensure duration is included in the label.
            label, _ = HistoryDrawerState.entries[0]
            self.assertIn("42", label)

        def test_selection_navigation(self):
            append_entry("rid-1", "p1", "resp1", "meta1")
            append_entry("rid-2", "p2", "resp2", "meta2")
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

            rendered = history_drawer_entries_from([DummyEntry()])

            self.assertEqual(len(rendered), 1)
            label, body = rendered[0]
            self.assertEqual(label, "rid-1 (42ms) [gemini]")
            self.assertEqual(body, "infer · full · rigor · prompt one · provider=gemini")
else:
    if not TYPE_CHECKING:

        class RequestHistoryDrawerTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
