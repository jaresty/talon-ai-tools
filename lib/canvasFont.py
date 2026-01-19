from dataclasses import dataclass, asdict
import threading
from typing import Callable, Optional, Dict, List, Tuple
from weakref import WeakKeyDictionary

from talon import settings

try:  # Talon runtime; some builds expose additional Skia APIs.
    from talon import skia  # type: ignore[import]
except Exception:  # pragma: no cover - defensive guard for older runtimes
    skia = None  # type: ignore[assignment]


_SELECTED_TYPEFACE: dict[str, str] = {}

# Default font preference chain for canvas-based UIs. The goal is to use a
# readable monospaced font when available, while still falling back to a
# system font with broad glyph coverage (including emoji) on platforms that
# support it.
DEFAULT_CANVAS_FAMILIES: list[str] = [
    "MonaspiceXe Nerd Font Mono",
    "Monaspace Xenon",
    "Menlo",
    # As a last resort, try the platform emoji font so arrow/symbol glyphs
    # are more likely to render, even if text metrics differ.
    "Apple Color Emoji",
]

# Preferred emoji-specific fallback families to try when drawing emoji runs.
DEFAULT_EMOJI_FAMILIES: list[str] = [
    # macOS colour emoji.
    "Apple Color Emoji",
    # Windows emoji.
    "Segoe UI Emoji",
    # Common Linux emoji font.
    "Noto Color Emoji",
]


_TYPEFACE_CACHE: Dict[str, object] = {}
_TYPEFACE_SENTINEL = object()


@dataclass
class _CanvasFontStats:
    typeface_cache_hits: int = 0
    typeface_cache_misses: int = 0
    emoji_plan_hits: int = 0
    emoji_plan_misses: int = 0
    segments_drawn: int = 0
    emoji_segments_drawn: int = 0


_STATS_LOCK = threading.Lock()
_STATS = _CanvasFontStats()


@dataclass
class _EmojiCacheEntry:
    key: Tuple[str, Tuple[str, ...], float, int]
    segments: List[Tuple[object | None, str]]
    original_typeface: object | None


_EMOJI_SEGMENT_CACHE: "WeakKeyDictionary[object, _EmojiCacheEntry]" = (
    WeakKeyDictionary()
)


def _reset_stats() -> None:
    global _STATS
    with _STATS_LOCK:
        _STATS = _CanvasFontStats()


def _stats_increment(field: str, value: int = 1) -> None:
    if value == 0:
        return
    with _STATS_LOCK:
        setattr(_STATS, field, getattr(_STATS, field) + value)


def canvas_font_stats(*, reset: bool = False) -> Dict[str, int]:
    global _STATS
    with _STATS_LOCK:
        snapshot = asdict(_STATS)
        if reset:
            _STATS = _CanvasFontStats()
    return snapshot


def reset_canvas_font_caches() -> None:
    """Clear cached Skia typefaces and emoji render plans (primarily for tests)."""

    _TYPEFACE_CACHE.clear()
    _EMOJI_SEGMENT_CACHE.clear()
    _reset_stats()


def _resolve_typeface(family: str):
    cached = _TYPEFACE_CACHE.get(family, _TYPEFACE_SENTINEL)
    if cached is not _TYPEFACE_SENTINEL:
        _stats_increment("typeface_cache_hits")
        return cached

    typeface = None
    sk = skia
    if sk is not None:
        try:
            FontMgr = getattr(sk, "FontMgr", None)
            FontStyle = getattr(sk, "FontStyle", None)
            if FontMgr is not None and FontStyle is not None:
                try:
                    mgr = FontMgr.RefDefault()
                    style = FontStyle()
                    typeface = mgr.matchFamilyStyle(family, style)
                except Exception:
                    typeface = None
            if typeface is None:
                TypefaceCtor = getattr(sk, "Typeface", None)
                if TypefaceCtor is not None:
                    try:
                        typeface = TypefaceCtor(family)
                    except Exception:
                        typeface = None
        except Exception:
            typeface = None

    if typeface is None:
        typeface = family
    _TYPEFACE_CACHE[family] = typeface
    _stats_increment("typeface_cache_misses")
    return typeface


def _apply_typeface_value(paint, value) -> bool:
    if paint is None:
        return False
    if value is None:
        try:
            paint.typeface = None
            return True
        except Exception:
            try:
                delattr(paint, "typeface")
                return True
            except Exception:
                return False
    try:
        paint.typeface = value
        return True
    except Exception:
        if isinstance(value, str):
            try:
                paint.typeface = value
                return True
            except Exception:
                return False
        return False


