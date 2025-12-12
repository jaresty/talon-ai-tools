from typing import Callable, Optional

from talon import Context, Module, actions, canvas, ui
from talon import skia

from .canvasFont import apply_canvas_typeface
from .helpUI import apply_scroll_delta, clamp_scroll
from .axisConfig import axis_docs_for
from .axisCatalog import axis_catalog
from .personaConfig import INTENT_PRESETS, PERSONA_PRESETS

from .modelState import GPTState
from .talonSettings import _AXIS_SOFT_CAPS

from .metaPromptConfig import first_meta_preview_line, meta_preview_lines

try:
    from .staticPromptConfig import (
        get_static_prompt_axes,
        static_prompt_settings_catalog,
    )
except ImportError:  # Talon may have a stale staticPromptConfig loaded
    from .staticPromptConfig import STATIC_PROMPT_CONFIG

    def get_static_prompt_axes(name: str) -> dict[str, object]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, object] = {}
        for axis in ("completeness", "scope", "method", "style"):
            value = profile.get(axis)
            if not value:
                continue
            if axis == "completeness":
                axes[axis] = str(value)
            else:
                if isinstance(value, list):
                    tokens = [str(v).strip() for v in value if str(v).strip()]
                else:
                    tokens = [str(value).strip()]
                if tokens:
                    axes[axis] = tokens
        return axes

    def static_prompt_settings_catalog():
        """Fallback settings catalog when static_prompt_settings_catalog is unavailable.

        This mirrors lib.staticPromptConfig.static_prompt_settings_catalog but
        builds entries directly from STATIC_PROMPT_CONFIG and get_static_prompt_axes
        so quick-help surfaces can still render static prompt details.
        """
        catalog: dict[str, dict[str, object]] = {}
        for name, profile in STATIC_PROMPT_CONFIG.items():
            catalog[name] = {
                "description": str(profile.get("description", "")).strip(),
                "axes": get_static_prompt_axes(name),
            }
        return catalog


def _axis_keys(axis: str) -> list[str]:
    """Return axis keys from the catalog SSOT, falling back to AxisDocs."""

    try:
        catalog = axis_catalog()
        axis_tokens = catalog.get("axes", {}).get(axis)
        if axis_tokens:
            return list(axis_tokens.keys())
    except Exception:
        pass

    docs = axis_docs_for(axis)
    return [doc.key for doc in docs]


def _persona_preset_commands() -> list[str]:
    """Return speakable persona preset commands in list order."""

    commands: list[str] = []
    for preset in PERSONA_PRESETS:
        # Only show explicit spoken forms; labels/keys are too verbose for quick help.
        spoken = (preset.spoken or "").strip().lower()
        if not spoken:
            continue
        commands.append(spoken)
    return commands


def _intent_preset_commands() -> list[str]:
    """Return speakable intent preset commands in list order."""

    commands: list[str] = []
    for preset in INTENT_PRESETS:
        spoken = (preset.key or "").strip().lower()
        if not spoken:
            continue
        commands.append(spoken)
    return commands


