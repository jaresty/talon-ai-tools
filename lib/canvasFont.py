from typing import Callable, Optional

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


def _try_set_typeface(paint, family: str) -> bool:
    """Best-effort typeface selection for a canvas paint object.

    Attempts to use Skia helpers when available, then falls back to assigning
    the family name directly. Returns True when a typeface was applied.
    """
    if not family or paint is None:
        return False

    sk = skia
    if sk is not None:
        try:
            typeface = None
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
            if typeface is not None:
                paint.typeface = typeface
                return True
        except Exception:
            # Fall through to the simpler string-based assignment below.
            pass

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

    if override_family:
        candidate_families = [str(override_family)]
    else:
        candidate_families = families

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
    if len(runs) <= 1:
        draw_text(text, x, y)
        return

    try:
        original_typeface = getattr(paint, "typeface", None)
    except Exception:
        original_typeface = None

    families = emoji_families or DEFAULT_EMOJI_FAMILIES
    cursor_x = x

    for is_emoji, segment in runs:
        if not segment:
            continue

        if is_emoji and families:
            # Try the configured emoji families; if all fail we still draw
            # with the existing typeface so content is visible.
            applied = False
            for family in families:
                if _try_set_typeface(paint, family):
                    applied = True
                    break
            if not applied and original_typeface is not None:
                try:
                    paint.typeface = original_typeface
                except Exception:
                    pass
        else:
            # Restore the original typeface for non-emoji spans.
            if original_typeface is not None:
                try:
                    paint.typeface = original_typeface
                except Exception:
                    pass

        try:
            draw_text(segment, cursor_x, y)
        except Exception:
            # As a last resort, try drawing the full text once.
            try:
                draw_text(text, x, y)
            except Exception:
                pass
            return

        cursor_x += approx_char_width * len(segment)

    # Restore original typeface at the end.
    if original_typeface is not None:
        try:
            paint.typeface = original_typeface
        except Exception:
            pass

