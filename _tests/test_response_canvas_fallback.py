import unittest

from talon_user.lib.responseCanvasFallback import (
    append_response_fallback,
    clear_all_fallbacks,
    clear_response_fallback,
    fallback_for,
)


class ResponseCanvasFallbackTests(unittest.TestCase):
    def setUp(self):
        clear_all_fallbacks()

    def test_append_and_clear(self):
        append_response_fallback("rid-1", "hi")
        append_response_fallback("rid-1", " there")
        self.assertEqual(fallback_for("rid-1"), "hi there")
        clear_response_fallback("rid-1")
        self.assertEqual(fallback_for("rid-1"), "")

    def test_append_caps_length(self):
        append_response_fallback("rid-2", "a" * 5000)
        append_response_fallback("rid-2", "b" * 4000)
        text = fallback_for("rid-2")
        self.assertEqual(len(text), 8000)
        self.assertTrue(text.startswith("a" * 1000))
        self.assertTrue(text.endswith("b" * 4000))

    def test_clear_all(self):
        append_response_fallback("rid-1", "hi")
        append_response_fallback("rid-2", "there")
        clear_all_fallbacks()
        self.assertEqual(fallback_for("rid-1"), "")
        self.assertEqual(fallback_for("rid-2"), "")


if __name__ == "__main__":
    unittest.main()
