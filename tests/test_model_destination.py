import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime importing tests; ignore
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import clip
    from talon_user.lib.modelDestination import AppendClipboard, Clipboard
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon_user.lib.modelTypes import GPTTextItem
    from talon_user.lib import modelDestination as destination_module

    class ModelDestinationClipboardTests(unittest.TestCase):
        def setUp(self) -> None:
            clip.set_text(None)

        def test_clipboard_destination_replaces_text(self):
            dest = Clipboard()
            message: GPTTextItem = {"type": "text", "text": "hello world"}

            dest.insert([message])

            self.assertEqual(clip.text(), "hello world")

        def test_append_clipboard_destination_appends_with_newline(self):
            clip.set_text("existing")
            dest = AppendClipboard()
            message: GPTTextItem = {"type": "text", "text": "more"}

            dest.insert([message])

            self.assertEqual(clip.text(), "existing\nmore")

        def test_default_destination_uses_response_renderer(self):
            message: GPTTextItem = {"type": "text", "text": "hello"}
            destination_module.confirmation_gui.showing = True

            with patch.object(destination_module, "render_for_destination") as renderer, patch.object(
                destination_module.actions.user, "paste"
            ) as paste:
                renderer.return_value = ResponsePresentation(
                    display_text="hello", paste_text="hello", open_browser=False
                )

                destination_module.Default().insert([message])

                renderer.assert_called_once()
                paste.assert_called_once_with("hello")
            destination_module.confirmation_gui.showing = False

        def test_default_destination_appends_to_confirmation_gui(self):
            message: GPTTextItem = {"type": "text", "text": "hello"}

            with patch.object(
                destination_module, "render_for_destination"
            ) as renderer, patch.object(
                destination_module.actions.user, "confirmation_gui_append"
            ) as append:
                renderer.return_value = ResponsePresentation(
                    display_text="hello", paste_text="hello"
                )

                destination_module.Default().insert([message])

                renderer.assert_called_once()
                append.assert_called_once()
else:
    class ModelDestinationClipboardTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
