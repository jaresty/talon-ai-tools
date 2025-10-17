import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime importing tests; ignore
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import clip
    from talon_user.lib.modelDestination import AppendClipboard, Clipboard
    from talon_user.lib.modelTypes import GPTTextItem

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
else:
    class ModelDestinationClipboardTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
