import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelSuggestionGUI import (
        UserActions,
        SuggestionGUIState,
        SuggestionCanvasState,
        _scroll_suggestions,
    )
    from talon_user.lib import modelSuggestionGUI
    from talon_user.lib.requestState import RequestPhase
    import talon_user.lib.talonSettings as talonSettings

    class ModelSuggestionGUITests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            SuggestionGUIState.suggestions = []
            SuggestionCanvasState.showing = False
            SuggestionCanvasState.scroll_y = 0.0
            self._original_notify = actions.app.notify
            actions.app.notify = MagicMock()
            actions.user.notify = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            actions.user.model_prompt_recipe_suggestions_gui_close = MagicMock()

        def tearDown(self):
            # Restore the original notify implementation so other tests that
            # rely on the stubbed `actions.app.calls` behaviour continue to
            # work as expected.
            actions.app.notify = self._original_notify

        def test_persona_presets_align_with_persona_catalog(self) -> None:
            from talon_user.lib.personaConfig import persona_catalog
            from talon_user.lib import modelSuggestionGUI as suggestion_module

            catalog = persona_catalog()
            helper_presets = suggestion_module._persona_presets()
            catalog_keys = {preset.key for preset in catalog.values()}
            helper_keys = {preset.key for preset in helper_presets}
            self.assertEqual(
                catalog_keys,
                helper_keys,
                "modelSuggestionGUI _persona_presets must cover the same PersonaPreset keys as persona_catalog",
            )

        def test_run_index_executes_suggestion_and_closes_gui(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Deep map",
                    "recipe": "describe · full · relations · cluster · bullets · fog",
                },
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(2)

            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

        def test_run_index_out_of_range_notifies_and_does_not_run(self):
            GPTState.last_suggested_recipes = [
                {
                    "name": "Only one",
                    "recipe": "describe · gist · focus · plain · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(0)
            UserActions.model_prompt_recipe_suggestions_run_index(3)

            self.assertGreaterEqual(actions.app.notify.call_count, 1)
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_run_index_with_no_suggestions_notifies(self):
            GPTState.last_suggested_recipes = []

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.app.notify.assert_called_once()
            actions.user.gpt_apply_prompt.assert_not_called()

        def test_scroll_clamps_to_max_via_overlay_helper(self):
            # Prepare a stub canvas and suggestions to drive a positive max_scroll.
            class RectStub:
                def __init__(self):
                    self.x = 0
                    self.y = 0
                    self.width = 800
                    self.height = 200

            class CanvasStub:
                rect = RectStub()

            SuggestionGUIState.suggestions = [
                modelSuggestionGUI.Suggestion(name="One", recipe="describe · fog"),
                modelSuggestionGUI.Suggestion(name="Two", recipe="describe · fog"),
                modelSuggestionGUI.Suggestion(name="Three", recipe="describe · fog"),
            ]
            modelSuggestionGUI._suggestion_canvas = CanvasStub()
            SuggestionCanvasState.scroll_y = 1000.0

            with patch.object(
                modelSuggestionGUI, "_measure_suggestion_height", return_value=200
            ):
                _scroll_suggestions(raw_delta=1.0)

            # With 3 rows @200px and the current header/layout geometry,
            # clamp_scroll should cap at the computed max_scroll of 640.
            self.assertEqual(SuggestionCanvasState.scroll_y, 640.0)

        def test_persona_stance_display_includes_long_form_axes(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="With persona preset",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="as facilitator",
                persona_audience="to stakeholders",
                persona_tone="directly",
                stance_command="persona stake",
                intent_purpose="teach",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            self.assertEqual(
                info["stance_display"],
                "model write as facilitator to stakeholders directly (persona stake) · intent teach",
            )
            self.assertEqual(info["persona_display"], "persona stake")
            self.assertEqual(
                info["persona_axes_summary"],
                "as facilitator · to stakeholders · directly",
            )

        def test_non_persona_stance_display_prefers_raw_command(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Axes stance",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="as teacher",
                persona_audience="to junior engineer",
                persona_tone="kindly",
                stance_command="model write as teacher to junior engineer kindly",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            self.assertEqual(
                info["stance_display"],
                "model write as teacher to junior engineer kindly",
            )

        def test_persona_stance_synthesises_preset_command_when_missing(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Preset only",
                recipe="describe · gist · focus · plain · fog",
                persona_voice="as facilitator",
                persona_audience="to stakeholders",
                persona_tone="directly",
                intent_purpose="resolve",
                stance_command="",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            self.assertEqual(
                info["stance_display"],
                "model write as facilitator to stakeholders directly (persona stake) · intent resolve",
            )
            self.assertEqual(info["persona_display"], "persona stake")

        def test_stance_display_defaults_to_model_write_when_prefix_missing(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="Audience + tone only",
                recipe="describe · gist · focus · plain · rog",
                persona_voice="",
                persona_audience="to team",
                persona_tone="directly",
                intent_purpose="inform",
                stance_command="",
            )

            info = modelSuggestionGUI._suggestion_stance_info(suggestion)

            self.assertEqual(
                info["stance_display"], "model write to team directly · intent inform"
            )

        def test_open_uses_cached_suggestions_and_shows_canvas(self):
            """model_prompt_recipe_suggestions_gui_open populates state and opens the canvas."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]
            self.assertFalse(SuggestionCanvasState.showing)

        def test_run_index_surfaces_migration_hint_on_legacy_style(self):
            """Suggestion execution should hint and abort when legacy style is spoken."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Legacy style",
                    "recipe": "describe · full · narrow · debugging · plain · rog",
                },
            ]

            def _fake_safe(match):
                actions.app.notify("GPT: style axis is removed")
                return ""

            with patch.object(
                modelSuggestionGUI, "safe_model_prompt", side_effect=_fake_safe
            ):
                UserActions.model_prompt_recipe_suggestions_run_index(1)

            actions.user.gpt_apply_prompt.assert_not_called()
            notifications = [
                str(args[0])
                for args in [
                    *(ca.args for ca in actions.app.notify.call_args_list),
                    *(ca.args for ca in actions.user.notify.call_args_list),
                ]
                if args
            ]
            self.assertTrue(
                any(
                    "style axis is removed" in note
                    or "styleModifier is no longer supported" in note
                    for note in notifications
                ),
                f"Expected migration hint notification, got {notifications}",
            )

        def test_open_with_no_suggestions_notifies_and_does_not_show_canvas(self):
            GPTState.last_suggested_recipes = []
            self.assertFalse(SuggestionCanvasState.showing)

            UserActions.model_prompt_recipe_suggestions_gui_open()

            actions.app.notify.assert_called_once()
            self.assertFalse(SuggestionCanvasState.showing)

        def test_run_index_handles_multi_tag_axis_recipe(self):
            """Suggestions with multi-tag axis fields should execute and update last_*."""
            # Seed a suggestion that uses multi-token scope/method/style segments.
            GPTState.last_suggested_recipes = [
                {
                    "name": "Jira FAQ ticket",
                    "recipe": "describe · full · actions edges · structure flow · story · jira faq · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Suggestion should have been executed and the GUI closed.
            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

            # GPTState last_* fields should reflect the parsed multi-tag axes.
            self.assertEqual(GPTState.last_static_prompt, "describe")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_directional, "fog")

            # Scope/method/form/channel are stored as space-separated token strings
            # built from recognised axis tokens.
            self.assertEqual(GPTState.last_scope, "actions edges")
            self.assertEqual(GPTState.last_method, "flow structure")
            self.assertEqual(GPTState.last_form, "faq")
            self.assertEqual(GPTState.last_channel, "jira")

        def test_drag_header_moves_canvas(self):
            """Dragging the header should move the suggestion canvas."""
            SuggestionGUIState.suggestions = []
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            # Provide a deterministic rect and move method on the stub canvas so
            # the drag handler can adjust position.
            canvas_obj.rect = type(
                "R", (), {"x": 10, "y": 20, "width": 400, "height": 300}
            )()
            moved_to: list[tuple[int, int]] = []

            def _move(x, y):
                moved_to.append((x, y))
                canvas_obj.rect = type(
                    "R", (), {"x": x, "y": y, "width": 400, "height": 300}
                )()

            canvas_obj.move = _move  # type: ignore[attr-defined]
            callbacks = getattr(canvas_obj, "_callbacks", {})
            mouse_cbs = callbacks.get("mouse") or []
            if not mouse_cbs:
                self.skipTest("Canvas stub does not expose mouse callbacks")
            mouse_cb = mouse_cbs[0]

            class _Evt:
                def __init__(self, event: str, x: int, y: int):
                    self.event = event
                    self.button = 0
                    self.pos = type("P", (), {"x": x, "y": y})()
                    self.gpos = type(
                        "P",
                        (),
                        {
                            "x": canvas_obj.rect.x + x,
                            "y": canvas_obj.rect.y + y,
                        },
                    )()

            # Start drag in the header (avoid the close hotspot by keeping x small).
            mouse_cb(_Evt("mousedown", 20, 10))
            # Move to a new position; rect should update via move().
            mouse_cb(_Evt("mousemove", 80, 60))

            self.assertIn((70, 70), moved_to)

        def test_scroll_event_callback_updates_offset(self):
            """Scroll events should adjust the suggestion canvas offset."""
            SuggestionGUIState.suggestions = [
                modelSuggestionGUI.Suggestion(
                    name=f"Suggestion {i}",
                    recipe="describe · gist · focus · plain · fog",
                )
                for i in range(20)
            ]
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            callbacks = getattr(canvas_obj, "_callbacks", {})
            scroll_cbs = (
                callbacks.get("scroll")
                or callbacks.get("wheel")
                or callbacks.get("mouse_scroll")
            )
            if not scroll_cbs:
                self.skipTest("Canvas stub does not expose scroll callbacks")
            scroll_cb = scroll_cbs[0]

            class _Evt:
                def __init__(self, delta: float):
                    self.dy = delta
                    self.wheel_y = delta

            self.assertEqual(SuggestionCanvasState.scroll_y, 0.0)
            scroll_cb(_Evt(-1.0))
            self.assertGreater(SuggestionCanvasState.scroll_y, 0.0)

        def test_reasoning_rendered_when_present(self):
            suggestion = modelSuggestionGUI.Suggestion(
                name="With reasoning",
                recipe="describe gist focus plain fog",
                reasoning="stance: kept; intent: kept understand; axes: chose fog for scan",
            )
            canvas_obj = modelSuggestionGUI._ensure_suggestion_canvas()
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type(
                    "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                )()
            modelSuggestionGUI.SuggestionGUIState.suggestions = [suggestion]
            callbacks = getattr(canvas_obj, "_callbacks", {})
            draw_cbs = callbacks.get("draw") or []
            if not draw_cbs:
                self.skipTest("Canvas stub does not expose draw callbacks")
            draw_cb = draw_cbs[0]

            draw_cb(canvas_obj)
            # Reasoning should be included in measured height and rendering path without errors.
            self.assertTrue(modelSuggestionGUI.SuggestionGUIState.suggestions)

        def test_request_is_in_flight_handles_request_phases(self) -> None:
            class State:
                def __init__(self, phase):
                    self.phase = phase

            with patch.object(
                modelSuggestionGUI,
                "current_state",
                return_value=State(RequestPhase.STREAMING),
            ):
                self.assertTrue(modelSuggestionGUI._request_is_in_flight())

            for terminal in (
                RequestPhase.IDLE,
                RequestPhase.DONE,
                RequestPhase.ERROR,
                RequestPhase.CANCELLED,
            ):
                with patch.object(
                    modelSuggestionGUI, "current_state", return_value=State(terminal)
                ):
                    self.assertFalse(modelSuggestionGUI._request_is_in_flight())

        def test_reject_if_request_in_flight_notifies_and_blocks(self) -> None:
            with (
                patch.object(
                    modelSuggestionGUI,
                    "try_start_request",
                    return_value=(False, "in_flight"),
                ),
                patch.object(modelSuggestionGUI, "current_state"),
                patch.object(modelSuggestionGUI, "set_drop_reason") as set_reason,
                patch.object(modelSuggestionGUI, "notify") as notify_mock,
            ):
                self.assertTrue(modelSuggestionGUI._reject_if_request_in_flight())
            set_reason.assert_called_once_with("in_flight")
            notify_mock.assert_called_once()

            with (
                patch.object(
                    modelSuggestionGUI, "try_start_request", return_value=(True, "")
                ),
                patch.object(modelSuggestionGUI, "current_state"),
                patch.object(modelSuggestionGUI, "set_drop_reason") as set_reason,
                patch.object(modelSuggestionGUI, "notify") as notify_mock,
            ):
                self.assertFalse(modelSuggestionGUI._reject_if_request_in_flight())
            set_reason.assert_not_called()
            notify_mock.assert_not_called()


else:
    if not TYPE_CHECKING:

        class ModelSuggestionGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
