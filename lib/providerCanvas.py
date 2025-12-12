from talon import Context, Module, canvas, skia, ui

from .canvasFont import apply_canvas_typeface

mod = Module()
ctx = Context()


class ProviderCanvasState:
    showing: bool = False
    title: str = "Providers"
    lines: list[str] = []


_canvas = None


def _ensure_canvas():
    global _canvas
    if _canvas is None:
        _canvas = canvas.Canvas.from_screen(ui.main_screen())
        _canvas.register("draw", _on_draw)
    return _canvas


def _on_draw(c):
    if not ProviderCanvasState.lines:
        return
    paint = skia.Paint()
    paint.color = 0xFFFFFFFF
    apply_canvas_typeface(paint)
    x = 40
    y = 60
    if ProviderCanvasState.title:
        paint_text = ProviderCanvasState.title
        c.draw_text(paint_text, x, y, paint=paint)
        y += 28
    for line in ProviderCanvasState.lines:
        c.draw_text(line, x, y, paint=paint)
        y += 22


def show_provider_canvas(title: str, lines: list[str]) -> None:
    ProviderCanvasState.title = title
    ProviderCanvasState.lines = lines
    c = _ensure_canvas()
    ProviderCanvasState.showing = True
    c.show()


def hide_provider_canvas() -> None:
    global _canvas
    ProviderCanvasState.showing = False
    ProviderCanvasState.lines = []
    if _canvas is not None:
        _canvas.hide()


@mod.action_class
class UserActions:
    def model_provider_canvas_show(title: str, lines: list[str]):
        """Show the provider canvas with the given lines."""

        show_provider_canvas(title, list(lines))

    def model_provider_canvas_close():
        """Hide the provider canvas."""

        hide_provider_canvas()
