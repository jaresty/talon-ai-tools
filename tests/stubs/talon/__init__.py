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
        return self._values.get(key, default)

    def set(self, key: str, value):
        self._values[key] = value


settings = _Settings()


class _UIElement:
    def get(self, _name):
        return None


class _UI:
    def focused_element(self):
        return _UIElement()


ui = _UI()


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
        return _ImguiFunction(func)

    return decorator


imgui = SimpleNamespace(open=open, GUI=_DummyGUI)


class _AppNamespace(SimpleNamespace):
    def notify(self, *_args, **_kwargs):
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
]
