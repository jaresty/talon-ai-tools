import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime importing tests; ignore
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.pureHelpers import strip_markdown

    class StripMarkdownTests(unittest.TestCase):
        def test_removes_code_block_fence_language(self):
            markdown = """\n```python\nprint('hello')\n```\n"""
            self.assertEqual(strip_markdown(markdown), "print('hello')")

        def test_defaults_to_plain_text_when_no_code_block(self):
            text = "plain text"
            self.assertEqual(strip_markdown(text), "plain text")
else:
    class StripMarkdownTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()
