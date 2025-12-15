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
    from talon import actions, app, settings
    from talon_user.lib.requestHistoryActions import (
        UserActions as HistoryActions,
        history_axes_for,
        history_summary_lines,
        _request_is_in_flight,
        _reject_if_request_in_flight,
        _model_source_save_dir,
    )
    import talon_user.lib.requestHistoryActions as history_actions
    from talon_user.lib.requestLog import append_entry, clear_history, all_entries
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelConfirmationGUI import (
        ConfirmationGUIState,
        UserActions as ConfirmationActions,
    )
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon_user.lib.requestState import RequestPhase
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
            # Allow tests to write entries without enforcing directional guardrails.
            import talon_user.lib.requestLog as requestlog  # type: ignore
            self._orig_append_entry = requestlog.append_entry
            def _append_entry_no_directional(*args, **kwargs):
                kwargs.setdefault("require_directional", False)
                return self._orig_append_entry(*args, **kwargs)
            requestlog.append_entry = _append_entry_no_directional  # type: ignore[attr-defined]
            globals()["append_entry"] = _append_entry_no_directional
            self.addCleanup(lambda: setattr(requestlog, "append_entry", self._orig_append_entry))
            self.addCleanup(lambda: globals().__setitem__("append_entry", self._orig_append_entry))

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
                recipe="describe · gist · focus · steps · bullets · slack · fog",
                axes={
                    "completeness": ["gist"],
                    "scope": ["focus"],
                    "method": ["steps"],
                    "form": ["bullets"],
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
            append_entry("rid-1", "p1", "resp1", "meta1", axes={"directional": ["fog"]})
            append_entry("rid-2", "p2", "resp2", "meta2", axes={"directional": ["fog"]})

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

        def test_history_show_latest_uses_drop_reason_when_no_directional(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )

            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_show_latest()

            notify_mock.assert_called()
            self.assertIn("directional lens", str(notify_mock.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

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

        def test_request_is_in_flight_handles_request_phases(self):
            class State:
                def __init__(self, phase):
                    self.phase = phase

            with patch.object(
                history_actions, "current_state", return_value=State(RequestPhase.STREAMING)
            ):
                self.assertTrue(_request_is_in_flight())

            for terminal in (
                RequestPhase.IDLE,
                RequestPhase.DONE,
                RequestPhase.ERROR,
                RequestPhase.CANCELLED,
            ):
                with patch.object(history_actions, "current_state", return_value=State(terminal)):
                    self.assertFalse(_request_is_in_flight())

        def test_reject_if_request_in_flight_notifies_and_blocks(self):
            with (
                patch.object(history_actions, "_request_is_in_flight", return_value=True),
                patch.object(history_actions, "notify") as notify_mock,
            ):
                self.assertTrue(_reject_if_request_in_flight())
                notify_mock.assert_called_once()

        def test_model_source_save_dir_prefers_setting_and_expands_user(self):
            with patch.object(settings, "get", return_value="~/example-dir"):
                path = _model_source_save_dir()
            self.assertTrue(path.endswith("example-dir"))
            self.assertFalse(path.startswith("~"), path)

        def test_model_source_save_dir_falls_back_to_repo_talon_root(self):
            with patch.object(settings, "get", return_value=""):
                path = _model_source_save_dir()
            self.assertTrue(path.endswith("talon-ai-model-sources"))

        def test_history_save_handles_directory_creation_failure(self):
            append_entry(
                "rid-err",
                "prompt",
                "resp",
                "meta",
                recipe="infer · full · rigor",
            )
            with (
                patch.object(history_actions, "notify") as notify_mock,
                patch("os.makedirs", side_effect=OSError("boom")),
                patch("builtins.open") as open_mock,
            ):
                HistoryActions.gpt_request_history_save_latest_source()
            notify_mock.assert_called()
            open_mock.assert_not_called()

        def test_prev_next_navigation(self):
            append_entry("rid-1", "p1", "resp1", "meta1", axes={"directional": ["fog"]})
            append_entry("rid-2", "p2", "resp2", "meta2", axes={"directional": ["fog"]})
            append_entry("rid-3", "p3", "resp3", "meta3", axes={"directional": ["fog"]})

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
            append_entry(
                "rid-1",
                "prompt one",
                "resp1",
                duration_ms=7,
                axes={"directional": ["fog"]},
            )
            actions.user.calls.clear()
            actions.app.calls.clear()
            HistoryActions.gpt_request_history_list(2)
            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(len(notify_calls) + len(app_notify_calls), 1)

        def test_history_list_filters_and_orders_directional_entries(self):
            append_entry(
                "rid-old",
                "old prompt",
                "old resp",
                axes={"scope": ["focus"]},
                require_directional=False,
            )
            append_entry(
                "rid-mid",
                "mid prompt",
                "mid resp",
                axes={"directional": ["jog"]},
            )
            # Recipe-only directional
            append_entry(
                "rid-new",
                "new prompt",
                "new resp",
                recipe="infer · gist · focus · fog",
                axes={},
            )

            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_list(3)

            notify_mock.assert_called_once()
            message = str(notify_mock.call_args[0][0])
            self.assertIn("rid-new", message)
            self.assertIn("rid-mid", message)
            self.assertNotIn("rid-old", message)
            new_idx = message.find("rid-new")
            mid_idx = message.find("rid-mid")
            self.assertLess(new_idx, mid_idx)

        def test_history_list_handles_entries_without_recipe(self):
            # Simulate legacy entries lacking a recipe attribute by monkeypatching all_entries.
            class LegacyEntry:
                def __init__(self, request_id, prompt, response, meta=""):
                    self.request_id = request_id
                    self.prompt = prompt
                    self.response = response
                    self.meta = meta
                    self.duration_ms = None
                    self.recipe = "infer · gist · focus · fog"
                    self.axes = {}

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
            append_entry(
                "rid-1",
                "prompt one",
                "history answer",
                duration_ms=7,
                axes={"directional": ["fog"]},
            )
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
                axes={},  # rely on recipe directional token
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
                recipe="infer · full · bound · steps · bullets",
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
                "form": ["bullets"],
                "directional": ["fog"],
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
                ["", "full", "bound edges", "rigor xp", "bullets", "fog"]
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
                "form": ["bullets", "Hydrated style"],
                "directional": ["fog"],
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
            self.assertEqual(GPTState.last_axes.get("form"), ["bullets"])
            self.assertEqual(GPTState.last_axes.get("directional"), ["fog"])

        def test_history_axes_for_filters_invalid_tokens(self):
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["bullets", "Hydrated style"],
            }

            filtered = history_axes_for(axes)

            self.assertEqual(filtered.get("completeness"), ["full"])
            self.assertEqual(filtered.get("scope"), ["bound"])
            self.assertEqual(filtered.get("method"), ["rigor"])
            self.assertEqual(filtered.get("form"), ["bullets"])
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
                    "form": ["bullets"],
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

        def test_history_entry_without_directional_hydrates_state_but_no_canvas(self):
            GPTState.last_directional = "fog"
            GPTState.last_response = "prev-response"
            setattr(GPTState, "current_provider_id", "prev-provider")
            append_entry(
                "rid-no-dir-2",
                "prompt",
                "response",
                meta="",
                recipe="describe · gist · focus",
                axes={
                    "completeness": ["gist"],
                    "scope": ["focus"],
                    "method": ["flow"],
                    "form": ["bullets"],
                    "channel": ["slack"],
                    "directional": [],
                },
            )
            with patch.object(app, "notify"), patch.object(
                actions.user, "model_response_canvas_open"
            ) as canvas_mock, patch.object(history_actions, "notify") as notify_fn:
                HistoryActions.gpt_request_history_show_latest()

            notify_fn.assert_called()
            canvas_mock.assert_not_called()
            # State should remain unchanged when directional is missing.
            self.assertEqual(GPTState.last_directional, "fog")
            self.assertEqual(GPTState.last_response, "prev-response")
            self.assertEqual(getattr(GPTState, "current_provider_id", ""), "prev-provider")

        def test_prev_keeps_navigation_when_directional_missing(self):
            append_entry(
                "rid-no-dir",
                "prompt",
                "resp missing dir",
                "meta",
                axes={"directional": []},
                require_directional=False,
            )
            append_entry(
                "rid-ok",
                "prompt ok",
                "resp ok",
                "meta",
                axes={"directional": ["fog"]},
            )
            HistoryActions.gpt_request_history_show_latest()
            self.assertEqual(GPTState.last_response, "resp ok")
            # cursor at 0; prev should skip missing-directional entry, notify, and keep cursor at latest
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_prev()
            self.assertGreaterEqual(len(notify_mock.call_args_list), 1)
            self.assertEqual(getattr(history_actions, "_cursor_offset"), 0)
            self.assertEqual(GPTState.last_response, "resp ok")

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

        def test_history_summary_lines_skips_entries_without_axes(self):
            append_entry(
                "rid-no-axes",
                "prompt",
                "resp",
                "meta",
            )

            lines = history_summary_lines(all_entries())

            self.assertEqual(len(lines), 0)

        def test_history_list_notifies_when_no_directional_entries(self):
            append_entry(
                "rid-no-dir",
                "prompt",
                "resp",
                "meta",
                recipe="infer · gist · focus",
                axes={"completeness": ["gist"], "directional": []},
            )

            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_list()

            notify_mock.assert_called()
            self.assertIn("No request history available", str(notify_mock.call_args[0][0]))

        def test_request_log_drops_missing_directional_and_notifies(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify") as notify_mock:
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )

            notify_mock.assert_called()
            self.assertIn("directional lens", str(notify_mock.call_args[0][0]))
            self.assertEqual(len(all_entries()), 0)
            self.assertTrue(requestlog.last_drop_reason())
            with patch.object(history_actions, "notify") as list_notify:
                HistoryActions.gpt_request_history_list()
            list_notify.assert_called()
            self.assertIn("directional lens", str(list_notify.call_args[0][0]))

        def test_drop_reason_consumed_after_history_list(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            with patch.object(history_actions, "notify") as list_notify:
                HistoryActions.gpt_request_history_list()
            self.assertIn("directional lens", str(list_notify.call_args[0][0]))
            # Reason should remain available (peeked, not consumed).
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_drop_reason_not_consumed_when_drawer_peeks(self):
            import talon_user.lib.requestHistoryDrawer as drawer  # type: ignore
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            # Drawer refresh should peek at last_drop_reason without consuming it.
            drawer.HistoryDrawerState.showing = True
            drawer.HistoryDrawerState.entries = []
            with patch.object(drawer, "_ensure_canvas"):
                drawer.UserActions.request_history_drawer_refresh()
            self.assertIn("directional lens", drawer.HistoryDrawerState.last_message)
            # History list should still see the same drop reason afterwards.
            with patch.object(history_actions, "notify") as list_notify:
                HistoryActions.gpt_request_history_list()
            self.assertIn("directional lens", str(list_notify.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_drop_reason_survives_history_list_for_drawer_refresh(self):
            import talon_user.lib.requestHistoryDrawer as drawer  # type: ignore
            import talon_user.lib.requestLog as requestlog  # type: ignore

            # Seed a drop reason with a non-directional entry.
            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            # History list should notify and leave the reason available.
            with patch.object(history_actions, "notify") as list_notify:
                HistoryActions.gpt_request_history_list()
            self.assertIn("directional lens", str(list_notify.call_args[0][0]))
            # Drawer refresh should still surface the same drop reason after list ran.
            drawer.HistoryDrawerState.showing = True
            drawer.HistoryDrawerState.entries = []
            with patch.object(drawer, "_ensure_canvas"):
                drawer.UserActions.request_history_drawer_refresh()
            self.assertIn("directional lens", drawer.HistoryDrawerState.last_message)

        def test_drop_reason_shared_between_latest_and_list(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            # show_latest should surface the reason without consuming it.
            messages: list[str] = []

            def _capture(msg):
                messages.append(msg)

            with patch.object(history_actions, "notify") as notify:
                notify.side_effect = _capture
                HistoryActions.gpt_request_history_show_latest()
            self.assertTrue(messages)
            self.assertIn("directional lens", messages[0])
            # history list should still see the same reason afterward.
            messages = []
            with patch.object(history_actions, "notify") as notify:
                notify.side_effect = _capture
                HistoryActions.gpt_request_history_list()
            self.assertTrue(messages)
            self.assertIn("directional lens", messages[0])

        def test_drop_reason_persists_when_entries_filtered(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            # Seed a drop reason and a non-directional entry that will be filtered.
            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            with patch.object(history_actions, "notify") as list_notify:
                HistoryActions.gpt_request_history_list()
            self.assertIn("directional lens", str(list_notify.call_args[0][0]))
            # Second call should still surface the drop reason (peeked, not consumed).
            with patch.object(history_actions, "notify") as list_notify2:
                HistoryActions.gpt_request_history_list()
            self.assertIn("directional lens", str(list_notify2.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_drop_reason_cleared_after_successful_append(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            # seed a drop to set the reason
            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            self.assertTrue(requestlog.last_drop_reason())
            # successful append clears the reason
            append_entry(
                "rid-ok",
                "prompt ok",
                "resp ok",
                axes={"directional": ["fog"]},
            )
            self.assertEqual(requestlog.last_drop_reason(), "")
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_show_latest()
            notify_mock.assert_not_called()

        def test_show_latest_does_not_read_drop_reason_when_history_exists(self):
            # Seed a directional entry so history is available.
            append_entry(
                "rid-ok",
                "prompt ok",
                "resp ok",
                axes={"directional": ["fog"]},
            )
            with patch.object(history_actions, "last_drop_reason") as drop_mock, patch.object(
                history_actions, "notify"
            ) as notify_mock:
                drop_mock.return_value = "stale reason"
                HistoryActions.gpt_request_history_show_latest()
            drop_mock.assert_not_called()
            notify_mock.assert_not_called()

        def test_drop_reason_cleared_by_clear_history(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            # Clear history should also clear the drop reason.
            requestlog.clear_history()
            messages: list[str] = []

            def _capture(msg):
                messages.append(msg)

            with patch.object(history_actions, "notify") as notify_mock:
                notify_mock.side_effect = _capture
                HistoryActions.gpt_request_history_list()
            self.assertTrue(messages)
            self.assertIn("No request history available", messages[0])
            self.assertEqual(requestlog.last_drop_reason(), "")

        def test_history_list_does_not_read_drop_reason_when_entries_exist(self):
            # Seed a directional entry so list has content.
            append_entry(
                "rid-ok",
                "prompt ok",
                "resp ok",
                axes={"directional": ["fog"]},
            )
            with patch.object(history_actions, "last_drop_reason") as drop_mock, patch.object(
                history_actions, "notify"
            ) as notify_mock:
                drop_mock.side_effect = AssertionError("should not read drop reason")
                HistoryActions.gpt_request_history_list()
            drop_mock.assert_not_called()
            notify_mock.assert_called()
            self.assertNotIn("directional lens", str(notify_mock.call_args[0][0]))

        def test_prev_skips_non_directional_entry_and_keeps_cursor(self):
            import talon_user.lib.requestHistoryActions as actions_mod  # type: ignore
            import talon_user.lib.requestLog as requestlog  # type: ignore

            # Latest entry has directional; previous entry lacks directional but is stored (opt-out).
            append_entry(
                "rid-older",
                "old prompt",
                "old resp",
                axes={"scope": ["focus"]},
                require_directional=False,
            )
            append_entry(
                "rid-latest",
                "new prompt",
                "new resp",
                axes={"directional": ["fog"]},
            )
            actions_mod._cursor_offset = 0  # reset navigation cursor
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_prev()
            notify_mock.assert_called()
            self.assertIn("No older history entry", str(notify_mock.call_args[0][0]))
            self.assertEqual(actions_mod._cursor_offset, 0)
            # Drop reason should not leak when directional history exists.
            self.assertEqual(requestlog.last_drop_reason(), "")

        def test_prev_reports_drop_reason_when_no_directional_history(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore
            import talon_user.lib.requestHistoryActions as actions_mod  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            actions_mod._cursor_offset = 0
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_prev()
            notify_mock.assert_called()
            self.assertIn("directional lens", str(notify_mock.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_next_reports_drop_reason_when_no_directional_history(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore
            import talon_user.lib.requestHistoryActions as actions_mod  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            actions_mod._cursor_offset = 0
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_next()
            notify_mock.assert_called()
            self.assertIn("directional lens", str(notify_mock.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_next_generic_when_directional_history_exists(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore
            import talon_user.lib.requestHistoryActions as actions_mod  # type: ignore

            append_entry(
                "rid-1",
                "prompt1",
                "resp1",
                axes={"directional": ["fog"]},
            )
            actions_mod._cursor_offset = 0
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_next()
            notify_mock.assert_called()
            self.assertIn("Already at latest history entry", str(notify_mock.call_args[0][0]))
            self.assertEqual(requestlog.last_drop_reason(), "")

        def test_show_previous_reports_drop_reason_when_no_directional_history(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            with patch.object(requestlog, "notify"):
                self._orig_append_entry(
                    "rid-no-dir",
                    "prompt",
                    "resp",
                    axes={"scope": ["focus"]},
                )
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_show_previous(1)
            notify_mock.assert_called()
            self.assertIn("directional lens", str(notify_mock.call_args[0][0]))
            self.assertIn("directional lens", requestlog.last_drop_reason())

        def test_show_previous_generic_when_directional_history_exists(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore

            append_entry(
                "rid-1",
                "prompt1",
                "resp1",
                axes={"directional": ["fog"]},
            )
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_show_previous(5)
            notify_mock.assert_called()
            self.assertIn("No older history entry", str(notify_mock.call_args[0][0]))
            self.assertEqual(requestlog.last_drop_reason(), "")

        def test_prev_generic_when_directional_history_exists(self):
            import talon_user.lib.requestLog as requestlog  # type: ignore
            import talon_user.lib.requestHistoryActions as actions_mod  # type: ignore

            append_entry(
                "rid-1",
                "prompt1",
                "resp1",
                axes={"directional": ["fog"]},
            )
            actions_mod._cursor_offset = 0
            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_prev()
            notify_mock.assert_called()
            self.assertIn("No older history entry", str(notify_mock.call_args[0][0]))
            self.assertEqual(requestlog.last_drop_reason(), "")

        def test_show_entry_sets_provider(self):
            append_entry(
                "rid-3",
                "prompt",
                "resp3",
                "meta3",
                recipe="infer · full",
                axes={"directional": ["fog"]},
                provider_id="gemini",
            )
            HistoryActions.gpt_request_history_show_latest()
            self.assertEqual(getattr(GPTState, "current_provider_id", ""), "gemini")

        def test_show_entry_clears_provider_when_missing(self):
            setattr(GPTState, "current_provider_id", "stale-provider")
            append_entry(
                "rid-3b",
                "prompt",
                "resp3",
                "meta3",
                recipe="infer · full",
                axes={"directional": ["fog"]},
            )
            HistoryActions.gpt_request_history_show_latest()
            self.assertEqual(getattr(GPTState, "current_provider_id", ""), "")

        def test_history_save_latest_source_writes_markdown_with_prompt(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            GPTState.last_history_save_path = "stale"

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
            self.assertTrue(os.path.realpath(path).startswith(os.path.realpath(tmpdir)), "save dir should respect setting")

            notify_calls = [c for c in actions.user.calls if c[0] == "notify"]
            app_notify_calls = [c for c in actions.app.calls if c[0] == "notify"]
            self.assertGreaterEqual(
                len(notify_calls) + len(app_notify_calls),
                1,
                "Expected at least one notification about saving history source",
            )
            result_path = HistoryActions.gpt_request_history_save_latest_source()
            self.assertIsNotNone(result_path)
            self.assertTrue(os.path.realpath(str(result_path)).startswith(os.path.realpath(tmpdir)))
            self.assertTrue(os.path.exists(result_path))
            self.assertEqual(
                GPTState.last_history_save_path,
                result_path,
                "Should track last history save path on success",
            )

        def test_history_save_emits_lifecycle_hook(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore
            talon_settings.set("user.model_source_save_directory", tmpdir)

            append_entry(
                "rid-hook",
                "prompt hook",
                "resp hook",
                "meta hook",
                axes={"directional": ["fog"]},
            )
            with patch.object(history_actions, "emit_history_saved") as emit_mock:
                path = HistoryActions.gpt_request_history_save_latest_source()
            self.assertIsNotNone(path)
            emit_mock.assert_called_once()
            called_path, called_rid = emit_mock.call_args[0]
            self.assertEqual(os.path.realpath(path or ""), os.path.realpath(called_path))
            self.assertEqual(called_rid, "rid-hook")

        def test_history_save_latest_source_handles_empty_prompt(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            GPTState.last_history_save_path = "stale"

            append_entry(
                "rid-empty",
                "",
                "resp",
                "meta",
                recipe="infer · full · rigor",
            )

            with patch.object(history_actions, "notify") as notify_mock:
                before = set(os.listdir(tmpdir))
                result = HistoryActions.gpt_request_history_save_latest_source()
                after = set(os.listdir(tmpdir))

            self.assertEqual(before, after, "No files should be written for empty prompts")
            notify_mock.assert_called()
            self.assertIsNone(result)
            self.assertEqual(GPTState.last_history_save_path, "")

        def test_history_save_latest_source_returns_none_when_no_history(self):
            actions.user.calls.clear()
            GPTState.last_history_save_path = "stale"
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_save_latest_source()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertEqual(GPTState.last_history_save_path, "")

        def test_history_last_save_path_returns_realpath(self):
            tmpdir = tempfile.mkdtemp()
            rel_path = os.path.join(tmpdir, "..", os.path.basename(tmpdir), "file.md")
            os.makedirs(os.path.dirname(rel_path), exist_ok=True)
            with open(rel_path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = rel_path

            returned = HistoryActions.gpt_request_history_last_save_path()

            self.assertEqual(returned, os.path.realpath(rel_path))
            self.assertEqual(GPTState.last_history_save_path, os.path.realpath(rel_path))

        def test_history_last_save_path_returns_path_when_available(self):
            tmpdir = tempfile.mkdtemp()
            path = os.path.join(tmpdir, "saved-history.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write("content")
            GPTState.last_history_save_path = path
            self.assertEqual(
                HistoryActions.gpt_request_history_last_save_path(),
                os.path.realpath(path),
            )

        def test_history_last_save_path_ignores_directory(self):
            tmpdir = tempfile.mkdtemp()
            dir_path = os.path.join(tmpdir, "saved-history-dir")
            os.makedirs(dir_path, exist_ok=True)
            GPTState.last_history_save_path = dir_path
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertEqual(GPTState.last_history_save_path, "")

        def test_history_last_save_path_notifies_when_missing(self):
            GPTState.last_history_save_path = ""
            with patch.object(history_actions, "notify") as notify_mock:
                result = HistoryActions.gpt_request_history_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertIn("model history save source", str(notify_mock.call_args[0][0]))

        def test_history_last_save_path_clears_missing_file(self):
            missing = "/tmp/saved-history-missing.md"
            GPTState.last_history_save_path = missing
            with patch.object(history_actions, "notify") as notify_mock, patch(
                "os.path.exists", return_value=False
            ):
                result = HistoryActions.gpt_request_history_last_save_path()
            self.assertIsNone(result)
            notify_mock.assert_called()
            self.assertIn("model history save source", str(notify_mock.call_args[0][0]))
            self.assertEqual(GPTState.last_history_save_path, "")

        def test_history_save_filename_includes_request_and_directional_slug(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)

            append_entry(
                "rid-slug",
                "prompt with slug",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"], "scope": ["focus"]},
            )

            HistoryActions.gpt_request_history_save_latest_source()

            files = list(os.listdir(tmpdir))
            self.assertEqual(len(files), 1, files)
            filename = files[0]
            self.assertIn("rid-slug", filename)
            self.assertIn("fog", filename)

        def test_history_save_filename_includes_provider_slug(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)

            append_entry(
                "rid-provider",
                "prompt with provider",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
                provider_id="gemini-pro",
            )

            HistoryActions.gpt_request_history_save_latest_source()

            files = list(os.listdir(tmpdir))
            self.assertEqual(len(files), 1, files)
            filename = files[0]
            self.assertIn("gemini-pro", filename)

        def test_history_save_notify_path_includes_filename(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-ntf",
                "prompt notify",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            with patch.object(history_actions, "notify") as notify_mock:
                HistoryActions.gpt_request_history_save_latest_source()

            notify_calls = [call for call in notify_mock.call_args_list]
            self.assertTrue(
                any("rid-ntf" in str(args[0]) for args, _ in notify_calls),
                "Notify should include saved filename path",
            )

        def test_history_save_blocks_when_request_in_flight(self):
            append_entry(
                "rid-guard",
                "prompt",
                "resp",
                "meta",
                recipe="infer · full · rigor",
            )
            with (
                patch.object(history_actions, "_reject_if_request_in_flight", return_value=True),
                patch.object(history_actions, "_save_history_prompt_to_file") as save_mock,
            ):
                result = HistoryActions.gpt_request_history_save_latest_source()
            save_mock.assert_not_called()
            self.assertIsNone(result)
            self.assertEqual(GPTState.last_history_save_path, "")

        def test_history_save_includes_provider_id_in_header(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-provider",
                "prompt with provider",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
                provider_id="gemini",
            )

            HistoryActions.gpt_request_history_save_latest_source()

            files = list(os.listdir(tmpdir))
            self.assertEqual(len(files), 1, files)
            content = open(os.path.join(tmpdir, files[0]), "r", encoding="utf-8").read()
            self.assertIn("provider_id: gemini", content)

        def test_history_save_uses_utc_timestamp(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-time",
                "prompt with time",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            HistoryActions.gpt_request_history_save_latest_source()

            files = list(os.listdir(tmpdir))
            self.assertEqual(len(files), 1, files)
            content = open(os.path.join(tmpdir, files[0]), "r", encoding="utf-8").read()
            self.assertRegex(content, r"^saved_at: .*Z", "saved_at should be UTC (Z)")

        def test_history_save_blocks_when_current_state_in_flight(self):
            append_entry(
                "rid-flight",
                "prompt",
                "resp",
                "meta",
                recipe="infer · full · rigor",
            )

            class State:
                def __init__(self, phase):
                    self.phase = phase

            with (
                patch.object(history_actions, "current_state", return_value=State(RequestPhase.STREAMING)),
                patch.object(history_actions, "notify") as notify_mock,
                patch.object(history_actions, "_save_history_prompt_to_file") as save_mock,
            ):
                HistoryActions.gpt_request_history_save_latest_source()
            save_mock.assert_not_called()
            notify_mock.assert_called()

        def test_history_save_succeeds_after_terminal_phase(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-done",
                "prompt terminal",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            class State:
                def __init__(self, phase):
                    self.phase = phase

            with patch.object(history_actions, "current_state", return_value=State(RequestPhase.DONE)):
                HistoryActions.gpt_request_history_save_latest_source()

            files = list(os.listdir(tmpdir))
            self.assertEqual(len(files), 1, files)

        def test_history_save_notifies_after_terminal_phase(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-notify",
                "prompt notify",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            class State:
                def __init__(self, phase):
                    self.phase = phase

            with (
                patch.object(history_actions, "current_state", return_value=State(RequestPhase.DONE)),
                patch.object(history_actions, "notify") as notify_mock,
            ):
                HistoryActions.gpt_request_history_save_latest_source()

            notify_calls = [args[0] for args, _ in notify_mock.call_args_list]
            self.assertTrue(any("Saved history source to" in str(msg) for msg in notify_calls))

        def test_history_save_creates_unique_files_for_multiple_entries(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-1",
                "prompt one",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )
            append_entry(
                "rid-2",
                "prompt two",
                "resp",
                "meta",
                recipe="infer · gist · rigor",
                axes={"directional": ["rog"]},
            )

            HistoryActions.gpt_request_history_save_latest_source()
            HistoryActions.gpt_request_history_save_latest_source()

            files = sorted(os.listdir(tmpdir))
            self.assertEqual(len(files), 2, files)
            self.assertIn("rid-2", files[0] + files[1])
            self.assertNotEqual(files[0], files[1], "Expected unique filenames per save attempt")

        def test_history_save_returns_unique_paths_on_dedupe(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-dedupe",
                "prompt one",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            first_path = HistoryActions.gpt_request_history_save_latest_source()
            second_path = HistoryActions.gpt_request_history_save_latest_source()

            self.assertIsNotNone(first_path)
            self.assertIsNotNone(second_path)
            self.assertNotEqual(first_path, second_path)
            self.assertTrue(os.path.exists(first_path))
            self.assertTrue(os.path.exists(second_path))

        def test_history_save_returns_absolute_path_for_relative_setting(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", "relative-save-dir")
            GPTState.last_history_save_path = ""

            append_entry(
                "rid-abs",
                "prompt abs",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                result = HistoryActions.gpt_request_history_save_latest_source()
            finally:
                os.chdir(cwd)

            self.assertIsNotNone(result)
            self.assertTrue(os.path.isabs(result or ""))
            expected_root = os.path.realpath(tmpdir)
            self.assertTrue(str(os.path.realpath(result or "")).startswith(expected_root))
            self.assertTrue(os.path.exists(result or ""))
            self.assertEqual(GPTState.last_history_save_path, result)

        def test_history_save_sequence_inflight_then_terminal(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-seq",
                "prompt seq",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={"directional": ["fog"]},
            )

            class State:
                def __init__(self, phase):
                    self.phase = phase

            with (
                patch.object(history_actions, "current_state", return_value=State(RequestPhase.SENDING)),
                patch.object(history_actions, "_save_history_prompt_to_file") as save_mock,
            ):
                HistoryActions.gpt_request_history_save_latest_source()
            save_mock.assert_not_called()

            with patch.object(history_actions, "current_state", return_value=State(RequestPhase.DONE)):
                HistoryActions.gpt_request_history_save_latest_source()
            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1, files)

        def test_history_save_writes_axes_headers(self):
            tmpdir = tempfile.mkdtemp()
            from talon import settings as talon_settings  # type: ignore

            talon_settings.set("user.model_source_save_directory", tmpdir)
            append_entry(
                "rid-axes",
                "prompt axes",
                "resp",
                "meta",
                recipe="infer · full · rigor",
                axes={
                    "completeness": ["full"],
                    "scope": ["focus"],
                    "method": ["steps"],
                    "form": ["bullets"],
                    "channel": ["slack"],
                    "directional": ["fog"],
                },
            )

            HistoryActions.gpt_request_history_save_latest_source()

            files = os.listdir(tmpdir)
            self.assertEqual(len(files), 1, files)
            content = open(os.path.join(tmpdir, files[0]), "r", encoding="utf-8").read()
            self.assertIn("completeness_tokens: full", content)
            self.assertIn("scope_tokens: focus", content)
            self.assertIn("method_tokens: steps", content)
            self.assertIn("form_tokens: bullets", content)
            self.assertIn("channel_tokens: slack", content)
            self.assertIn("directional_tokens: fog", content)

else:
    if not TYPE_CHECKING:

        class RequestHistoryActionTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
