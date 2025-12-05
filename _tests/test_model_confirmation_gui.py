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
    from talon_user.lib.modelState import GPTState

    class ConfirmationGUIMetaTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()

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

else:
    if not TYPE_CHECKING:
        class ConfirmationGUIMetaTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
