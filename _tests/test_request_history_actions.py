import os
import tempfile
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
    from talon import actions, app
    from talon_user.lib.requestHistoryActions import (
        UserActions as HistoryActions,
        history_axes_for,
        history_summary_lines,
    )
    import talon_user.lib.requestHistoryActions as history_actions
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
            append_entry(
                "rid-1",
                "prompt text",
                "answer text",
                "meta text",
                recipe="describe · gist · focus · steps · plain · slack · fog",
                axes={
                    "completeness": ["gist"],
                    "scope": ["focus"],
                    "method": ["steps"],
                    "form": ["plain"],
                    "channel": ["slack"],
                    "directional": ["fog"],
                },
            )
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

        def test_history_actions_respect_in_flight_guard(self):
            append_entry("rid-1", "prompt text", "answer text", "meta text")
            import sys

            module = sys.modules[HistoryActions.__module__]
            with (
                patch.object(module, "_reject_if_request_in_flight", return_value=True),
                patch.object(module, "_show_entry") as show_entry,
            ):
                HistoryActions.gpt_request_history_show_latest()
                HistoryActions.gpt_request_history_show_previous(1)
                HistoryActions.gpt_request_history_prev()
                HistoryActions.gpt_request_history_next()
            show_entry.assert_not_called()

        def test_history_list_and_save_respect_in_flight_guard(self):
            append_entry("rid-1", "prompt text", "answer text", "meta text")
            import sys

            module = sys.modules[HistoryActions.__module__]
            with patch.object(module, "_reject_if_request_in_flight", return_value=True):
                HistoryActions.gpt_request_history_list(1)
                HistoryActions.gpt_request_history_save_latest_source()
            # No notify calls should have been made when guarded.
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertEqual(len(notify_calls) + len(app_notify_calls), 0)

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
                "form": ["bullets"],
                "channel": ["jira"],
                "directional": ["fog"],
            }
            expected_axes = history_axes_for(axes)
            append_entry(
                "rid-axes",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="infer · full · bound · steps · plain",
                axes=axes,
            )

            HistoryActions.gpt_request_history_show_latest()

            self.assertEqual(GPTState.last_axes, expected_axes)
            # last_* strings should be derived from the axes tokens (not the legacy recipe).
            self.assertEqual(GPTState.last_completeness, "max")
            self.assertEqual(
                GPTState.last_scope, " ".join(expected_axes.get("scope", []))
            )
            self.assertEqual(GPTState.last_method, "rigor")
            self.assertEqual(GPTState.last_form, "bullets")
            self.assertEqual(GPTState.last_channel, "jira")
            self.assertEqual(GPTState.last_directional, "fog")
            self.assertIn("fog", GPTState.last_recipe)

        def test_history_show_latest_recap_uses_last_axes_tokens(self):
            axes = {
                "completeness": ["full"],
                "scope": ["bound", "edges"],
                "method": ["rigor", "xp"],
                "form": ["plain"],
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

        def test_history_show_latest_warns_on_style_axis(self):
            axes = {
                "style": ["plain"],
                "form": ["table"],
                "channel": ["slack"],
                "directional": ["rog"],
            }
            append_entry(
                "rid-style",
                "prompt text",
                "resp axes",
                "meta axes",
                recipe="legacy · plain",
                axes=axes,
            )
            actions.user.calls.clear()

            HistoryActions.gpt_request_history_show_latest()

            notifications = [c for c in actions.user.calls if c[0] == "notify"]
            self.assertTrue(
                any("style axis is removed" in str(args[0]).lower() for _, args, _ in notifications)
            )
            # Style is ignored; form/channel/directional still hydrate.
            self.assertEqual(GPTState.last_form, "table")
            self.assertEqual(GPTState.last_channel, "slack")
            self.assertEqual(GPTState.last_directional, "rog")

        def test_history_show_latest_filters_invalid_axis_tokens(self):
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["plain", "Hydrated style"],
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

            self.assertEqual(GPTState.last_axes.get("completeness"), ["full"])
            self.assertEqual(GPTState.last_axes.get("scope"), ["bound"])
            self.assertEqual(GPTState.last_axes.get("method"), ["rigor"])
            self.assertEqual(GPTState.last_axes.get("form"), ["plain"])
            # Directional was absent; ensure no unknowns leaked through.
            self.assertFalse(GPTState.last_axes.get("directional"))

        def test_history_axes_for_filters_invalid_tokens(self):
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["plain", "Hydrated style"],
            }

            filtered = history_axes_for(axes)

            self.assertEqual(filtered.get("completeness"), ["full"])
            self.assertEqual(filtered.get("scope"), ["bound"])
            self.assertEqual(filtered.get("method"), ["rigor"])
            self.assertEqual(filtered.get("form"), ["plain"])
            self.assertFalse(filtered.get("directional"))

        def test_history_axes_for_applies_axis_caps(self):
            axes = {
                "scope": ["bound", "edges", "focus"],
                "method": ["rigor", "xp", "steps", "plan"],
                "form": ["code", "table"],
                "channel": ["slack", "jira"],
                "directional": ["fog"],
            }

            filtered = history_axes_for(axes)

            self.assertEqual(filtered.get("scope"), ["edges", "focus"])
            self.assertEqual(filtered.get("method"), ["plan", "steps", "xp"])
            # Form/channel are singletons post-split; caps enforce last-wins.
            self.assertEqual(filtered.get("form"), ["table"])
            self.assertEqual(filtered.get("channel"), ["jira"])
            self.assertEqual(filtered.get("directional"), ["fog"])

        def test_history_entry_without_directional_notifies_and_returns(self):
            # History entries lacking directional should not open the canvas or update last state.
            append_entry(
                "rid-no-dir",
                "prompt",
                "response",
                meta="",
                recipe="describe · gist · focus · flow",
                axes={
                    "completeness": ["gist"],
                    "scope": ["focus"],
                    "method": ["flow"],
                    "form": ["plain"],
                    "channel": ["slack"],
                    "directional": [],
                },
            )
            GPTState.last_directional = ""
            with patch.object(app, "notify") as notify_mock, patch.object(
                actions.user, "model_response_canvas_open"
            ) as canvas_mock, patch.object(history_actions, "notify") as notify_fn:
                HistoryActions.gpt_request_history_show_latest()

            notify_fn.assert_called()
            canvas_mock.assert_not_called()
            self.assertEqual(GPTState.last_directional, "")

        def test_history_summary_lines_matches_existing_formatting(self):
            append_entry(
                "rid-1",
                "prompt one",
                "resp1",
                "meta1",
                recipe="infer · full · rigor",
                duration_ms=7,
                axes={"directional": ["fog"]},
            )

            entries = all_entries()[-1:]
            lines = history_summary_lines(entries)

            self.assertEqual(
                lines, ["0: rid-1 (7ms) | infer · full · rigor · fog · prompt one"]
            )

        def test_history_summary_lines_prefers_axes_tokens(self):
            append_entry(
                "rid-axes",
                "prompt one",
                "resp1",
                "meta1",
                recipe="infer · legacy-style",
                axes={
                    "completeness": ["full"],
                    "scope": ["actions"],
                    "method": ["rigor"],
                    "form": ["adr"],
                    "channel": ["slack"],
                    "directional": ["fog"],
                },
            )

            lines = history_summary_lines(all_entries()[-1:])

            self.assertTrue(any("adr" in line and "slack" in line for line in lines))
            self.assertFalse(any("legacy-style" in line for line in lines))

        def test_history_summary_lines_include_provider(self):
            append_entry(
                "rid-2",
                "prompt provider",
                "resp2",
                "meta2",
                recipe="infer · full · rog",
                axes={"directional": ["rog"]},
                provider_id="gemini",
            )
            lines = history_summary_lines(all_entries())
            self.assertTrue(any("provider=gemini" in line for line in lines))

        def test_history_summary_lines_skips_entries_without_directional(self):
            append_entry(
                "rid-no-dir",
                "prompt",
                "resp",
                "meta",
                recipe="infer · gist · focus",
                axes={"completeness": ["gist"], "directional": []},
            )
            append_entry(
                "rid-with-dir",
                "prompt",
                "resp",
                "meta",
                recipe="infer · gist · focus · rog",
                axes={"completeness": ["gist"], "directional": ["rog"]},
            )

            lines = history_summary_lines(all_entries())

            self.assertEqual(len(lines), 1)
            self.assertIn("rid-with-dir", lines[0])

        def test_show_entry_sets_provider(self):
            append_entry(
                "rid-3",
                "prompt",
                "resp3",
                "meta3",
                recipe="infer · full",
                provider_id="gemini",
            )
            HistoryActions.gpt_request_history_show_latest()
            self.assertEqual(getattr(GPTState, "current_provider_id", ""), "gemini")

        def test_history_save_latest_source_writes_markdown_with_prompt(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)

            append_entry(
                "rid-1",
                "prompt one",
                "resp1",
                "meta1",
                recipe="infer · full · rigor",
                duration_ms=7,
            )

            actions.user.calls.clear()
            before = set(os.listdir(tmpdir))

            HistoryActions.gpt_request_history_save_latest_source()

            after = set(os.listdir(tmpdir))
            new_files = list(after - before)
            self.assertEqual(len(new_files), 1, new_files)
            path = os.path.join(tmpdir, new_files[0])
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("# Source", content)
            self.assertIn("prompt one", content)

            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(
                len(notify_calls) + len(app_notify_calls),
                1,
                "Expected at least one notification about saving history source",
            )

else:
    if not TYPE_CHECKING:

        class RequestHistoryActionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
