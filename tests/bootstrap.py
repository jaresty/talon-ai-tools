"""Utilities to emulate Talon's import layout for unit tests."""

from __future__ import annotations

import pathlib
import sys
import types
from typing import Iterable


def _prepend_sys_path(paths: Iterable[pathlib.Path]) -> None:
    for path in paths:
        str_path = str(path)
        if str_path not in sys.path:
            sys.path.insert(0, str_path)


def _ensure_namespace(name: str, location: pathlib.Path) -> None:
    if name in sys.modules:
        module = sys.modules[name]
        if getattr(module, "__path__", None) is None:
            module.__path__ = [str(location)]  # type: ignore[attr-defined]
        return
    module = types.ModuleType(name)
    module.__path__ = [str(location)]  # type: ignore[attr-defined]
    sys.modules[name] = module


def bootstrap() -> None:
    """Configure sys.path and namespace packages for tests."""
    root = pathlib.Path(__file__).resolve().parents[1]
    stubs = pathlib.Path(__file__).resolve().parent / "stubs"

    _prepend_sys_path([stubs, root])

    _ensure_namespace("talon_user", root)
    _ensure_namespace("talon_user.lib", root / "lib")
    _ensure_namespace("talon_user.GPT", root / "GPT")
    _ensure_namespace("talon_user.Images", root / "Images")

