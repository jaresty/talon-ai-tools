"""Lightweight Talon stubs for running unit tests outside the Talon runtime."""

from types import SimpleNamespace


class Context:
    def __init__(self):
        self.tags: list[str] = []


class Module:
    def tag(self, *_, **__):
        return None

    def list(self, *_, **__):
        return None

    def setting(self, name, *_, default=None, **__):
        key = f"user.{name}"
        settings._register_default(key, default)
        return None

    def capture(self, *_, **__):
        def decorator(func):
            return func

        return decorator

    def action_class(self, cls=None):  # pragma: no cover - simple passthrough
        if cls is None:
            def decorator(target):
                return target

            return decorator
        return cls


class _ActionRecorder:
    def __init__(self):
        self.calls: list[tuple[str, tuple, dict]] = []

    def __getattr__(self, item):
        def _noop(*args, **kwargs):
            self.calls.append((item, args, kwargs))
            if item == "language":
                return ""
            return None

        return _noop


class _UserActions(_ActionRecorder):
    def __init__(self):
        super().__init__()
        self.pasted: list[str] = []

    def paste(self, text):
        self.calls.append(("paste", (text,), {}))
        self.pasted.append(text)
        clip.set_text(text)


class _AppActions(_ActionRecorder):
    def notify(self, *_args, **_kwargs):
        self.calls.append(("notify", _args, _kwargs))
        return None


class _EditActions(_ActionRecorder):
    pass


class _CodeActions(_ActionRecorder):
    def language(self):
        self.calls.append(("language", tuple(), {}))
        return ""


class _Actions(SimpleNamespace):
    def __init__(self):
        super().__init__(
            user=_UserActions(),
            app=_AppActions(),
            edit=_EditActions(),
            code=_CodeActions(),
        )


actions = _Actions()
cron = SimpleNamespace(after=lambda _, fn: fn())


class _Clip:
    def __init__(self):
        self._text: str | None = None

    def text(self):
        return self._text

    def set_text(self, value):
        self._text = value

    def image(self):  # pragma: no cover - default to no clipboard image
        return None


clip = _Clip()


class _Settings:
    def __init__(self):
        self._values: dict[str, object] = {}

    def _register_default(self, key: str, value):
        if key not in self._values and value is not None:
            self._values[key] = value

    def get(self, key: str, default=None):
        if key == "user.model_streaming":
            return 1
        return self._values.get(key, default)

    def set(self, key: str, value):
        self._values[key] = value


settings = _Settings()


class _UIElement:
    def __init__(self, x=0, y=0, width=1920, height=1080):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get(self, _name):
        return None


class _UI:
    # Minimal subset needed for tests; real Talon exposes main_screen().
    Rect = _UIElement

    def main_screen(self):
        return _UIElement()

    def focused_element(self):
        return _UIElement()


ui = _UI()


class _Canvas:
    """Minimal canvas stub for tests.

    Provides just enough of the `canvas.Canvas` API used in this repo to
    allow unit tests to exercise open/close wiring without a real Talon
    runtime or drawing surface.
    """

    def __init__(self, _screen=None):
        self._callbacks: dict[str, list] = {}
        self.visible: bool = False
        self.rect = None
        self.blocks_mouse = False

    @classmethod
    def from_screen(cls, screen, **_kwargs):
        # The screen object is ignored in tests; real Talon will supply a
        # proper screen with geometry.
        return cls(screen)

    @classmethod
    def from_rect(cls, rect, **_kwargs):
        # In tests, treat from_rect the same as from_screen and ignore rect.
        obj = cls(rect)
        obj.rect = rect
        return obj

    def register(self, event: str, callback):
        self._callbacks.setdefault(event, []).append(callback)

    def unregister(self, event: str, callback):
        callbacks = self._callbacks.get(event)
        if not callbacks:
            return
        try:
            callbacks.remove(callback)
        except ValueError:
            pass

    def show(self):
        self.visible = True
        # Optionally invoke draw callbacks once so they are smoke-tested.
        for cb in self._callbacks.get("draw", []):
            cb(self)

    def hide(self):
        self.visible = False

    # Minimal drawing/movement primitives used by response and suggestion canvases.
    def draw_text(self, *_args, **_kwargs):
        return None

    def draw_rect(self, *_args, **_kwargs):
        return None

    def move(self, x: float, y: float):
        if self.rect is not None:
            try:
                self.rect.x = x
                self.rect.y = y
            except Exception:
                pass


canvas = SimpleNamespace(Canvas=_Canvas)


class _Tap:
    """Minimal tap stub that records registrations."""

    KEY = 1
    HOOK = 2

    def __init__(self):
        self.registrations: list[tuple[int, object]] = []

    def register(self, event_mask: int, handler):
        self.registrations.append((event_mask, handler))

    def unregister(self, event_mask: int, handler):
        try:
            self.registrations.remove((event_mask, handler))
        except ValueError:
            pass


tap = _Tap()


class _SkiaPaint:
    def __init__(self):
        self.color = 0


class _SkiaRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class _SkiaModule(SimpleNamespace):
    def __init__(self):
        super().__init__(Paint=_SkiaPaint, Rect=_SkiaRect)


skia = _SkiaModule()


class _DummyGUI:
    def text(self, *_args, **_kwargs):
        return None

    def line(self):
        return None

    def spacer(self):
        return None

    def button(self, *_args, **_kwargs):
        return False


class _ImguiFunction:
    def __init__(self, func):
        self._func = func
        self.showing = False

    def __call__(self, *args, **kwargs):
        return self._func(_DummyGUI(), *args, **kwargs)

    def show(self, *args, **kwargs):
        self.showing = True
        return self(*args, **kwargs)

    def hide(self):
        self.showing = False


def open():
    def decorator(func):
        wrapper = _ImguiFunction(func)
        # Expose the underlying function so tests can call it directly
        # with a custom GUI stub when needed.
        setattr(wrapper, "__wrapped__", func)
        return wrapper

    return decorator


imgui = SimpleNamespace(open=open, GUI=_DummyGUI)


class _AppNamespace(SimpleNamespace):
    def __init__(self):
        super().__init__()
        self.calls: list[tuple[str, tuple, dict]] = []

    def notify(self, message: str, *args, **kwargs):
        self.calls.append(("notify", (message, *args), kwargs))
        return None


app = _AppNamespace()


__all__ = [
    "actions",
    "app",
    "clip",
    "Context",
    "imgui",
    "Module",
    "settings",
    "ui",
    "canvas",
    "skia",
    "tap",
]
