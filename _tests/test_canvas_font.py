import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.canvasFont import _split_emoji_runs

    class CanvasFontEmojiSplitTests(unittest.TestCase):
        def test_split_emoji_runs_mixed_text(self) -> None:
            runs = _split_emoji_runs("Hello 😀 world 🌍!")
            # Expect something like: ["Hello ", "😀", " world ", "🌍", "!"]
            parts = [segment for _is_emoji, segment in runs]
            self.assertEqual("".join(parts), "Hello 😀 world 🌍!")
            # Ensure at least one emoji run was detected.
            self.assertTrue(any(is_emoji for is_emoji, _segment in runs))

        def test_split_emoji_runs_empty_string(self) -> None:
            self.assertEqual(_split_emoji_runs(""), [])

else:
    class CanvasFontEmojiSplitTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self) -> None:
            pass

