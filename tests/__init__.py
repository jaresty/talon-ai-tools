"""Test package bootstrap to emulate Talon's module layout."""

import pathlib
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
STUBS = pathlib.Path(__file__).resolve().parent / "stubs"

# Ensure repository and stub paths are importable first
for path in (STUBS, ROOT):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)


def _ensure_namespace(pkg: str, location: pathlib.Path) -> None:
    if pkg in sys.modules:
        return
    module = types.ModuleType(pkg)
    module.__path__ = [str(location)]  # type: ignore[attr-defined]
    sys.modules[pkg] = module


# Mirror Talon's package naming (arbitrary namespace for tests)
_ensure_namespace("talon_user", ROOT)
_ensure_namespace("talon_user.lib", ROOT / "lib")
_ensure_namespace("talon_user.GPT", ROOT / "GPT")

# Provide alias so modules expecting `talon_user.lib` style can be imported
sys.modules.setdefault("talon_user.Images", types.ModuleType("talon_user.Images"))
sys.modules["talon_user.Images"].__path__ = [str(ROOT / "Images")]  # type: ignore[attr-defined]

