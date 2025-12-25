import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelResponseCanvas import (
        ResponseCanvasState,
        UserActions,
        _ensure_response_canvas,
        register_response_draw_handler,
        unregister_response_draw_handler,
    )
    from talon import actions
    from talon_user.lib.modelState import GPTState
    from talon_user.lib import streamingCoordinator
    from talon_user.lib import modelResponseCanvas
    from talon_user.lib.requestState import RequestPhase, RequestState
    from talon_user.lib.personaConfig import PersonaPreset

    class ModelResponseCanvasTests(unittest.TestCase):
        def setUp(self) -> None:
            ResponseCanvasState.showing = False
            ResponseCanvasState.scroll_y = 0.0
            ResponseCanvasState.meta_expanded = False
            ResponseCanvasState.meta_pinned_request_id = ""
            GPTState.text_to_confirm = ""
            GPTState.last_streaming_snapshot = {}
            try:
                import talon_user.lib.modelResponseCanvas as mrc

                mrc._last_meta_signature = None  # type: ignore[attr-defined]
            except Exception:
                modelResponseCanvas._last_meta_signature = None  # type: ignore[attr-defined]
            modelResponseCanvas.reset_persona_intent_maps_cache()
            self._state_patch = patch.object(
                modelResponseCanvas,
                "current_state",
                return_value=RequestState(),
            )
            self._state_patch.start()

        def _render_recap_lines(
            self,
            recipe_snapshot: dict[str, object],
            grammar_phrase: str,
            recap_snapshot: dict[str, str] | None = None,
            persona_maps=None,
        ) -> list[str]:
            captured: list[str] = []
            effective_recap = recap_snapshot or {"response": "answer body", "meta": ""}
            with ExitStack() as stack:
                stack.enter_context(
                    patch.object(
                        modelResponseCanvas,
                        "last_recipe_snapshot",
                        return_value=recipe_snapshot,
                    )
                )
                stack.enter_context(
                    patch.object(
                        modelResponseCanvas,
                        "last_recap_snapshot",
                        return_value=effective_recap,
                    )
                )
                stack.enter_context(
                    patch.object(
                        modelResponseCanvas,
                        "suggestion_grammar_phrase",
                        return_value=grammar_phrase,
                    )
                )
                if persona_maps is not None:
                    stack.enter_context(
                        patch.object(
                            modelResponseCanvas,
                            "persona_intent_maps",
                            return_value=persona_maps,
                        )
                    )
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                original_draw_text = getattr(canvas_obj, "draw_text", None)

                def _capture(text, *args, **kwargs):
                    captured.append(str(text))
                    if original_draw_text:
                        return original_draw_text(text, *args, **kwargs)
                    return None

                stack.enter_context(patch.object(canvas_obj, "draw_text", new=_capture))
                callbacks = getattr(canvas_obj, "_callbacks", {})
                for cb in callbacks.get("draw") or []:
                    cb(canvas_obj)
            return captured

        def tearDown(self) -> None:
            try:
                self._state_patch.stop()
            except Exception:
                pass

        def test_open_is_idempotent_and_toggle_closes(self) -> None:
            GPTState.last_response = "line one\nline two"
            _ensure_response_canvas()

            UserActions.model_response_canvas_open()
            self.assertTrue(ResponseCanvasState.showing)

            UserActions.model_response_canvas_open()
            self.assertTrue(ResponseCanvasState.showing)

            UserActions.model_response_canvas_toggle()
            self.assertFalse(ResponseCanvasState.showing)

        def test_refresh_preserves_expanded_meta(self) -> None:
            """Hiding/showing during refresh should not collapse meta."""
            GPTState.last_response = "line one\nline two"
            ResponseCanvasState.meta_expanded = True
            ResponseCanvasState.meta_pinned_request_id = "req-refresh"
            canvas_obj = _ensure_response_canvas()
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type(
                    "R", (), {"x": 0, "y": 0, "width": 400, "height": 300}
                )()
            canvas_obj.show()
            ResponseCanvasState.showing = True

            UserActions.model_response_canvas_refresh()

            self.assertTrue(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "req-refresh")

        def test_refresh_does_not_hide_when_showing(self) -> None:
            class DummyCanvas:
                def __init__(self):
                    self.hide_called = False
                    self.show_calls = 0

                def hide(self):
                    self.hide_called = True

                def show(self):
                    self.show_calls += 1

            dummy = DummyCanvas()
            modelResponseCanvas._response_canvas = dummy  # type: ignore[attr-defined]
            ResponseCanvasState.showing = True
            ResponseCanvasState.scroll_y = 123.0

            with patch.object(
                modelResponseCanvas, "_guard_response_canvas", return_value=False
            ):
                UserActions.model_response_canvas_refresh()

            self.assertFalse(dummy.hide_called)
            self.assertGreater(dummy.show_calls, 0)
            self.assertEqual(ResponseCanvasState.scroll_y, 123.0)

        def test_response_canvas_uses_lifecycle_drop_helpers(self) -> None:
            import talon_user.lib.historyLifecycle as history_lifecycle

            self.assertIs(
                modelResponseCanvas.set_drop_reason, history_lifecycle.set_drop_reason
            )
            self.assertIs(
                modelResponseCanvas.last_drop_reason, history_lifecycle.last_drop_reason
            )

        def test_open_without_answer_is_safe(self) -> None:
            GPTState.last_response = ""
            _ensure_response_canvas()

            UserActions.model_response_canvas_open()
            # With no response/meta, opening is a no-op.
            self.assertFalse(ResponseCanvasState.showing)

        def test_meta_collapses_on_new_recap_signature(self) -> None:
            """Expanded meta should reset when a new response/meta is rendered."""
            ResponseCanvasState.meta_expanded = True
            ResponseCanvasState.meta_pinned_request_id = "req-old"
            modelResponseCanvas._last_meta_signature = (  # type: ignore[attr-defined]
                "req-old",
                "old",
                "old_meta",
                "old_recipe",
            )
            GPTState.last_response = "new response text"
            GPTState.last_meta = "meta block"
            GPTState.last_recipe = "new recipe"
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(request_id="req-new"),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertFalse(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "")
            self.assertEqual(
                modelResponseCanvas._last_meta_signature,  # type: ignore[attr-defined]
                ("req-new", "new response text", "meta block", "new recipe"),
            )

        def test_meta_stays_expanded_for_inflight_updates(self) -> None:
            """User-expanded meta should stay open as a request streams new content."""
            ResponseCanvasState.meta_expanded = True
            modelResponseCanvas._last_meta_signature = (  # type: ignore[attr-defined]
                "req-same",
                "old",
                "old_meta",
                "old_recipe",
            )
            GPTState.last_response = "new response text"
            GPTState.last_meta = "meta block"
            GPTState.last_recipe = "new recipe"
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(
                    phase=RequestPhase.STREAMING, request_id="req-same"
                ),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "req-same")
            self.assertEqual(
                modelResponseCanvas._last_meta_signature,  # type: ignore[attr-defined]
                ("req-same", "new response text", "meta block", "new recipe"),
            )

        def test_meta_stays_expanded_when_request_id_missing_on_completion(
            self,
        ) -> None:
            """If request id drops after completion, keep meta open using last known id."""
            ResponseCanvasState.meta_expanded = True
            modelResponseCanvas._last_meta_signature = (  # type: ignore[attr-defined]
                "req-same",
                "old",
                "old_meta",
                "old_recipe",
            )
            GPTState.last_response = "final response"
            GPTState.last_meta = "final meta"
            GPTState.last_recipe = "final recipe"
            # Simulate a completion draw where the request id is missing in state.
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(phase=RequestPhase.DONE, request_id=""),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "req-same")
            self.assertEqual(
                modelResponseCanvas._last_meta_signature,  # type: ignore[attr-defined]
                ("req-same", "final response", "final meta", "final recipe"),
            )

        def test_meta_stays_expanded_when_request_id_appears_mid_request(self) -> None:
            """Avoid collapsing when a late-arriving request id matches the same inflight request."""
            ResponseCanvasState.meta_expanded = True
            modelResponseCanvas._last_meta_signature = (  # type: ignore[attr-defined]
                "",
                "old",
                "old_meta",
                "old_recipe",
            )
            GPTState.last_response = "later response"
            GPTState.last_meta = "later meta"
            GPTState.last_recipe = "later recipe"
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(
                    phase=RequestPhase.STREAMING, request_id="req-now"
                ),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "req-now")
            self.assertEqual(
                modelResponseCanvas._last_meta_signature,  # type: ignore[attr-defined]
                ("req-now", "later response", "later meta", "later recipe"),
            )

        def test_meta_collapse_when_pinned_request_changes(self) -> None:
            """Pinned meta should collapse when a different non-empty request id arrives."""
            ResponseCanvasState.meta_expanded = True
            ResponseCanvasState.meta_pinned_request_id = "req-a"
            modelResponseCanvas._last_meta_signature = (  # type: ignore[attr-defined]
                "req-a",
                "old",
                "old_meta",
                "old_recipe",
            )
            GPTState.last_response = "other response"
            GPTState.last_meta = "other meta"
            GPTState.last_recipe = "other recipe"
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(phase=RequestPhase.DONE, request_id="req-b"),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertFalse(ResponseCanvasState.meta_expanded)
            self.assertEqual(ResponseCanvasState.meta_pinned_request_id, "")

        def test_open_allows_inflight_progress_without_answer(self) -> None:
            GPTState.last_response = ""
            _ensure_response_canvas()
            with patch.object(
                modelResponseCanvas,
                "current_state",
                return_value=RequestState(phase=RequestPhase.SENDING),
            ):
                UserActions.model_response_canvas_open()
            self.assertTrue(ResponseCanvasState.showing)

        def test_custom_draw_handler_invoked_on_show(self) -> None:
            GPTState.last_response = "test"
            calls: list[object] = []

            def handler(c) -> None:
                calls.append(c)

            register_response_draw_handler(handler)
            try:
                canvas_obj = _ensure_response_canvas()
                canvas_obj.show()
                self.assertGreaterEqual(len(calls), 1)
            finally:
                unregister_response_draw_handler(handler)

        def test_mouse_scroll_adjusts_scroll_offset(self) -> None:
            GPTState.last_response = "line one\nline two\nline three"
            ResponseCanvasState.scroll_y = 0.0
            canvas_obj = _ensure_response_canvas()
            # In the Talon stub, Canvas.from_rect does not set rect; provide
            # a minimal rect so the mouse handler does not early-return.
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type(
                    "R", (), {"x": 0, "y": 0, "width": 400, "height": 300}
                )()
            # Access the registered mouse handler from the stub canvas.
            callbacks = getattr(canvas_obj, "_callbacks", {})
            mouse_cbs = callbacks.get("mouse") or []
            if not mouse_cbs:
                self.skipTest("Canvas stub does not expose mouse callbacks")
            mouse_cb = mouse_cbs[0]

            class _Evt:
                def __init__(self, dy: float):
                    self.event = "mouse_scroll"
                    self.dy = dy
                    # Minimal pos/gpos for handler hit-testing.
                    self.pos = type("P", (), {"x": 10, "y": 50})()
                    self.gpos = type("P", (), {"x": 10, "y": 50})()
                    self.button = None

            # Simulate scroll down.
            mouse_cb(_Evt(-1.0))
            self.assertGreater(ResponseCanvasState.scroll_y, 0.0)

            # Simulate scroll up enough to clamp back to zero.
            mouse_cb(_Evt(100.0))
            self.assertEqual(ResponseCanvasState.scroll_y, 0.0)

        def test_paste_button_closes_canvas_before_paste(self) -> None:
            GPTState.text_to_confirm = "paste me"
            ResponseCanvasState.showing = True
            canvas_obj = _ensure_response_canvas()
            if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                canvas_obj.rect = type(
                    "R", (), {"x": 0, "y": 0, "width": 400, "height": 300}
                )()
            canvas_obj.show()
            callbacks = getattr(canvas_obj, "_callbacks", {})
            mouse_cbs = callbacks.get("mouse") or []
            if not mouse_cbs:
                self.skipTest("Canvas stub does not expose mouse callbacks")
            mouse_cb = mouse_cbs[0]
            bounds = modelResponseCanvas._response_button_bounds.get("paste")  # type: ignore[attr-defined]
            if not bounds:
                self.skipTest("Paste button bounds not available")
            bx1, by1, _bx2, _by2 = bounds
            calls: list[str] = []
            orig_close = actions.user.model_response_canvas_close
            orig_paste = actions.user.confirmation_gui_paste

            def _close():
                calls.append("close")
                ResponseCanvasState.showing = False

            def _paste():
                calls.append("paste")

            actions.user.model_response_canvas_close = _close  # type: ignore[attr-defined]
            actions.user.confirmation_gui_paste = _paste  # type: ignore[attr-defined]
            try:

                class _Evt:
                    def __init__(self, x: int, y: int):
                        self.event = "mousedown"
                        self.button = 0
                        self.pos = type("P", (), {"x": x, "y": y})()
                        self.gpos = self.pos

                rel_x = bx1 - canvas_obj.rect.x + 1
                rel_y = by1 - canvas_obj.rect.y + 1
                mouse_cb(_Evt(rel_x, rel_y))
            finally:
                actions.user.model_response_canvas_close = orig_close  # type: ignore[attr-defined]
                actions.user.confirmation_gui_paste = orig_paste  # type: ignore[attr-defined]

            self.assertEqual(calls, ["close", "paste"])
            self.assertFalse(ResponseCanvasState.showing)

        def test_inflight_canvas_passes_snapshot_to_streaming_adapter(self) -> None:
            """Inflight canvas draws should pass streaming state through the streamingCoordinator adapter."""
            GPTState.text_to_confirm = "streamed"
            GPTState.last_streaming_snapshot = {
                "text": "streamed",
                "completed": False,
                "errored": False,
                "error_message": "",
            }

            with (
                patch.object(
                    modelResponseCanvas,
                    "_current_request_state",
                    return_value=RequestState(phase=RequestPhase.STREAMING),
                ),
                patch.object(
                    streamingCoordinator,
                    "canvas_view_from_snapshot",
                    side_effect=lambda snapshot: {
                        "text": snapshot.get("text", ""),
                        "status": "inflight",
                        "error_message": "",
                    },
                ) as mock_view,
            ):
                canvas_obj = _ensure_response_canvas()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(mock_view.called)
            snapshot_arg = mock_view.call_args[0][0]
            self.assertEqual(snapshot_arg["text"], "streamed")
            self.assertFalse(bool(snapshot_arg.get("completed")))
            self.assertFalse(bool(snapshot_arg.get("errored")))

        def test_cancel_button_shown_when_inflight_without_progress_pref(self) -> None:
            """Response canvas should surface a cancel affordance even when progress UI is disabled."""

            GPTState.current_destination_kind = "pill"
            with patch.object(
                modelResponseCanvas,
                "_current_request_state",
                return_value=RequestState(phase=RequestPhase.STREAMING),
            ):
                canvas_obj = _ensure_response_canvas()
                if not hasattr(canvas_obj, "rect") or canvas_obj.rect is None:
                    canvas_obj.rect = type(
                        "R", (), {"x": 0, "y": 0, "width": 500, "height": 400}
                    )()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            bounds = modelResponseCanvas._response_button_bounds.get("cancel")  # type: ignore[attr-defined]
            self.assertIsNotNone(
                bounds, "Expected cancel button bounds to be registered"
            )

        def test_error_canvas_passes_errored_snapshot_to_streaming_adapter(
            self,
        ) -> None:
            """Error-phase canvas draws should pass an errored snapshot to the streamingCoordinator adapter."""
            GPTState.text_to_confirm = "partial error text"
            GPTState.last_streaming_snapshot = {
                "text": "partial error text",
                "completed": False,
                "errored": True,
                "error_message": "timeout",
            }

            with (
                patch.object(
                    modelResponseCanvas,
                    "_current_request_state",
                    return_value=RequestState(phase=RequestPhase.ERROR),
                ),
                patch.object(
                    streamingCoordinator,
                    "canvas_view_from_snapshot",
                    side_effect=lambda snapshot: {
                        "text": snapshot.get("text", ""),
                        "status": "errored",
                        "error_message": "timeout",
                    },
                ) as mock_view,
            ):
                canvas_obj = _ensure_response_canvas()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(mock_view.called)
            snapshot_arg = mock_view.call_args[0][0]
            self.assertEqual(snapshot_arg["text"], "partial error text")
            self.assertFalse(bool(snapshot_arg.get("completed")))
            self.assertTrue(bool(snapshot_arg.get("errored")))

        def test_completed_snapshot_used_when_no_buffer_or_last_response(self) -> None:
            """Completed streaming snapshot should be used when buffers are empty."""
            GPTState.text_to_confirm = ""
            GPTState.last_streaming_snapshot = {
                "text": "final streamed text",
                "completed": True,
                "errored": False,
                "error_message": "",
            }

            with (
                patch.object(
                    modelResponseCanvas,
                    "_current_request_state",
                    return_value=RequestState(phase=RequestPhase.DONE),
                ),
                patch.object(
                    streamingCoordinator,
                    "canvas_view_from_snapshot",
                    side_effect=lambda snapshot: {
                        "text": snapshot.get("text", ""),
                        "status": "completed",
                        "error_message": "",
                    },
                ) as mock_view,
            ):
                canvas_obj = _ensure_response_canvas()
                callbacks = getattr(canvas_obj, "_callbacks", {})
                draw_cbs = callbacks.get("draw") or []
                for cb in draw_cbs:
                    cb(canvas_obj)

            self.assertTrue(mock_view.called)
            snapshot_arg = mock_view.call_args[0][0]
            self.assertEqual(snapshot_arg["text"], "final streamed text")
            self.assertTrue(bool(snapshot_arg.get("completed")))
            self.assertFalse(bool(snapshot_arg.get("errored")))

        def test_recap_surfaces_form_channel_directional_hint(self) -> None:
            """Recap line should remind users about single form/channel and the directional requirement."""

            GPTState.last_response = "answer body"
            GPTState.last_recipe = "infer · full · focus"
            GPTState.last_directional = "fog"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "focus"
            GPTState.last_method = "steps"
            GPTState.last_form = "bullets"
            GPTState.last_channel = "slack"

            recipe_snapshot = {
                "recipe": "infer · full · focus · steps · bullets · slack",
                "static_prompt": "infer",
                "completeness": "full",
                "scope_tokens": ["focus"],
                "method_tokens": ["steps"],
                "form_tokens": ["bullets"],
                "channel_tokens": ["slack"],
                "directional": "fog",
            }
            captured = self._render_recap_lines(
                recipe_snapshot=recipe_snapshot,
                grammar_phrase="model again fog",
            )

            axes_hint = [
                line for line in captured if "Axes: single directional lens" in line
            ]
            self.assertTrue(
                axes_hint,
                "Expected response recap to surface directional + form/channel singleton hint",
            )
            stance_lines = [line for line in captured if line.startswith("Stance:")]
            defaults_lines = [line for line in captured if line.startswith("Defaults:")]
            self.assertTrue(stance_lines, "Expected stance summary in response recap")
            self.assertTrue(
                defaults_lines, "Expected defaults summary in response recap"
            )

        def test_recap_surfaces_persona_and_intent_aliases(self) -> None:
            GPTState.last_response = "answer body"
            GPTState.last_recipe = "describe · gist"

            persona_maps = SimpleNamespace(
                persona_presets={},
                persona_preset_aliases={},
                intent_presets={
                    "decide": SimpleNamespace(
                        key="decide", label="Decide", intent="decide"
                    )
                },
                intent_preset_aliases={},
                intent_synonyms={},
                intent_display_map={"decide": "Decide"},
            )

            recipe_snapshot = {
                "recipe": "describe · gist",
                "static_prompt": "describe",
                "form_tokens": [],
                "channel_tokens": [],
                "persona_preset_key": "teach_junior_dev",
                "persona_preset_label": "Teach junior dev",
                "persona_preset_spoken": "mentor",
                "persona_voice": "as teacher",
                "persona_audience": "to junior dev",
                "persona_tone": "kindly",
                "intent_preset_key": "decide",
                "intent_purpose": "decide",
                "intent_display": "",
            }

            captured = self._render_recap_lines(
                recipe_snapshot=recipe_snapshot,
                grammar_phrase="model run describe gist",
                persona_maps=persona_maps,
            )

            persona_lines = [line for line in captured if "Persona:" in line]
            intent_lines = [line for line in captured if "Intent:" in line]
            self.assertTrue(
                any("mentor" in line.lower() for line in persona_lines),
                f"Expected persona alias in recap, saw: {persona_lines}",
            )
            self.assertTrue(
                any("teach_junior_dev" in line for line in persona_lines),
                f"Expected canonical persona key in recap, saw: {persona_lines}",
            )
            self.assertTrue(
                any(
                    "intent" in line.lower() and "decide" in line.lower()
                    for line in intent_lines
                ),
                f"Expected canonical intent in recap, saw: {intent_lines}",
            )

            stance_lines = [line for line in captured if line.startswith("Stance:")]
            defaults_lines = [line for line in captured if line.startswith("Defaults:")]
            self.assertTrue(stance_lines, "Expected stance summary in response recap")
            self.assertTrue(
                defaults_lines, "Expected defaults summary in response recap"
            )

        def test_recap_persona_falls_back_to_catalog_alias(self) -> None:
            GPTState.last_response = "answer body"
            GPTState.last_recipe = "describe · gist"

            persona_preset = PersonaPreset(
                key="teach_junior_dev",
                label="Teach junior dev",
                spoken="mentor",
                voice="as teacher",
                audience="to junior dev",
                tone="kindly",
            )
            persona_maps = SimpleNamespace(
                persona_presets={"teach_junior_dev": persona_preset},
                persona_preset_aliases={
                    "teach_junior_dev": "teach_junior_dev",
                    "mentor": "teach_junior_dev",
                    "teach junior dev": "teach_junior_dev",
                },
                intent_presets={},
                intent_preset_aliases={},
                intent_synonyms={},
                intent_display_map={"decide": "Decide"},
            )

            recipe_snapshot = {
                "recipe": "describe · gist",
                "static_prompt": "describe",
                "form_tokens": [],
                "channel_tokens": [],
                "persona_preset_key": "teach_junior_dev",
                "persona_preset_label": "",
                "persona_preset_spoken": "",
                "persona_voice": "as teacher",
                "persona_audience": "to junior dev",
                "persona_tone": "kindly",
                "intent_preset_key": "decide",
                "intent_purpose": "decide",
                "intent_display": "",
            }

            captured = self._render_recap_lines(
                recipe_snapshot=recipe_snapshot,
                grammar_phrase="model run describe gist",
                persona_maps=persona_maps,
            )

            persona_lines = [line for line in captured if "Persona:" in line]
            self.assertTrue(
                any("mentor" in line.lower() for line in persona_lines),
                f"Expected persona alias fallback, saw: {persona_lines}",
            )
            self.assertTrue(
                any("teach_junior_dev" in line for line in persona_lines),
                f"Expected canonical persona key fallback, saw: {persona_lines}",
            )

        def test_recap_header_surfaces_recipe_axes_persona_intent(self) -> None:
            GPTState.last_response = "answer body"
            GPTState.last_recipe = "describe · gist"
            GPTState.last_completeness = "full"
            GPTState.last_scope = "focus"
            GPTState.last_method = "steps"
            GPTState.last_form = "bullets"
            GPTState.last_channel = "slack"

            persona_preset = PersonaPreset(
                key="teach_junior_dev",
                label="Teach junior dev",
                spoken="mentor",
                voice="as teacher",
                audience="to junior dev",
                tone="kindly",
            )
            persona_maps = SimpleNamespace(
                persona_presets={"teach_junior_dev": persona_preset},
                persona_preset_aliases={
                    "teach_junior_dev": "teach_junior_dev",
                    "mentor": "teach_junior_dev",
                    "teach junior dev": "teach_junior_dev",
                },
                intent_presets={
                    "decide": SimpleNamespace(
                        key="decide", label="Decide", intent="decide"
                    )
                },
                intent_preset_aliases={},
                intent_synonyms={},
                intent_display_map={"decide": "Decide"},
            )

            recipe_snapshot = {
                "recipe": "describe · full · focus · steps · bullets · slack",
                "static_prompt": "describe",
                "completeness": "full",
                "scope_tokens": ["focus"],
                "method_tokens": ["steps"],
                "form_tokens": ["bullets"],
                "channel_tokens": ["slack"],
                "directional": "fog",
                "persona_preset_key": "teach_junior_dev",
                "persona_preset_label": "",
                "persona_preset_spoken": "mentor",
                "persona_voice": "as teacher",
                "persona_audience": "to junior dev",
                "persona_tone": "kindly",
                "intent_preset_key": "decide",
                "intent_purpose": "decide",
                "intent_display": "",
            }

            captured = self._render_recap_lines(
                recipe_snapshot=recipe_snapshot,
                grammar_phrase="say describe fog",
                persona_maps=persona_maps,
            )

            header_lines = [
                line
                for line in captured
                if line
                in (
                    "Talon GPT Result",
                    "Prompt recap",
                    "Recipe: describe · full · focus · steps · bullets · slack · fog",
                    "Say: say describe fog",
                )
            ]
            self.assertEqual(
                header_lines,
                [
                    "Talon GPT Result",
                    "Prompt recap",
                    "Recipe: describe · full · focus · steps · bullets · slack · fog",
                    "Say: say describe fog",
                ],
            )

            persona_line = next(
                (line for line in captured if line.startswith("Persona:")), ""
            )
            self.assertIn("mentor", persona_line.lower())
            self.assertIn("teach_junior_dev", persona_line)

            intent_line = next(
                (line for line in captured if line.startswith("Intent:")), ""
            )
            self.assertIn("Decide", intent_line)
            self.assertIn("decide", intent_line.lower())

            axes_hint = [
                line for line in captured if "Axes: single directional lens" in line
            ]

            self.assertTrue(axes_hint, "Expected axes hint in recap header")

            # Reset GPTState overrides to avoid influencing later tests.
            GPTState.last_completeness = ""
            GPTState.last_scope = ""
            GPTState.last_method = ""
            GPTState.last_form = ""
            GPTState.last_channel = ""

        def test_persona_intent_maps_cached_across_draws(self) -> None:
            modelResponseCanvas.reset_persona_intent_maps_cache()
            recipe_snapshot = {
                "recipe": "describe · gist",
                "static_prompt": "describe",
                "form_tokens": [],
                "channel_tokens": [],
                "persona_preset_key": "teach_junior_dev",
                "persona_preset_label": "Teach junior dev",
                "persona_preset_spoken": "mentor",
                "persona_voice": "as teacher",
                "persona_audience": "to junior dev",
                "persona_tone": "kindly",
                "intent_preset_key": "decide",
                "intent_purpose": "decide",
                "intent_display": "Decide",
            }

            with patch.object(
                modelResponseCanvas,
                "persona_intent_maps",
                wraps=modelResponseCanvas.persona_intent_maps,
            ) as mock_maps:
                self._render_recap_lines(
                    recipe_snapshot=recipe_snapshot,
                    grammar_phrase="model run describe gist",
                )
                self._render_recap_lines(
                    recipe_snapshot=recipe_snapshot,
                    grammar_phrase="model run describe gist",
                )
            self.assertEqual(
                mock_maps.call_count,
                1,
                "Expected persona_intent_maps to be cached between draws",
            )

            modelResponseCanvas.reset_persona_intent_maps_cache()
            with patch.object(
                modelResponseCanvas,
                "persona_intent_maps",
                wraps=modelResponseCanvas.persona_intent_maps,
            ) as mock_maps_after_reset:
                self._render_recap_lines(
                    recipe_snapshot=recipe_snapshot,
                    grammar_phrase="model run describe gist",
                )
            self.assertEqual(
                mock_maps_after_reset.call_count,
                1,
                "Expected persona_intent_maps to be invoked after cache reset",
            )


else:
    if not TYPE_CHECKING:

        class ModelResponseCanvasTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
