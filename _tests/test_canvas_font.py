import unittest
from typing import Any, List, cast

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

SKIP_TESTS = bootstrap is None

if not SKIP_TESTS:
    from talon import skia as _real_skia
    from talon_user.lib import canvasFont as canvas_font_module

    skia = cast(Any, _real_skia)
    _split_emoji_runs = canvas_font_module._split_emoji_runs
else:  # pragma: no cover - executed only outside harness
    skia = cast(Any, None)
    canvas_font_module = cast(Any, None)
    _split_emoji_runs = cast(Any, None)


class CanvasFontEmojiSplitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SKIP_TESTS:
            raise unittest.SkipTest("Test harness unavailable outside unittest runs")

    def test_split_emoji_runs_mixed_text(self) -> None:
        runs = _split_emoji_runs("Hello 😀 world 🌍!")
        parts = [segment for _is_emoji, segment in runs]
        self.assertEqual("".join(parts), "Hello 😀 world 🌍!")
        self.assertTrue(any(is_emoji for is_emoji, _segment in runs))

    def test_split_emoji_runs_empty_string(self) -> None:
        self.assertEqual(_split_emoji_runs(""), [])


class CanvasFontCachingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SKIP_TESTS:
            raise unittest.SkipTest("Test harness unavailable outside unittest runs")
        cls._skia = skia
        cls._canvas_font = canvas_font_module
        cls._reset_caches = getattr(cls._canvas_font, "reset_canvas_font_caches", None)

    def setUp(self) -> None:
        self._skia.reset_stats()
        reset_fn = getattr(self.__class__, "_reset_caches", None)
        if callable(reset_fn):
            reset_fn()
        self._skia.stats.typeface_creations = 0
        self._skia.stats.match_calls = 0

    def test_apply_canvas_typeface_reuses_cached_typefaces(self) -> None:
        paint = self._skia.Paint()
        font_families: List[str] = ["Test Mono"]

        self._canvas_font.apply_canvas_typeface(
            paint,
            families=font_families,
            debug=None,
            cache_key="test",
        )
        first_creations = self._skia.stats.typeface_creations

        self._canvas_font.apply_canvas_typeface(
            paint,
            families=font_families,
            debug=None,
            cache_key="test",
        )

        self.assertEqual(
            self._skia.stats.typeface_creations,
            first_creations,
            msg="apply_canvas_typeface should reuse cached Skia typefaces",
        )

    def test_draw_text_with_emoji_fallback_caches_segments(self) -> None:
        class _DummyCanvas:
            def __init__(self, paint_obj, sink):
                self.paint = paint_obj
                self._sink = sink

            def draw_text(self, segment: str, *_args, **_kwargs):
                self._sink(segment)

        draw_calls: List[str] = []
        paint = self._skia.Paint()
        dummy_canvas = _DummyCanvas(paint, lambda segment: draw_calls.append(segment))

        text = "emoji 😀 text"
        families = ["Emoji Font"]

        self._canvas_font.draw_text_with_emoji_fallback(
            dummy_canvas,
            text,
            x=0,
            y=0,
            approx_char_width=8.0,
            emoji_families=families,
        )
        first_creations = self._skia.stats.typeface_creations

        self._canvas_font.draw_text_with_emoji_fallback(
            dummy_canvas,
            text,
            x=0,
            y=0,
            approx_char_width=8.0,
            emoji_families=families,
        )

        self.assertEqual(
            self._skia.stats.typeface_creations,
            first_creations,
            msg="draw_text_with_emoji_fallback should reuse cached emoji typefaces",
        )
        self.assertGreaterEqual(len(draw_calls), 2)
