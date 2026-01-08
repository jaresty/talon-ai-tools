from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Sequence

DEFAULT_OUTPUT = Path("build/prompt-grammar.json")
_PROMPT_GRAMMAR_MODULE: ModuleType | None = None


def _ensure_namespace(name: str, location: Path) -> None:
    module = sys.modules.get(name)
    if module is None:
        module = ModuleType(name)
        sys.modules[name] = module
    paths = getattr(module, "__path__", None)
    location_str = str(location)
    if paths is None:
        module.__path__ = [location_str]  # type: ignore[attr-defined]
    elif location_str not in paths:
        paths.append(location_str)


def _bootstrap_prompt_namespace() -> None:
    root = Path(__file__).resolve().parents[1]
    stubs = root / "_tests" / "stubs"
    if stubs.exists():
        stubs_str = str(stubs)
        if stubs_str not in sys.path:
            sys.path.insert(0, stubs_str)
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    _ensure_namespace("talon_user", root)
    _ensure_namespace("talon_user.lib", root / "lib")
    _ensure_namespace("talon_user.GPT", root / "GPT")
    _ensure_namespace("talon_user.Images", root / "Images")


def _prompt_grammar_module() -> ModuleType:
    global _PROMPT_GRAMMAR_MODULE
    if _PROMPT_GRAMMAR_MODULE is not None:
        return _PROMPT_GRAMMAR_MODULE
    try:
        from talon_user.lib import promptGrammar as module  # type: ignore[import]
    except ModuleNotFoundError:
        _bootstrap_prompt_namespace()
        from talon_user.lib import promptGrammar as module  # type: ignore[import]
    _PROMPT_GRAMMAR_MODULE = module
    return module


def export_prompt_grammar(
    output_path: Path, *, indent: int | None = 2
) -> dict[str, Any]:
    payload = _prompt_grammar_module().prompt_grammar_payload()

    output_path.parent.mkdir(parents=True, exist_ok=True)

    json_kwargs: dict[str, Any] = {"ensure_ascii": False}
    if indent is None:
        json_kwargs["separators"] = (",", ":")
    else:
        json_kwargs["indent"] = max(indent, 0)

    data = json.dumps(payload, **json_kwargs)
    if not data.endswith("\n"):
        data += "\n"
    output_path.write_text(data, encoding="utf-8")
    return payload


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m prompts.export",
        description="Export the Concordance prompt grammar to JSON.",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Destination path for the exported JSON (default: build/prompt-grammar.json).",
    )
    parser.add_argument(
        "--indent",
        dest="indent",
        type=int,
        default=2,
        help="Indent level for pretty JSON output (default: 2).",
    )
    parser.add_argument(
        "--compact",
        dest="compact",
        action="store_true",
        help="Emit compact JSON without indentation.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    indent: int | None = None if args.compact else args.indent
    try:
        export_prompt_grammar(args.output, indent=indent)
    except Exception as exc:  # pragma: no cover - defensive guardrail
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote prompt grammar to {args.output}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    sys.exit(main())