def _try_set_typeface(paint, family: str) -> bool:
    """Best-effort typeface selection for a canvas paint object."""
    if not family or paint is None:
        return False

    typeface_value = _resolve_typeface(family)
    if _apply_typeface_value(paint, typeface_value):
        return True

    # Fallback: attempt plain family assignment when cached object failed.
    if isinstance(typeface_value, str):
        return _apply_typeface_value(paint, typeface_value)
    try:
        paint.typeface = family
        return True
    except Exception:
        return False


def apply_canvas_typeface(
    paint,
    *,
    settings_key: str = "user.model_response_canvas_typeface",
    families: Optional[list[str]] = None,
    debug: Optional[Callable[[str], None]] = None,
    cache_key: Optional[str] = None,
) -> None:
    """Apply a best-effort typeface to the given canvas paint.

    - Respects a Talon `settings_key` override when present.
    - Otherwise walks `families` (or `DEFAULT_CANVAS_FAMILIES`) in order and
      stops at the first name that can be applied.
    - Optionally logs the chosen family via `debug` when it changes.
    """
    if paint is None:
        return

    try:
        override_family = settings.get(settings_key, "") or ""
    except Exception:
        override_family = ""

    if families is None:
        families = DEFAULT_CANVAS_FAMILIES

    # Treat an override as the first candidate in the family list rather than
    # a hard replacement so we still fall back to emoji-capable defaults (for
    # example, Apple Color Emoji) when the preferred monospace font lacks
    # glyphs for some codepoints.
    candidate_families: list[str] = []
    if override_family:
        candidate_families.append(str(override_family))
    candidate_families.extend(families)

    selected: Optional[str] = None
    for fam in candidate_families:
        if not fam:
            continue
        if _try_set_typeface(paint, fam):
            selected = fam
            break

    if not selected or not debug or cache_key is None:
        return

    previous = _SELECTED_TYPEFACE.get(cache_key)
    if previous != selected:
        _SELECTED_TYPEFACE[cache_key] = selected
        debug(f"{cache_key} canvas typeface set to '{selected}'")


def _is_emoji_scalar(cp: int) -> bool:
    """Return True when the codepoint is likely part of an emoji sequence.

    This deliberately focuses on common emoji blocks plus VS16 / ZWJ so that
    joined sequences stay in a single run. It avoids pulling in the entire
    emoji-data set while still catching the vast majority of emoji used in
    model responses.
    """
    # Basic symbol/emoji ranges.
    if 0x1F300 <= cp <= 0x1FAFF:
        return True
    if 0x2600 <= cp <= 0x27BF:
        return True
    # Regional indicator symbols (flags).
    if 0x1F1E6 <= cp <= 0x1F1FF:
        return True
    # Variation selector-16 and zero-width joiner – keep them with emoji runs.
    if cp in (0xFE0F, 0x200D):
        return True
    return False


def _split_emoji_runs(text: str) -> list[tuple[bool, str]]:
    """Split text into `(is_emoji_run, segment)` tuples.

    The goal is to keep most emoji clusters (including ZWJ/VS16) in a single
    run so we can swap in an emoji-capable typeface just for those spans.
    """
    if not text:
        return []

    runs: list[tuple[bool, str]] = []
    current: list[str] = []
    current_is_emoji = _is_emoji_scalar(ord(text[0]))

    for ch in text:
        is_emoji = _is_emoji_scalar(ord(ch))
        if not current:
            current.append(ch)
            current_is_emoji = is_emoji
            continue
        if is_emoji == current_is_emoji:
            current.append(ch)
        else:
            runs.append((current_is_emoji, "".join(current)))
            current = [ch]
            current_is_emoji = is_emoji

    if current:
        runs.append((current_is_emoji, "".join(current)))

    return runs


