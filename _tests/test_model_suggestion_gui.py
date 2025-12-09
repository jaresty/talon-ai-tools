import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

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
    )
    from talon_user.lib import modelSuggestionGUI

    class ModelSuggestionGUITests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            SuggestionGUIState.suggestions = []
            SuggestionCanvasState.showing = False
            self._original_notify = actions.app.notify
            actions.app.notify = MagicMock()
            actions.user.gpt_apply_prompt = MagicMock()
            actions.user.model_prompt_recipe_suggestions_gui_close = MagicMock()

        def tearDown(self):
            # Restore the original notify implementation so other tests that
            # rely on the stubbed `actions.app.calls` behaviour continue to
            # work as expected.
            actions.app.notify = self._original_notify

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

        def test_open_uses_cached_suggestions_and_shows_canvas(self):
            """model_prompt_recipe_suggestions_gui_open populates state and opens the canvas."""
            GPTState.last_suggested_recipes = [
                {
                    "name": "Quick scan",
                    "recipe": "dependency · gist · relations · steps · plain · fog",
                },
            ]
            self.assertFalse(SuggestionCanvasState.showing)
            self.assertEqual(SuggestionGUIState.suggestions, [])

            UserActions.model_prompt_recipe_suggestions_gui_open()

            # Suggestions should be copied into GUI state and the canvas opened.
            self.assertTrue(SuggestionCanvasState.showing)
            self.assertEqual(len(SuggestionGUIState.suggestions), 1)

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
                    "recipe": "ticket · full · actions edges · structure flow · jira faq · fog",
                },
            ]

            UserActions.model_prompt_recipe_suggestions_run_index(1)

            # Suggestion should have been executed and the GUI closed.
            actions.user.gpt_apply_prompt.assert_called_once()
            actions.user.model_prompt_recipe_suggestions_gui_close.assert_called_once()

            # GPTState last_* fields should reflect the parsed multi-tag axes.
            self.assertEqual(GPTState.last_static_prompt, "ticket")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_directional, "fog")

            # Scope/method/style are stored as space-separated token strings
            # built from recognised axis tokens.
            self.assertEqual(GPTState.last_scope, "actions edges")
            self.assertEqual(GPTState.last_method, "structure flow")
            self.assertEqual(GPTState.last_style, "jira faq")

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

else:
    if not TYPE_CHECKING:
        class ModelSuggestionGUITests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass
