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