def draw_text_with_emoji_fallback(
    canvas_obj,
    text: str,
    x: float,
    y: float,
    *,
    approx_char_width: float = 8.0,
    emoji_families: Optional[list[str]] = None,
    debug: Optional[Callable[[str], None]] = None,
) -> None:
    """Draw text, using an emoji-capable typeface for emoji runs when possible.

    This helper avoids relying on Skia Font/FontMgr APIs that are not exposed
    in all Talon runtimes. It works by:
    - Splitting the text into emoji/non-emoji runs.
    - Temporarily switching `canvas.paint.typeface` to an emoji family for
      emoji runs (and restoring afterwards).
    - Advancing `x` using a fixed `approx_char_width` so layout remains
      consistent with existing monospace assumptions.
    """
    if not text:
        return

    draw_text = getattr(canvas_obj, "draw_text", None)
    paint = getattr(canvas_obj, "paint", None)

    # If we cannot draw or adjust typefaces, fall back to a single draw call.
    if draw_text is None:
        return
    if paint is None:
        draw_text(text, x, y)
        return

    runs = _split_emoji_runs(text)
    if not runs:
        _stats_increment("segments_drawn")
        draw_text(text, x, y)
        return

    if len(runs) <= 1:
        _stats_increment("segments_drawn")
        if runs and runs[0][0]:
            _stats_increment("emoji_segments_drawn")
        draw_text(text, x, y)
        return

    try:
        original_typeface = getattr(paint, "typeface", None)
    except Exception:
        original_typeface = None

    families_list = [
        str(fam) for fam in (emoji_families or DEFAULT_EMOJI_FAMILIES) if fam
    ]
    try:
        approx_width = float(approx_char_width)
    except Exception:
        approx_width = 8.0
    if approx_width <= 0:
        approx_width = 8.0

    families_tuple = tuple(families_list)
    cache_key = (text, families_tuple, approx_width, id(original_typeface))

    cache_entry = None
    if paint is not None:
        existing = _EMOJI_SEGMENT_CACHE.get(paint)
        if existing is not None and existing.key == cache_key:
            cache_entry = existing
            _stats_increment("emoji_plan_hits")

    def _describe_typeface() -> str:
        if paint is None:
            return "paint=None"
        try:
            tf = getattr(paint, "typeface", None)
        except Exception:
            return "typeface=<unavailable>"
        if tf is None:
            return "typeface=None"
        name = None
        try:
            get_family = getattr(tf, "getFamilyName", None)
            if callable(get_family):
                name = get_family()
            else:
                name = getattr(tf, "familyName", None)
        except Exception:
            name = None
        ident = f"id={id(tf)}"
        if isinstance(tf, str):
            return f"typeface=str:{tf!r} {ident}"
        if name:
            return f"typeface=skia:{name!r} {ident}"
        try:
            tf_repr = repr(tf)
        except Exception:
            tf_repr = "<repr-unavailable>"
        return f"typeface={type(tf).__name__!s} {ident} repr={tf_repr!r}"

    if debug is not None:
        try:
            debug(
                f"emoji_draw text={text!r} runs="
                + "|".join(("E:" if is_e else "T:") + seg for (is_e, seg) in runs)
            )
            debug(f"emoji_draw initial {_describe_typeface()}")
        except Exception:
            pass

    if cache_entry is None:
        segments: List[Tuple[object | None, str]] = []
        for is_emoji, segment in runs:
            if not segment:
                continue
            if is_emoji and families_list:
                resolved_value = None
                for family in families_list:
                    resolved_value = _resolve_typeface(family)
                    if debug is not None:
                        try:
                            debug(
                                f"emoji_draw resolved family={family!r} for segment={segment!r}"
                            )
                        except Exception:
                            pass
                    if resolved_value is not None:
                        break
                segments.append((resolved_value, segment))
            else:
                segments.append((None, segment))
        cache_entry = _EmojiCacheEntry(cache_key, segments, original_typeface)
        _stats_increment("emoji_plan_misses")
        if paint is not None:
            _EMOJI_SEGMENT_CACHE[paint] = cache_entry

    segments = cache_entry.segments
    cached_original = cache_entry.original_typeface
    cursor_x = x

    for typeface_value, segment in segments:
        if not segment:
            continue

        _stats_increment("segments_drawn")

        if typeface_value is None:
            if cached_original is not None:
                _apply_typeface_value(paint, cached_original)
        else:
            _stats_increment("emoji_segments_drawn")
            _apply_typeface_value(paint, typeface_value)
            if debug is not None:
                try:
                    debug(
                        f"emoji_draw using cached typeface for segment={segment!r} -> {_describe_typeface()}"
                    )
                except Exception:
                    pass
        try:
            draw_text(segment, cursor_x, y)
        except Exception:
            try:
                draw_text(text, x, y)
            except Exception:
                pass
            return
        cursor_x += approx_width * len(segment)

    if cached_original is not None:
        _apply_typeface_value(paint, cached_original)