def _draw_wrapped_commands(
    prefix: str,
    commands: list[str],
    draw_text: Callable[[str, int, int], None],
    x: int,
    y: int,
    rect: Optional["Rect"],
    line_h: int,
    command_prefix: Optional[str] = None,
) -> int:
    """Render a prefixed command list, wrapping to multiple lines when needed."""

    if not commands:
        return y

    entries = list(commands)
    if command_prefix and entries:
        entries = [f"{command_prefix} {entries[0]}"] + entries[1:]

    approx_char_width = 8
    max_pixels = 320
    try:
        if rect is not None and hasattr(rect, "width"):
            padding = 0
            if hasattr(rect, "x"):
                padding = max(x - rect.x, 0)
            max_pixels = max(int(rect.width) - (2 * padding), 120)
    except Exception:
        # Fall back to the default max width if rect math fails.
        max_pixels = 320
    # Keep lines readable even on wide panels.
    max_pixels = min(max_pixels, 520)
    max_chars = max(int(max_pixels // approx_char_width), 10)

    lines: list[str] = []
    current = prefix + entries[0]
    for cmd in entries[1:]:
        candidate = current + " · " + cmd
        if len(candidate) > max_chars and current:
            lines.append(current)
            current = " " * len(prefix) + cmd
        else:
            current = candidate
    lines.append(current)

    for line in lines:
        draw_text(line, x, y)
        y += line_h
    return y


# Axis summaries (keys only; descriptions remain in docs). Pulled directly from
# the generated axis map so quick help follows the list files.
COMPLETENESS_KEYS = _axis_keys("completeness")
SCOPE_KEYS = _axis_keys("scope")
METHOD_KEYS = _axis_keys("method")
STYLE_KEYS = _axis_keys("style")


def _group_directional_keys() -> dict[str, list[str]]:
    """Arrange directional lenses into vertical/horizontal groups.

    The canvas layout uses this to build the directional XY map; the exact
    grouping logic is intentionally simple and mirrors the legacy imgui
    helper without depending on list files.
    """
    groups: dict[str, list[str]] = {
        "up": [],
        "center_v": [],
        "down": [],
        "left": [],
        "center_h": [],
        "right": [],
        "central": [],
        "non_directional": [],
        "fused_other": [],
    }
    vertical_up = {"fog"}
    vertical_center = {"fig"}
    vertical_down = {"dig"}
    horizontal_left = {"rog"}
    horizontal_center = {"bog"}
    horizontal_right = {"ong"}
    central_names = {"jog"}

    directional_keys = {"fog", "fig", "dig", "rog", "bog", "ong", "jog"}
    try:
        catalog = axis_catalog()
        catalog_keys = set((catalog.get("axes", {}).get("directional") or {}).keys())
        if catalog_keys:
            directional_keys |= catalog_keys
    except Exception:
        pass
    seen_directional: set[str] = set()

    for base in directional_keys:
        is_directional = False
        if base in vertical_up:
            groups["up"].append(base)
            is_directional = True
        if base in vertical_center:
            groups["center_v"].append(base)
            is_directional = True
        if base in vertical_down:
            groups["down"].append(base)
            is_directional = True

        if base in horizontal_left:
            groups["left"].append(base)
            is_directional = True
        if base in horizontal_center:
            groups["center_h"].append(base)
            is_directional = True
        if base in horizontal_right:
            groups["right"].append(base)
            is_directional = True

        if base in central_names:
            groups["central"].append(base)
            is_directional = True

        if is_directional:
            seen_directional.add(base)

    return groups


class HelpGUIState:
    """Shared quick-help state reused by canvas tests and legacy callers."""

    section: str = "all"
    static_prompt: Optional[str] = None
    showing: bool = False


mod = Module()
ctx = Context()

try:  # Talon runtime
    from talon.types import Rect
except Exception:  # Tests / stubs

    class Rect:  # type: ignore[override]
        def __init__(self, x: float, y: float, width: float, height: float):
            self.x = x
            self.y = y
            self.width = width
            self.height = height


class HelpCanvasState:
    """State specific to the canvas-based quick help view."""

    showing: bool = False
    scroll_y: float = 0.0


_help_canvas: Optional[canvas.Canvas] = None
_draw_handlers: list[Callable] = []
_drag_offset: Optional[tuple[float, float]] = None
_hover_close: bool = False
_hover_panel: bool = False

# Default geometry for the quick help window. Kept in one place so future
# tweaks do not require hunting for magic numbers.
_PANEL_WIDTH = 820
_PANEL_HEIGHT = 980
_PANEL_OFFSET_X = 200
_PANEL_OFFSET_Y = 80


def _debug(msg: str) -> None:
    """Lightweight debug logging for the canvas quick help.

    Logs to the Talon log via stdout. This is intentionally simple so users
    can copy/paste logs when diagnosing issues with `model quick help`.
    """
    try:
        print(f"GPT quick help canvas: {msg}")
    except Exception:
        # Printing should not be able to break the UI.
        pass


def _build_direction_grid() -> dict[tuple[str, str], list[str]]:
    """Compute a 3x3 directional grid from the shared grouping helper."""
    groups = _group_directional_keys()
    grid: dict[tuple[str, str], list[str]] = {
        ("up", "left"): [],
        ("up", "center"): [],
        ("up", "right"): [],
        ("center", "left"): [],
        ("center", "center"): [],
        ("center", "right"): [],
        ("down", "left"): [],
        ("down", "center"): [],
        ("down", "right"): [],
    }

    if not groups:
        return grid

    def _assign(token: str) -> None:
        row = "center"
        col = "center"
        if token in groups["up"]:
            row = "up"
        elif token in groups["down"]:
            row = "down"
        elif token in groups["center_v"]:
            row = "center"

        if token in groups["left"]:
            col = "left"
        elif token in groups["right"]:
            col = "right"
        elif token in groups["center_h"]:
            col = "center"

        if token in groups["central"]:
            row = "center"
            col = "center"

        grid[(row, col)].append(token)

    for key in _group_directional_keys().values():
        for token in key:
            _assign(token)

    return grid


def _ensure_canvas() -> canvas.Canvas:
    """Create the help canvas if needed and register draw handlers."""
    global _help_canvas
    if _help_canvas is not None:
        _debug("reusing existing canvas instance")
        return _help_canvas

    screen = ui.main_screen()
    # Prefer centering relative to the main screen while keeping geometry
    # bounded so the panel stays fully visible.
    # Width/height defaults live in module-level constants so they are easy
    # to tune without scattering magic numbers.
    try:
        screen_x = getattr(screen, "x", 0)
        screen_y = getattr(screen, "y", 0)
        screen_width = getattr(screen, "width", _PANEL_WIDTH + 80)
        screen_height = getattr(screen, "height", _PANEL_HEIGHT + 80)
        margin_x = 40
        margin_y = 40

        # Constrain panel size so it always fits within the screen margins.
        panel_width = min(_PANEL_WIDTH, max(screen_width - 2 * margin_x, 480))
        panel_height = min(_PANEL_HEIGHT, max(screen_height - 2 * margin_y, 480))

        start_x = screen_x + max((screen_width - panel_width) // 2, margin_x)
        start_y = screen_y + max((screen_height - panel_height) // 2, margin_y)
        rect = Rect(start_x, start_y, panel_width, panel_height)
        _debug(
            f"initial canvas rect=({start_x}, {start_y}, {panel_width}, {panel_height}) "
            f"screen=({getattr(screen, 'x', 0)}, {getattr(screen, 'y', 0)}, "
            f"{getattr(screen, 'width', 'n/a')}, {getattr(screen, 'height', 'n/a')})"
        )
        # Use a regular canvas rather than a Talon "panel" so the rect we
        # choose is respected on all platforms; dragging and mouse blocking
        # are handled explicitly below.
        _help_canvas = canvas.Canvas.from_rect(rect)
        try:
            _help_canvas.blocks_mouse = True
        except Exception:
            pass
        _debug("created new canvas instance from_rect")
    except Exception:
        _help_canvas = canvas.Canvas.from_screen(screen)
        _debug("created new canvas instance from_main_screen (fallback)")

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        # Delegate to registered handlers so tests can replace or extend
        # drawing behaviour without depending on Talon's canvas internals.
        for handler in list(_draw_handlers):
            try:
                handler(c)
            except Exception:
                # Drawing errors should not crash Talon; fail closed.
                continue

    _help_canvas.register("draw", _on_draw)
    _debug("registered draw handler on canvas")

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Minimal mouse handler to support close and drag affordances."""
        global _drag_offset, _hover_close, _hover_panel
        try:
            rect = getattr(_help_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type = getattr(evt, "event", "") or ""
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos

            # In Talon canvas events, `pos` is already local to the canvas.
            local_x = pos.x
            local_y = pos.y
            if local_y < 0 or local_x < 0:
                return

            header_height = 32
            hotspot_width = 80
            inside_panel = 0 <= local_x <= rect.width and 0 <= local_y <= rect.height

            # Track hover state for the close hotspot so the renderer can
            # provide visual feedback.
            if event_type in ("mousemove", "mouse_move"):
                _hover_close = (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                )
                _hover_panel = inside_panel

            # Close hotspot: primary-button press in the top-right corner.
            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("close click detected in canvas header")
                    _reset_help_state("all", None)
                    _close_canvas()
                    _drag_offset = None
                    return

                # Start drag anywhere else in the panel.
                _drag_offset = (gpos.x - rect.x, gpos.y - rect.y)
                _debug(f"drag start at offset {_drag_offset}")
                return

            # End drag on mouse up.
            if event_type in ("mouseup", "mouse_up"):
                if _drag_offset is not None:
                    _debug("drag end")
                _drag_offset = None
                _hover_panel = inside_panel
                return

            # Drag while moving with offset set.
            if event_type in ("mousemove", "mouse_move") and _drag_offset is not None:
                dx, dy = _drag_offset
                new_x = gpos.x - dx
                new_y = gpos.y - dy
                try:
                    # Use the canvas move API, as other Talon canvas UIs do, to
                    # keep dragging responsive and avoid unnecessary rect
                    # recreation on every frame.
                    _help_canvas.move(new_x, new_y)
                except Exception:
                    # If rect assignment fails for any reason, stop dragging.
                    _drag_offset = None
                return

            # Vertical scroll via mouse wheel when available.
            if event_type in ("mouse_scroll", "wheel", "scroll"):
                dy = getattr(evt, "dy", 0) or getattr(evt, "wheel_y", 0)
                try:
                    dy = float(dy)
                except Exception:
                    dy = 0.0
                if dy:
                    # Positive dy scrolls down (content up). Keep the bound
                    # conservative; the content is mostly text and fits well
                    # within a couple of thousand pixels.
                    new_scroll = HelpCanvasState.scroll_y - dy * 40.0
                    HelpCanvasState.scroll_y = clamp_scroll(new_scroll, 2000.0)
                return

        except Exception:
            # Mouse handling should never crash Talon; ignore errors.
            return

    try:
        _help_canvas.register("mouse", _on_mouse)
        _debug("registered mouse handler on canvas")
    except Exception:
        # Older Talon versions or the unittest stubs may not support mouse
        # registration; treat this as an optional enhancement.
        _debug("mouse handler registration failed; close hotspot disabled")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        """Key handler for quick help (Escape + basic scrolling)."""
        try:
            if not getattr(evt, "down", False):
                return
            key = (getattr(evt, "key", "") or "").lower()
            if key in ("escape", "esc"):
                _debug("escape key pressed; closing canvas quick help")
                _reset_help_state("all", None)
                _close_canvas()
                return

            # Provide simple keyboard scrolling so users can inspect tall
            # quick-help content without relying solely on the mouse.
            # Use coarse and fine increments similar to the response canvas.
            delta = 0.0
            if key in ("pagedown", "page_down"):
                delta = 200.0
            elif key in ("pageup", "page_up"):
                delta = -200.0
            elif key in ("down", "j"):
                delta = 40.0
            elif key in ("up", "k"):
                delta = -40.0
            if delta:
                new_scroll = HelpCanvasState.scroll_y + delta
                HelpCanvasState.scroll_y = clamp_scroll(new_scroll, 2000.0)
        except Exception:
            return

    try:
        _help_canvas.register("key", _on_key)
        _debug("registered key handler on canvas")
    except Exception:
        _debug("key handler registration failed; Escape close disabled")

    return _help_canvas


def register_draw_handler(handler: Callable) -> None:
    """Register a draw handler for the help canvas.

    This is primarily intended for tests and future slices that want to
    extend the visual layout without touching the canvas wiring.
    """
    _draw_handlers.append(handler)


def unregister_draw_handler(handler: Callable) -> None:
    """Remove a previously registered draw handler, if present."""
    try:
        _draw_handlers.remove(handler)
    except ValueError:
        pass


def _open_canvas() -> None:
    """Show the canvas-based quick help."""
    _debug(
        "_open_canvas called: showing=%s help_showing=%s"
        % (
            getattr(HelpCanvasState, "showing", False),
            getattr(HelpGUIState, "showing", False),
        )
    )
    canvas_obj = _ensure_canvas()
    if canvas_obj is None:
        _debug("_open_canvas: _ensure_canvas returned None; aborting show")
        return
    HelpCanvasState.showing = True
    HelpGUIState.showing = True
    HelpCanvasState.scroll_y = 0.0
    _debug("opening canvas quick help (calling show())")
    try:
        canvas_obj.show()
        _debug("canvas quick help: show() returned without raising")
    except Exception as e:
        _debug(f"canvas quick help: show() failed: {e}")

        _debug("canvas quick help: show() returned without raising")
    except Exception as e:
        _debug(f"canvas quick help: show() failed: {e}")


def _close_canvas() -> None:
    """Hide the canvas-based quick help."""
    global _help_canvas
    if _help_canvas is None:
        HelpCanvasState.showing = False
        HelpGUIState.showing = False
        return
    HelpCanvasState.showing = False
    HelpGUIState.showing = False
    HelpCanvasState.scroll_y = 0.0
    try:
        _debug("closing canvas quick help")
        _help_canvas.hide()
    except Exception:
        # In tests, the stub hide() is a no-op; in Talon, hide errors should
        # not propagate.
        pass


def _reset_help_state(
    section: str = "all", static_prompt: Optional[str] = None
) -> None:
    """Reset shared quick-help state to a known baseline."""
    HelpGUIState.section = section
    HelpGUIState.static_prompt = static_prompt


def _default_draw_quick_help(
    c: canvas.Canvas,
) -> None:  # pragma: no cover - visual only
    """Baseline canvas renderer for quick help.

    This implementation intentionally keeps canvas usage conservative so it
    remains robust across Talon versions and the unit-test stub:
    - If `c.paint` or `c.rect` are missing (as in tests), it exits quickly.
    - In a real Talon runtime, it renders a simple textual layout:
      title, grammar skeleton, axis summaries, and a directional grid
      summary derived from the shared helpers.
    """
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        _debug("canvas draw skipped (no draw_text on canvas object)")
        return

    # Set the shared canvas paint to an explicit colour so text is readable on
    # light panel backgrounds, following the same pattern talon_hud uses.
    paint = getattr(c, "paint", None)
    base_textsize = None
    if paint is not None:
        try:
            base_textsize = getattr(paint, "textsize", None)
        except Exception:
            base_textsize = None
        # Align quick-help canvas font with the shared GPT canvas font chain.
        apply_canvas_typeface(
            paint,
            settings_key="user.model_response_canvas_typeface",
            debug=_debug,
            cache_key="help",
        )

    # Fill the entire canvas rect with a solid background so the quick help
    # feels like an opaque modal rather than floating text, and add a subtle
    # outline so it reads as a coherent panel.
    rect = getattr(c, "rect", None)
    if rect is not None and paint is not None and hasattr(rect, "width"):
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            paint.color = "FFFFFF"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(rect)
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.STROKE
            paint.color = "C0C0C0"
            c.draw_rect(
                Rect(rect.x + 0.5, rect.y + 0.5, rect.width - 1, rect.height - 1)
            )
            # Restore style; text colour is set explicitly below.
            if old_style is not None:
                paint.style = old_style
            paint.color = old_color or "000000"
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    # Now ensure text uses a readable colour on top of the background.
    if paint is not None:
        try:
            paint.color = "000000"  # hex string (opaque black)
        except Exception:
            pass

    # Draw near the top-left of the canvas; apply a vertical scroll offset so
    # tall quick-help content can be inspected on smaller screens.
    scroll_y = getattr(HelpCanvasState, "scroll_y", 0.0) or 0.0
    if rect is not None and hasattr(rect, "x") and hasattr(rect, "y"):
        x = rect.x + 40
        y = rect.y + 60 - int(scroll_y)
    else:
        x = 40
        y = 60 - int(scroll_y)
    line_h = 18

    # Header band behind the title and close button so the top of the panel
    # feels like a natural title bar.
    if rect is not None and paint is not None and hasattr(rect, "width"):
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            header_height = 40
            paint.color = "F5F5F5"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            header_rect = Rect(rect.x + 4, rect.y + 4, rect.width - 8, header_height)
            c.draw_rect(header_rect)
            # Restore paint for text.
            paint.color = old_color or "000000"
            if old_style is not None:
                paint.style = old_style
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    # Title.
    title_old_size = None
    if paint is not None and isinstance(base_textsize, (int, float)):
        try:
            title_old_size = base_textsize
            paint.textsize = int(base_textsize * 1.2)
        except Exception:
            title_old_size = None
    draw_text("Model grammar quick reference (canvas)", x, y)
    # Draw a small close hint in the top-right header area to align with the
    # clickable close hotspot registered in `_ensure_canvas()`. When hovered,
    # slightly underline the label so it feels interactive.
    if (
        rect is not None
        and hasattr(rect, "width")
        and hasattr(rect, "x")
        and hasattr(rect, "y")
    ):
        close_label = "[X]"
        close_y = rect.y + 24
        # Align close label within the same horizontal band as the title.
        close_x = rect.x + rect.width - (len(close_label) * 8) - 16
        draw_text(close_label, close_x, close_y)
        if _hover_close:
            try:
                underline_rect = Rect(close_x, close_y + 4, len(close_label) * 8, 1)
                c.draw_rect(underline_rect)
            except Exception:
                pass
    # Restore title text size for body content.
    if paint is not None and title_old_size is not None:
        try:
            paint.textsize = title_old_size
        except Exception:
            pass

    # Spacer below the title; rely on hover/affordances rather than a long
    # textual hint for interaction.
    y += line_h * 2

    # Grammar skeleton and last-recipe reminder.
    draw_text("Grammar:", x, y)
    y += line_h
    draw_text(
        "  model run <staticPrompt> [completeness] [scope] [method] [style] <directional lens>",
        x,
        y,
    )
    y += line_h

    # Make multiplicity explicit so users know how many axis tokens are kept.
    scope_cap = _AXIS_SOFT_CAPS.get("scope", 2)
    method_cap = _AXIS_SOFT_CAPS.get("method", 3)
    style_cap = _AXIS_SOFT_CAPS.get("style", 3)
    caps_line = (
        f"  Caps: 1 static prompt · 1 completeness · scope≤{scope_cap} · "
        f"method≤{method_cap} · style≤{style_cap} · 1 directional lens"
    )
    draw_text(caps_line, x, y)
    y += line_h

    # Persona / Intent quick grammar and presets.
    draw_text("Who / Why (Persona / Intent):", x, y)
    y += line_h
    draw_text("  persona <personaPreset>", x, y)
    y += line_h
    draw_text("  intent <intentPreset>", x, y)
    y += line_h

    try:
        persona_commands = _persona_preset_commands()
        if persona_commands:
            y = _draw_wrapped_commands(
                "  Persona presets (Who): ",
                persona_commands,
                draw_text,
                x,
                y,
                rect,
                line_h,
                command_prefix="persona",
            )
    except Exception:
        # If persona presets cannot be imported, continue without them.
        pass

    try:
        intent_commands = _intent_preset_commands()
        if intent_commands:
            y = _draw_wrapped_commands(
                "  Intent presets (Why): ",
                intent_commands,
                draw_text,
                x,
                y,
                rect,
                line_h,
                command_prefix="intent",
            )
    except Exception:
        # If intent presets cannot be imported, continue without them.
        pass

    draw_text(
        "  Status/reset: persona status · persona reset · intent status · intent reset",
        x,
        y,
    )
    y += line_h

    section_focus = getattr(HelpGUIState, "section", "all") or "all"

    if HelpGUIState.static_prompt:
        sp = HelpGUIState.static_prompt
        draw_text(f"Static prompt focus: {sp}", x, y)
        y += line_h

        # When a static prompt is focused, render its description and axis
        # profile using the shared static prompt settings catalog so quick help
        # stays aligned with docs and Talon settings.
        try:
            settings_catalog = static_prompt_settings_catalog()
        except Exception:
            settings_catalog = {}
        entry = settings_catalog.get(sp) if settings_catalog else None
        if entry:
            description = str(entry.get("description") or "").strip()
            if description:
                draw_text(description, x, y)
                y += line_h
            axes = entry.get("axes") or {}
            if axes:
                draw_text("Profile axes:", x, y)
                y += line_h
                for axis in ("completeness", "scope", "method", "style"):
                    value = axes.get(axis)
                    if not value:
                        continue
                    if isinstance(value, list):
                        rendered = " ".join(str(v) for v in value)
                    else:
                        rendered = str(value)
                    if rendered:
                        draw_text(f"  {axis.capitalize()}: {rendered}", x, y)
                        y += line_h
            y += line_h
    elif GPTState.last_recipe:
        recipe = GPTState.last_recipe
        directional = getattr(GPTState, "last_directional", "")
        if recipe:
            # Show a recap line plus a speakable `model …` hint, mirroring the
            # behaviour of the imgui quick help.
            recap = recipe
            if directional:
                recap = f"{recipe} · {directional}"
            draw_text(f"Last recipe: {recap}", x, y)
            y += line_h

            speakable = f"model run {recipe.replace(' · ', ' ')}"
            if directional:
                speakable = f"{speakable} {directional}"
            draw_text(f"Say: {speakable}", x, y)
            y += line_h

    y += line_h

    # Draw a subtle border around the panel, with a slightly stronger
    # contrast when the mouse is hovering over the panel. This gives a
    # lightweight hover effect without relying on cursor changes.
    if rect is not None and paint is not None and hasattr(rect, "width"):
        try:
            old_color = getattr(paint, "color", None)
            border_color = "C0C0C0" if not _hover_panel else "808080"
            paint.color = border_color
            top = rect.y + 4
            left = rect.x + 4
            right = rect.x + rect.width - 4
            bottom = rect.y + rect.height - 4
            c.draw_line(left, top, right, top)
            c.draw_line(right, top, right, bottom)
            c.draw_line(right, bottom, left, bottom)
            c.draw_line(left, bottom, left, top)
            # Restore text colour for subsequent drawing.
            paint.color = old_color or "000000"
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    # Axis summaries (keys only; descriptions remain in docs).
    # Lay these out in two columns to keep the canvas from becoming overly tall.
    y_axes_top = y
    x_left = x
    # Default to a reasonable column separation; when rect is available, use half-width.
    if rect is not None and hasattr(rect, "width"):
        x_right = rect.x + rect.width // 2
    else:
        x_right = x + 360
    y_left = y_axes_top
    y_right = y_axes_top

    def _draw_axis_keys_wrapped(keys: list[str], col_x: int, col_y: int) -> int:
        """Render axis keys across multiple lines to avoid over-long rows.

        We use character-count based wrapping, approximating width so text
        stays within the canvas without depending on precise font metrics.
        """
        if not keys:
            return col_y

        # Approximate maximum character width based on the column width so the
        # two axis columns don't bleed into each other.
        approx_char_width = 8
        if rect is not None and hasattr(rect, "width"):
            # Reserve margin inside the column for breathing room.
            max_pixels = max((rect.width // 2) - 60, 120)
        else:
            max_pixels = 320
        max_chars = max(int(max_pixels // approx_char_width), 10)

        idx = 0
        while idx < len(keys):
            row: list[str] = []
            # Build up a row until adding another key would exceed max_chars.
            while idx < len(keys):
                candidate_key = keys[idx]
                candidate = ", ".join(row + [candidate_key]) if row else candidate_key
                line_text = "  " + candidate
                if len(line_text) > max_chars and row:
                    break
                row.append(candidate_key)
                idx += 1
                if len(line_text) >= max_chars:
                    break
            draw_text("  " + ", ".join(row), col_x, col_y)
            col_y += line_h

        return col_y

    def _draw_axis_column(
        label: str, axis_key: str, keys: list[str], col_x: int, col_y: int
    ) -> int:
        heading_old_size = None
        if paint is not None and isinstance(base_textsize, (int, float)):
            try:
                heading_old_size = getattr(paint, "textsize", None)
                if isinstance(heading_old_size, (int, float)):
                    paint.textsize = int(heading_old_size * 1.05)
            except Exception:
                heading_old_size = None
        if section_focus == axis_key:
            heading = f"{label} (focus)"
        else:
            heading = label
        draw_text(f"{heading}:", col_x, col_y)
        col_y += line_h
        if paint is not None and heading_old_size is not None:
            try:
                paint.textsize = heading_old_size
            except Exception:
                pass
        if keys:
            col_y = _draw_axis_keys_wrapped(keys, col_x, col_y)
        col_y += line_h // 2
        return col_y

    # Left column: completeness + scope
    y_left = _draw_axis_column(
        "Completeness", "completeness", COMPLETENESS_KEYS, x_left, y_left
    )
    y_left = _draw_axis_column("Scope", "scope", SCOPE_KEYS, x_left, y_left)

    # Right column: method + style
    y_right = _draw_axis_column("Method", "method", METHOD_KEYS, x_right, y_right)
    y_right = _draw_axis_column("Style", "style", STYLE_KEYS, x_right, y_right)

    # Brief axis multiplicity hint so users know which axes can be combined.
    # Draw this note below whichever column is taller and wrap it so it stays
    # within the visible canvas width.
    axes_bottom = max(y_left, y_right)
    note = (
        f"Note: completeness is single-valued. Scope≤{scope_cap}, method≤{method_cap}, "
        f"style≤{style_cap}; combine tags like actions edges or structure flow."
    )
    approx_char_width = 8
    if rect is not None and hasattr(rect, "x") and hasattr(rect, "width"):
        right_bound = rect.x + rect.width - 40
    else:
        right_bound = x_left + 480
    max_pixels = max(right_bound - x_left, 120)
    max_chars = max(int(max_pixels // approx_char_width), 20)

    words = note.split()
    line = ""
    note_y = axes_bottom
    for word in words:
        candidate = f"{line} {word}".strip()
        if len(candidate) > max_chars and line:
            draw_text(line, x_left, note_y)
            note_y += line_h
            line = word
        else:
            line = candidate
    if line:
        draw_text(line, x_left, note_y)
        note_y += line_h

    # Continue below the wrapped note.
    y = note_y + line_h

    # Draw a subtle separator between the axis block and the directional map
    # to make the section boundary easier to see.
    if rect is not None and hasattr(rect, "x") and hasattr(rect, "width"):
        try:
            sep_y = y - (line_h // 2)
            sep_rect = Rect(rect.x + 16, sep_y, rect.width - 32, 1)
            c.draw_rect(sep_rect)
        except Exception:
            # If drawing fails for any reason, continue without the separator.
            pass

    # Directional overview as a coarse grid summary.
    grid = _build_direction_grid()
    y += line_h
    if section_focus == "directional":
        draw_text("Directional lenses (focus, coordinate map)", x, y)
    else:
        draw_text("Directional lenses (coordinate map)", x, y)
    y += line_h
    # Brief semantic hints so the axes feel meaningful, not just symbolic.
    draw_text(
        "  Vertical: abstract (up) – generalise; concrete (down) – ground/specify.",
        x,
        y,
    )
    y += line_h
    draw_text(
        "  Horizontal: reflect (left) – analyse; act (right) – change/extend; center – mix/balance.",
        x,
        y,
    )
    y += line_h * 2

    def _fmt_cell(row: str, col: str) -> str:
        tokens = grid.get((row, col)) or []
        return ", ".join(tokens) if tokens else "-"

    def _fmt_base_cell(row: str, col: str) -> str:
        """Format only base (single-token) lenses for the main grid.

        Combined two-word lenses like 'fly rog' are omitted here and shown
        instead in the quadrant annotations so we avoid duplication.
        """
        tokens = [t for t in (grid.get((row, col)) or []) if " " not in t]
        return ", ".join(tokens)

    def _build_combined_lines(row: str) -> list[str]:
        """Build multi-line combined lens summary for a vertical row.

        Example:
          combined:
            reflect: fly rog
            mixed:   fly bog
            act:     fly ong
        """
        lines: list[str] = []
        segments: list[str] = []
        for col, label in (("left", "reflect"), ("center", "mixed"), ("right", "act")):
            raw = [t for t in (grid.get((row, col)) or []) if " " in t]
            if not raw:
                continue
            tokens = list(dict.fromkeys(raw))
            segments.append(f"{label}: {', '.join(tokens)}")
        if not segments:
            return lines
        lines.append("  combined:")
        for seg in segments:
            lines.append(f"    {seg}")
        return lines

    # Lay out the directional lenses as a cross-shaped XY map with five
    # labelled blocks: up/abstract, left/reflect, center/mixed, right/act,
    # down/concrete. This mirrors the mental model from ADR 016 and the
    # ASCII sketch used during design.
    if rect is not None and hasattr(rect, "x") and hasattr(rect, "width"):
        total_width = max(rect.width - 80, 300)
        block_width = max(min(total_width // 3, 260), 180)
        col_gap = 16
        center_x = rect.x + rect.width // 2 - block_width // 2
        left_x = center_x - block_width - col_gap
        right_x = center_x + block_width + col_gap
    else:
        block_width = 220
        left_x = x
        center_x = x + block_width + 24
        right_x = center_x + block_width + 24

    block_rects: dict[str, Rect] = {}

    def _draw_block(
        title: str,
        lines: list[str],
        box_x: int,
        box_y: int,
        box_width: int,
        bg_color: Optional[str],
        key: Optional[str],
    ) -> int:
        # Optional soft background tint to make each block feel like a
        # distinct region in the coordinate map.
        if rect is not None and paint is not None and bg_color:
            try:
                old_color = getattr(paint, "color", None)
                old_style = getattr(paint, "style", None)
                height = (1 + len(lines)) * line_h + (line_h // 2)
                pad_x = 8
                pad_y = line_h // 3
                paint.color = bg_color
                if hasattr(paint, "Style") and hasattr(paint, "style"):
                    paint.style = paint.Style.FILL
                bg_rect = Rect(
                    box_x - pad_x,
                    box_y - pad_y,
                    box_width + 2 * pad_x,
                    height + 2 * pad_y,
                )
                c.draw_rect(bg_rect)
                if key:
                    block_rects[key] = bg_rect
                paint.color = old_color or "000000"
                if old_style is not None:
                    paint.style = old_style
            except Exception:
                try:
                    paint.color = "000000"
                except Exception:
                    pass

        draw_text(title, box_x, box_y)
        # Slightly larger heading for the block title.
        heading_old_size = None
        if paint is not None and isinstance(base_textsize, (int, float)):
            try:
                heading_old_size = getattr(paint, "textsize", None)
                if isinstance(heading_old_size, (int, float)):
                    paint.textsize = int(heading_old_size * 1.05)
            except Exception:
                heading_old_size = None
        box_y += line_h
        if paint is not None and heading_old_size is not None:
            try:
                paint.textsize = heading_old_size
            except Exception:
                pass
        for line in lines:
            draw_text(line, box_x, box_y)
            box_y += line_h
        return box_y

    y_grid_top = y

    # Top: UP / ABSTRACT
    up_lines: list[str] = []
    val = _fmt_base_cell("up", "left")
    if val:
        up_lines.append(f"  reflect: {val}")
    val = _fmt_base_cell("up", "center")
    if val:
        up_lines.append(f"  center:  {val}")
    val = _fmt_base_cell("up", "right")
    if val:
        up_lines.append(f"  act:     {val}")
    up_lines.extend(_build_combined_lines("up"))

    top_end_y = _draw_block(
        "UP / ABSTRACT",
        up_lines,
        center_x,
        y_grid_top,
        block_width,
        "FFF9E5",
        "up",
    )

    # Center column: CENTER / MIXED
    # Focus this block on the true central lenses so tokens like `fog` and
    # `dig` stay anchored to their UP/DOWN blocks instead of being relabelled
    # here as "abstract"/"concrete" again.
    center_start_y = top_end_y + (line_h // 2)
    center_lines: list[str] = []
    val = _fmt_base_cell("center", "center")
    if val:
        center_lines.append(f"  center: {val}")

    center_end_y = _draw_block(
        "CENTER / MIXED",
        center_lines,
        center_x,
        center_start_y,
        block_width,
        "F5F5F5",
        "center",
    )

    # Left: LEFT / REFLECT
    left_lines: list[str] = []
    val = _fmt_base_cell("up", "left")
    if val:
        left_lines.append(f"  abstract: {val}")
    val = _fmt_base_cell("center", "left")
    if val:
        left_lines.append(f"  center:   {val}")
    val = _fmt_base_cell("down", "left")
    if val:
        left_lines.append(f"  concrete: {val}")
    # Light hint that vertical movement for this stance comes from fly/dip.
    if any(
        " " in t
        for t in (grid.get(("up", "left"), []) or [])
        + (grid.get(("down", "left"), []) or [])
    ):
        left_lines.append("  vertical: via fly/dip")

    left_end_y = _draw_block(
        "LEFT / REFLECT",
        left_lines,
        left_x,
        center_start_y,
        block_width,
        "EEF5FF",
        "left",
    )

    # Right: RIGHT / ACT
    right_lines: list[str] = []
    val = _fmt_base_cell("up", "right")
    if val:
        right_lines.append(f"  abstract: {val}")
    val = _fmt_base_cell("center", "right")
    if val:
        right_lines.append(f"  center:   {val}")
    val = _fmt_base_cell("down", "right")
    if val:
        right_lines.append(f"  concrete: {val}")
    if any(
        " " in t
        for t in (grid.get(("up", "right"), []) or [])
        + (grid.get(("down", "right"), []) or [])
    ):
        right_lines.append("  vertical: via fly/dip")

    right_end_y = _draw_block(
        "RIGHT / ACT",
        right_lines,
        right_x,
        center_start_y,
        block_width,
        "E9F8EC",
        "right",
    )

    # Bottom: DOWN / CONCRETE
    bottom_start_y = center_end_y + (line_h // 2)
    down_lines: list[str] = []
    val = _fmt_base_cell("down", "left")
    if val:
        down_lines.append(f"  reflect: {val}")
    val = _fmt_base_cell("down", "center")
    if val:
        down_lines.append(f"  center:  {val}")
    val = _fmt_base_cell("down", "right")
    if val:
        down_lines.append(f"  act:     {val}")
    down_lines.extend(_build_combined_lines("down"))

    bottom_end_y = _draw_block(
        "DOWN / CONCRETE",
        down_lines,
        center_x,
        bottom_start_y,
        block_width,
        "FFF0F5",
        "down",
    )

    y = max(left_end_y, right_end_y, bottom_end_y) + line_h

    # Short caption to reinforce usage without adding heavy text blocks.
    draw_text(
        "  One lens per call. fly/fip/dip move up/center/down; rog/bog/ong set reflect/mixed/act.",
        x,
        y,
    )
    y += line_h

    # Optional examples section, shown only when explicitly focused to avoid
    # making the default quick help view too tall (mirrors imgui semantics).
    if section_focus == "examples":
        y += line_h
        draw_text("Examples", x, y)
        y += line_h
        draw_text("  Debug bug: describe · full · narrow · debugging · rog", x, y)
        y += line_h
        draw_text("  Fix locally: fix · full · narrow · steps · ong", x, y)
        y += line_h
        draw_text("  Summarize gist: describe · gist · focus · plain · fog", x, y)
        y += line_h
        draw_text("  Sketch diagram: describe · gist · focus · diagram · fog", x, y)
        y += line_h
        draw_text("  Architecture decision: describe · full · focus · adr · rog", x, y)
        y += line_h
        draw_text("  Present slides: describe · full · focus · presenterm · rog", x, y)
        y += line_h
        draw_text("  Format for Slack: describe · gist · focus · slack · fog", x, y)
        y += line_h
        draw_text("  Format for Jira: describe · gist · focus · jira · fog", x, y)
        y += line_h
        draw_text("  Systems sketch: describe · gist · focus · systemic · fog", x, y)
        y += line_h
        draw_text(
            "  Experiment plan: describe · full · focus · experimental · fog", x, y
        )
        y += line_h
        draw_text("  Type/taxonomy: describe · full · focus · taxonomy · rog", x, y)
        y += line_h
        draw_text("  Analysis only: describe · gist · focus · analysis · fog", x, y)
        y += line_h
        draw_text("  Sample options: describe · samples · focus · diverge · fog", x, y)
        y += line_h * 2
        draw_text("Replaced prompts", x, y)
        y += line_h
        draw_text(
            "  simple → use describe · gist · plain (or the 'Simplify locally' pattern).",
            x,
            y,
        )
        y += line_h
        draw_text(
            "  short → use describe · gist · tight (or the 'Tighten summary' pattern).",
            x,
            y,
        )
        y += line_h
        draw_text(
            "  todo-style 'how to' → use todo · gist · checklist (or the 'Extract todos' pattern).",
            x,
            y,
        )


# Register the default quick help renderer so the canvas has a baseline view
# even if no custom handlers are attached.
register_draw_handler(_default_draw_quick_help)


@mod.action_class
class UserActions:
    def model_help_canvas_open():
        """Toggle the canvas-based model grammar quick reference"""
        if HelpCanvasState.showing:
            _reset_help_state("all", None)
            _close_canvas()
            return

        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass

        _reset_help_state("all", None)
        _open_canvas()

    def model_help_canvas_close():
        """Explicitly close the canvas-based quick help and reset state"""
        _reset_help_state("all", None)
        _close_canvas()

    def model_help_canvas_open_for_last_recipe():
        """Open canvas quick help focused on the last recipe"""
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass

        # Match the legacy imgui semantics: reset back to the generic "all"
        # section and clear any static prompt focus when opening for the last
        # recipe.
        _reset_help_state("all", None)
        _open_canvas()

    def model_help_canvas_open_for_static_prompt(static_prompt: str):
        """Open canvas quick help focused on a specific static prompt"""
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass

        _reset_help_state("all", static_prompt)
        _open_canvas()

    def model_help_canvas_open_completeness():
        """Open canvas quick help focused on completeness"""
        _reset_help_state("completeness", None)
        _open_canvas()

    def model_help_canvas_open_scope():
        """Open canvas quick help focused on scope"""
        _reset_help_state("scope", None)
        _open_canvas()

    def model_help_canvas_open_method():
        """Open canvas quick help focused on method"""
        _reset_help_state("method", None)
        _open_canvas()

    def model_help_canvas_open_style():
        """Open canvas quick help focused on style"""
        _reset_help_state("style", None)
        _open_canvas()

    def model_help_canvas_open_directional():
        """Open canvas quick help focused on directional lenses"""
        _reset_help_state("directional", None)
        _open_canvas()

    def model_help_canvas_open_examples():
        """Open canvas quick help focused on examples"""
        _reset_help_state("examples", None)
        _open_canvas()

    def model_help_canvas_open_who():
        """Open canvas quick help focused on persona (Who)"""
        _reset_help_state("who", None)
        _open_canvas()

    def model_help_canvas_open_why():
        """Open canvas quick help focused on intent (Why)"""
        _reset_help_state("why", None)
        _open_canvas()

    def model_help_canvas_open_how():
        """Open canvas quick help focused on contract (How)"""
        _reset_help_state("how", None)
        _open_canvas()
