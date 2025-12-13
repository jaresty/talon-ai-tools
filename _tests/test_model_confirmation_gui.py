import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelConfirmationGUI import confirmation_gui
    from talon_user.lib.modelConfirmationGUI import (
        UserActions as ConfirmationActions,
    )
    from talon_user.lib.modelState import GPTState
    from talon import actions

    class ConfirmationGUIMetaTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()
            actions.user.calls.clear()

        def test_includes_meta_preview_when_last_meta_present(self) -> None:
            GPTState.text_to_confirm = "Body"
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_meta = "Interpreted as: summarise the design tradeoffs."

            rendered_lines: list[str] = []

            # Call the underlying imgui function with a stub GUI so we can
            # capture the rendered text lines.
            gui_fn = confirmation_gui.__wrapped__  # type: ignore[attr-defined]

            class _StubGUI:
                def text(self, value: str) -> None:
                    rendered_lines.append(value)

                def line(self) -> None:
                    pass

                def spacer(self) -> None:
                    pass

                def button(self, *_args, **_kwargs) -> bool:
                    return False

            gui_fn(_StubGUI())  # type: ignore[arg-type]

            self.assertTrue(
                any(line.startswith("Recipe: ") for line in rendered_lines),
                "Expected a Recipe line in the confirmation GUI output",
            )
            self.assertTrue(
                any(line.strip() == "Meta:" for line in rendered_lines),
                "Expected a Meta header line in the confirmation GUI output",
            )

        def test_meta_preview_skips_markdown_heading(self) -> None:
            # When meta starts with a markdown heading, the preview should use
            # the first non-heading line rather than the raw heading text.
            GPTState.text_to_confirm = "Body"
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_meta = "## Model interpretation\nInterpreted as: summarise the design tradeoffs."

            rendered_lines: list[str] = []

            gui_fn = confirmation_gui.__wrapped__  # type: ignore[attr-defined]

            class _StubGUI:
                def text(self, value: str) -> None:
                    rendered_lines.append(value)

                def line(self) -> None:
                    pass

                def spacer(self) -> None:
                    pass

                def button(self, *_args, **_kwargs) -> bool:
                    return False

            gui_fn(_StubGUI())  # type: ignore[arg-type]

            self.assertTrue(
                any(line.strip() == "Meta:" for line in rendered_lines),
                "Expected a Meta header line",
            )
            meta_body_lines = [
                line for line in rendered_lines if line.strip() != "Meta:"
            ]
            # The preview should not be the raw heading text.
            self.assertFalse(
                any("## Model interpretation" in line for line in meta_body_lines),
                "Meta preview should skip markdown headings",
            )
            self.assertTrue(
                any("Interpreted as:" in line for line in meta_body_lines),
                "Meta preview should use the first non-heading meta line",
            )

        def test_help_hub_button_triggers_action(self) -> None:
            GPTState.text_to_confirm = "Body"
            GPTState.last_recipe = "describe"

            gui_fn = confirmation_gui.__wrapped__  # type: ignore[attr-defined]

            class _StubGUI:
                def text(self, value: str) -> None:
                    pass

                def line(self) -> None:
                    pass

                def spacer(self) -> None:
                    pass

                def button(self, label: str, *_args, **_kwargs) -> bool:
                    # Simulate clicking More actions and then Open Help Hub.
                    return label in ("More actions…", "Open Help Hub")

            gui_fn(_StubGUI())  # type: ignore[arg-type]

            labels = [call[0] for call in actions.user.calls]
            self.assertIn("help_hub_open", labels)

        def test_confirmation_recap_includes_migration_hints(self) -> None:
            """Confirmation recap should remind users of form/channel singletons and directional requirement."""
            GPTState.text_to_confirm = "Body"
            GPTState.last_recipe = "describe · gist · focus · plain"
            GPTState.last_directional = "fog"

            rendered_lines: list[str] = []

            gui_fn = confirmation_gui.__wrapped__  # type: ignore[attr-defined]

            class _StubGUI:
                def text(self, value: str) -> None:
                    rendered_lines.append(value)

                def line(self) -> None:
                    pass

                def spacer(self) -> None:
                    pass

                def button(self, *_args, **_kwargs) -> bool:
                    return False

            gui_fn(_StubGUI())  # type: ignore[arg-type]

            self.assertTrue(
                any("Form/channel are single-value" in line for line in rendered_lines),
                f"Expected form/channel migration hint in confirmation recap, got {rendered_lines}",
            )
            self.assertTrue(
                any("directional lens" in line for line in rendered_lines),
                f"Expected directional migration hint in confirmation recap, got {rendered_lines}",
            )

        def test_save_to_file_button_triggers_action(self) -> None:
            GPTState.text_to_confirm = "Body"
            GPTState.last_recipe = "describe"

            gui_fn = confirmation_gui.__wrapped__  # type: ignore[attr-defined]

            class _StubGUI:
                def text(self, value: str) -> None:
                    pass

                def line(self) -> None:
                    pass

                def spacer(self) -> None:
                    pass

                def button(self, label: str, *_args, **_kwargs) -> bool:
                    # Simulate clicking More actions and then Save to file.
                    return label in ("More actions…", "Save to file")

            gui_fn(_StubGUI())  # type: ignore[arg-type]

            labels = [call[0] for call in actions.user.calls]
            self.assertIn("confirmation_gui_save_to_file", labels)

        def test_confirmation_close_dismisses_response_canvas(self) -> None:
            GPTState.text_to_confirm = "Body"
            actions.user.calls.clear()

            ConfirmationActions.confirmation_gui_close()

            labels = [call[0] for call in actions.user.calls]
            self.assertIn("model_response_canvas_close", labels)

        def test_paste_invokes_canvas_close_before_paste(self) -> None:
            GPTState.text_to_confirm = "Paste me"
            actions.user.calls.clear()
            actions.user.pasted.clear()

            orig_close = actions.user.confirmation_gui_close
            orig_canvas_close = getattr(
                actions.user, "model_response_canvas_close", None
            )

            def _record_canvas_close():
                actions.user.calls.append(("model_response_canvas_close", tuple(), {}))

            try:
                actions.user.confirmation_gui_close = (
                    ConfirmationActions.confirmation_gui_close
                )  # type: ignore[attr-defined]
                actions.user.model_response_canvas_close = _record_canvas_close  # type: ignore[attr-defined]
                ConfirmationActions.confirmation_gui_paste()
            finally:
                actions.user.confirmation_gui_close = orig_close  # type: ignore[attr-defined]
                if orig_canvas_close is not None:
                    actions.user.model_response_canvas_close = orig_canvas_close  # type: ignore[attr-defined]
                elif hasattr(actions.user, "model_response_canvas_close"):
                    delattr(actions.user, "model_response_canvas_close")

            labels = [call[0] for call in actions.user.calls]
            self.assertIn("model_response_canvas_close", labels)
            self.assertIn("paste", labels)
            self.assertLess(
                labels.index("model_response_canvas_close"),
                labels.index("paste"),
            )
            self.assertEqual(actions.user.pasted[-1], "Paste me")

else:
    if not TYPE_CHECKING:

        class ConfirmationGUIMetaTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
