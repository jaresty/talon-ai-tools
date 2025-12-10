import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.requestHistoryActions import (
        UserActions as HistoryActions,
        history_axes_for,
        history_summary_lines,
    )
    from talon_user.lib.requestLog import append_entry, clear_history, all_entries
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelConfirmationGUI import (
        ConfirmationGUIState,
        UserActions as ConfirmationActions,
    )
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon import actions

    class RequestHistoryActionTests(unittest.TestCase):
        def setUp(self):
            clear_history()
            actions.user.calls.clear()
            actions.user.pasted.clear()
            actions.app.calls.clear()
            GPTState.last_response = ""
            GPTState.last_meta = ""
            GPTState.text_to_confirm = ""

            # Stub canvas open to record invocation.
            def _open_canvas():
                actions.user.calls.append(("model_response_canvas_open", tuple(), {}))

            actions.user.model_response_canvas_open = _open_canvas  # type: ignore[attr-defined]

        def test_show_latest_populates_state_and_opens_canvas(self):
            append_entry("rid-1", "prompt text", "answer text", "meta text")
            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(GPTState.last_response, "answer text")
            self.assertEqual(GPTState.last_meta, "meta text")
            self.assertEqual(GPTState.text_to_confirm, "answer text")
            self.assertIn(
                ("model_response_canvas_open", tuple(), {}),
                actions.user.calls,
            )

        def test_show_previous_uses_offset(self):
            append_entry("rid-1", "p1", "resp1", "meta1")
            append_entry("rid-2", "p2", "resp2", "meta2")

            HistoryActions.gpt_request_history_show_previous(1)
            self.assertEqual(GPTState.last_response, "resp1")
            self.assertEqual(GPTState.last_meta, "meta1")

        def test_empty_history_notifies(self):
            HistoryActions.gpt_request_history_show_latest()
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)

        def test_prev_next_navigation(self):
            append_entry("rid-1", "p1", "resp1", "meta1")
            append_entry("rid-2", "p2", "resp2", "meta2")
            append_entry("rid-3", "p3", "resp3", "meta3")

            HistoryActions.gpt_request_history_show_latest()
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp2")
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp1")
            # Attempting to go past oldest should not change.
            HistoryActions.gpt_request_history_prev()
            self.assertEqual(GPTState.last_response, "resp1")
            # Step forward to newer entries.
            HistoryActions.gpt_request_history_next()
            self.assertEqual(GPTState.last_response, "resp2")
            HistoryActions.gpt_request_history_next()
            self.assertEqual(GPTState.last_response, "resp3")
            # Already at latest.
            HistoryActions.gpt_request_history_next()

        def test_history_list_notifies(self):
            append_entry("rid-1", "prompt one", "resp1", duration_ms=7)
            actions.user.calls.clear()
            actions.app.calls.clear()
            HistoryActions.gpt_request_history_list(2)
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)

        def test_history_list_handles_entries_without_recipe(self):
            # Simulate legacy entries lacking a recipe attribute by monkeypatching all_entries.
            class LegacyEntry:
                def __init__(self, request_id, prompt, response, meta=""):
                    self.request_id = request_id
                    self.prompt = prompt
                    self.response = response
                    self.meta = meta
                    self.duration_ms = None

            saved_all_entries = all_entries
            try:

                def legacy_all_entries():
                    return [
                        LegacyEntry(
                            "rid-legacy", "prompt legacy", "resp legacy", "meta legacy"
                        )
                    ]

                HistoryActions.all_entries = staticmethod(legacy_all_entries)  # type: ignore[attr-defined]
                actions.user.calls.clear()
                actions.app.calls.clear()
                HistoryActions.gpt_request_history_list(1)
                notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
                app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
                self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)
            finally:
                HistoryActions.all_entries = staticmethod(saved_all_entries)  # type: ignore[attr-defined]

        def test_history_open_clears_presentation_and_pastes_entry(self):
            append_entry("rid-1", "prompt one", "history answer", duration_ms=7)
            ConfirmationGUIState.current_presentation = ResponsePresentation(
                display_text="old display",
                paste_text="old paste",
            )
            ConfirmationGUIState.display_thread = True
            ConfirmationGUIState.last_item_text = "thread chunk"

            HistoryActions.gpt_request_history_show_latest()
            ConfirmationActions.confirmation_gui_paste()

            self.assertIsNone(ConfirmationGUIState.current_presentation)
            self.assertFalse(ConfirmationGUIState.display_thread)
            self.assertEqual(actions.user.pasted[-1], "history answer")

        def test_history_open_syncs_axes_from_recipe(self):
            # Seed stale live axes and ensure the history entry recipe replaces them.
            GPTState.last_static_prompt = "todo"
            GPTState.last_completeness = "gist"
            GPTState.last_scope = "actions"
            GPTState.last_method = "steps"
            GPTState.last_style = "checklist"
            GPTState.last_directional = "rog"

            append_entry(
                "rid-1",
                "prompt text",
                "resp",
                "meta",
                recipe="infer · full · rigor · jog",
            )

            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(GPTState.last_static_prompt, "infer")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_method, "rigor")
            self.assertEqual(GPTState.last_directional, "jog")

        def test_history_show_latest_prefers_axes_dict(self):
            # If an entry includes an axes dict, it should win over the legacy recipe string.
            axes = {
                "completeness": ["max"],
                "scope": ["edges", "bound"],
                "method": ["rigor"],
                "style": ["jira"],
            }
            append_entry(
                "rid-axes",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="infer · full · bound · steps · plain",
                axes=axes,
            )

            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(GPTState.last_axes, axes)
            # last_* strings should be derived from the axes tokens (not the legacy recipe).
            self.assertEqual(GPTState.last_completeness, "max")
            self.assertEqual(GPTState.last_scope, "edges bound")
            self.assertEqual(GPTState.last_method, "rigor")
            self.assertEqual(GPTState.last_style, "jira")

        def test_history_show_latest_recap_uses_last_axes_tokens(self):
            axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor", "xp"],
                "style": ["plain"],
            }
            append_entry(
                "rid-axes",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="legacy · should · be · ignored",
                axes=axes,
            )

            HistoryActions.gpt_request_history_show_latest()

            # The recap recipe string is derived from tokens, not the legacy recipe.
            expected_recipe = " · ".join(
                ["", "full", "bound edges", "rigor xp", "plain"]
            ).strip(" ·")
            self.assertEqual(GPTState.last_recipe, expected_recipe)

        def test_history_show_latest_filters_invalid_axis_tokens(self):
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "style": ["plain", "Hydrated style"],
            }
            append_entry(
                "rid-axes",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="legacy · should · be · ignored",
                axes=axes,
            )

            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor"],
                    "style": ["plain"],
                },
            )

        def test_history_axes_for_filters_invalid_tokens(self):
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "style": ["plain", "Hydrated style"],
            }

            filtered = history_axes_for(axes)

            self.assertEqual(
                filtered,
                {
                    "completeness": ["full"],
                    "scope": ["bound"],
                    "method": ["rigor"],
                    "style": ["plain"],
                },
            )

        def test_history_summary_lines_matches_existing_formatting(self):
            append_entry(
                "rid-1",
                "prompt one",
                "resp1",
                "meta1",
                recipe="infer · full · rigor",
                duration_ms=7,
            )

            entries = all_entries()[-1:]
            lines = history_summary_lines(entries)

            self.assertEqual(
                lines, ["0: rid-1 (7ms) | infer · full · rigor · prompt one"]
            )
else:
    if not TYPE_CHECKING:

        class RequestHistoryActionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
