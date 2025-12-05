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

            # Confirm both the recipe recap and meta preview are present.
            self.assertTrue(
                any(line.startswith("Recipe: ") for line in rendered_lines),
                "Expected a Recipe line in the confirmation GUI output",
            )
            self.assertTrue(
                any(line.startswith("Meta: ") for line in rendered_lines),
                "Expected a Meta preview line in the confirmation GUI output",
            )

else:
    if not TYPE_CHECKING:
        class ConfirmationGUIMetaTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

