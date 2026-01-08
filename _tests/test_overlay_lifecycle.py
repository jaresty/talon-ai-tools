import unittest
from types import SimpleNamespace
from typing import TYPE_CHECKING
from unittest.mock import patch

from unittest.mock import patch

if not TYPE_CHECKING:

    class OverlayLifecycleTests(unittest.TestCase):
        def test_close_overlays_invokes_closers_and_ignores_failures(self) -> None:
            from talon_user.lib.overlayLifecycle import close_overlays

            calls = []

            def ok():
                calls.append("ok")

            def boom():
                calls.append("boom")
                raise RuntimeError("fail")

            close_overlays([ok, boom, None, ok])
            self.assertEqual(calls, ["ok", "boom", "ok"])

        def test_close_common_overlays_calls_present_closers(self) -> None:
            from talon_user.lib.overlayLifecycle import (
                COMMON_OVERLAY_CLOSERS,
                close_common_overlays,
            )

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def prompt_pattern_gui_close(self):
                    calls.append("prompt")

                def model_prompt_recipe_suggestions_gui_close(self):
                    calls.append("suggestions")

                def model_help_canvas_close(self):
                    calls.append("help")

                def model_response_canvas_close(self):
                    calls.append("response")

                def confirmation_gui_close(self):
                    calls.append("confirmation")

            self.assertIn("confirmation_gui_close", COMMON_OVERLAY_CLOSERS)
            self.assertIn("model_response_canvas_close", COMMON_OVERLAY_CLOSERS)
            close_common_overlays(Actions())
            self.assertEqual(
                calls,
                [
                    "pattern",
                    "prompt",
                    "suggestions",
                    "help",
                    "response",
                    "confirmation",
                ],
            )

        def test_close_common_overlays_noop_when_missing_attrs(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            class Actions:
                pass

            # Should not raise even when none of the closers exist.
            close_common_overlays(Actions())

        def test_close_common_overlays_respects_exclude(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def model_response_canvas_close(self):
                    calls.append("response")

            close_common_overlays(Actions(), exclude={"model_response_canvas_close"})
            self.assertEqual(calls, ["pattern"])

        def test_close_common_overlays_noop_on_none_actions(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            # Should safely no-op when actions_obj is None.
            close_common_overlays(None)

        def test_common_overlay_closers_are_unique(self) -> None:
            from talon_user.lib.overlayLifecycle import COMMON_OVERLAY_CLOSERS

            self.assertEqual(
                len(COMMON_OVERLAY_CLOSERS), len(set(COMMON_OVERLAY_CLOSERS))
            )

        def test_close_common_overlays_ignores_non_callables(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                model_response_canvas_close = "not a function"

                def model_pattern_gui_close(self):
                    calls.append("pattern")

            close_common_overlays(Actions())
            self.assertEqual(calls, ["pattern"])

        def test_close_common_overlays_calls_extra_when_present(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def extra_close(self):
                    calls.append("extra")

            close_common_overlays(Actions(), extra=["extra_close"])
            self.assertEqual(calls, ["pattern", "extra"])

        def test_close_common_overlays_exclude_applies_to_extra(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def extra_close(self):
                    calls.append("extra")

            close_common_overlays(
                Actions(), exclude={"extra_close"}, extra=["extra_close"]
            )
            self.assertEqual(calls, [])

        def test_close_common_overlays_dedupes_names(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                # Duplicate name should not lead to double call when passed via extra.
                def model_response_canvas_close(self):
                    calls.append("response")

            close_common_overlays(
                Actions(),
                extra=["model_pattern_gui_close", "model_response_canvas_close"],
            )
            self.assertEqual(calls, ["pattern", "response"])

        def test_close_common_overlays_ignores_noncallable_extra(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                extra_close = "not callable"

                def model_pattern_gui_close(self):
                    calls.append("pattern")

            close_common_overlays(Actions(), extra=["extra_close"])
            self.assertEqual(calls, ["pattern"])

        def test_close_common_overlays_respects_exclude_for_base_closers(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def model_response_canvas_close(self):
                    calls.append("response")

            close_common_overlays(Actions(), exclude={"model_response_canvas_close"})
            self.assertEqual(calls, ["pattern"])

        def test_close_common_overlays_respects_declared_order(self) -> None:
            from talon_user.lib.overlayLifecycle import (
                COMMON_OVERLAY_CLOSERS,
                close_common_overlays,
            )

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def prompt_pattern_gui_close(self):
                    calls.append("prompt")

                def model_prompt_recipe_suggestions_gui_close(self):
                    calls.append("suggestions")

                def model_help_canvas_close(self):
                    calls.append("help")

                def model_response_canvas_close(self):
                    calls.append("response")

                def confirmation_gui_close(self):
                    calls.append("confirmation")

            close_common_overlays(Actions())
            expected = [
                "pattern",
                "prompt",
                "suggestions",
                "help",
                "response",
                "confirmation",
            ]
            # Ensure the constant matches the expected ordering.
            self.assertEqual(
                list(COMMON_OVERLAY_CLOSERS),
                [
                    "model_pattern_gui_close",
                    "prompt_pattern_gui_close",
                    "model_prompt_recipe_suggestions_gui_close",
                    "model_help_canvas_close",
                    "model_response_canvas_close",
                    "confirmation_gui_close",
                ],
            )
            self.assertEqual(calls, expected)

        def test_close_common_overlays_ignores_unlisted_callables(self) -> None:
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            class Actions:
                def model_pattern_gui_close(self):
                    calls.append("pattern")

                def not_in_common_set(self):
                    calls.append("extra")

            close_common_overlays(Actions())
            self.assertEqual(calls, ["pattern"])

        def test_common_overlay_closers_do_not_call_gating(self) -> None:
            from talon_user.lib import (
                modelHelpCanvas,
                modelPatternGUI,
                modelPromptPatternGUI,
                modelSuggestionGUI,
            )
            from talon_user.lib.overlayLifecycle import close_common_overlays

            calls = []

            with (
                patch("talon_user.lib.surfaceGuidance.try_begin_request") as try_begin,
                patch.object(
                    modelHelpCanvas,
                    "_close_canvas",
                    side_effect=lambda: self.assertTrue(
                        getattr(
                            modelHelpCanvas.GPTState,
                            "suppress_overlay_inflight_guard",
                            False,
                        )
                    ),
                ),
                patch.object(modelHelpCanvas, "_reset_help_state"),
                patch.object(
                    modelPatternGUI,
                    "_close_pattern_canvas",
                    side_effect=lambda: self.assertTrue(
                        getattr(
                            modelPatternGUI.GPTState,
                            "suppress_overlay_inflight_guard",
                            False,
                        )
                    ),
                ),
                patch.object(modelPatternGUI, "ctx", SimpleNamespace(tags=[])),
                patch.object(
                    modelPromptPatternGUI,
                    "_close_prompt_pattern_canvas",
                    side_effect=lambda: self.assertTrue(
                        getattr(
                            modelPromptPatternGUI.GPTState,
                            "suppress_overlay_inflight_guard",
                            False,
                        )
                    ),
                ),
                patch.object(modelPromptPatternGUI, "ctx", SimpleNamespace(tags=[])),
                patch.object(
                    modelSuggestionGUI,
                    "_close_suggestion_canvas",
                    side_effect=lambda: calls.append("suggestion_close"),
                ),
                patch.object(modelSuggestionGUI, "ctx", SimpleNamespace(tags=[])),
            ):
                actions_stub = SimpleNamespace(
                    model_pattern_gui_close=modelPatternGUI.UserActions.model_pattern_gui_close,
                    prompt_pattern_gui_close=modelPromptPatternGUI.UserActions.prompt_pattern_gui_close,
                    model_prompt_recipe_suggestions_gui_close=modelSuggestionGUI.UserActions.model_prompt_recipe_suggestions_gui_close,
                    model_help_canvas_close=modelHelpCanvas.UserActions.model_help_canvas_close,
                    model_response_canvas_close=lambda: calls.append("response_close"),
                    confirmation_gui_close=lambda: calls.append("confirmation_close"),
                )
                close_common_overlays(actions_stub, passive=True)

            try_begin.assert_not_called()
            self.assertIn("suggestion_close", calls)
