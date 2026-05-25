#!/usr/bin/env python3
"""Pre-commit check: verify all token metadata in prompt-grammar.json has embedding vectors.

Fails with a clear message if any token is missing its embedding, directing the
developer to run scripts/embed_tokens.py before committing.

Usage:
    python3 scripts/check_embeddings.py [path/to/prompt-grammar.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_GRAMMAR = Path(__file__).resolve().parents[1] / "build" / "prompt-grammar.json"


def check_embeddings(grammar_path: Path) -> list[str]:
    """Return list of missing-embedding descriptions; empty list means all present."""
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    missing: list[str] = []

    axes_meta = grammar.get("axes", {}).get("metadata", {})
    for axis, tokens in axes_meta.items():
        for token, meta in tokens.items():
            if not isinstance(meta, dict) or "embedding" not in meta:
                missing.append(f"axes.metadata.{axis}.{token}")

    task_meta = grammar.get("tasks", {}).get("metadata", {})
    for token, meta in task_meta.items():
        if not isinstance(meta, dict) or "embedding" not in meta:
            missing.append(f"tasks.metadata.{token}")

    persona_meta = grammar.get("persona", {}).get("metadata", {})
    for axis, tokens in persona_meta.items():
        if not isinstance(tokens, dict):
            continue
        for token, meta in tokens.items():
            if not isinstance(meta, dict) or "embedding" not in meta:
                missing.append(f"persona.metadata.{axis}.{token}")

    return missing


def main() -> None:
    grammar_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_GRAMMAR
    if not grammar_path.exists():
        print(f"check_embeddings: {grammar_path} not found", file=sys.stderr)
        sys.exit(1)

    missing = check_embeddings(grammar_path)
    if missing:
        print(
            f"check_embeddings: {len(missing)} token(s) missing embedding vectors in {grammar_path}",
            file=sys.stderr,
        )
        for m in missing[:10]:
            print(f"  - {m}", file=sys.stderr)
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more", file=sys.stderr)
        print(
            "\nRun: .venv/bin/python3 scripts/embed_tokens.py",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"check_embeddings: OK ({grammar_path.name})")


if __name__ == "__main__":
    main()
