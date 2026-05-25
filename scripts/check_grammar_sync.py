#!/usr/bin/env python3
"""Verify that prompt-grammar.json is in sync with source, ignoring embedding vectors.

CI does not generate embeddings (no sentence_transformers), so a raw git diff would
always fail when embeddings are present. This script compares grammar content with
the embedding fields stripped so CI can verify structural sync independently.

Usage:
    python3 scripts/check_grammar_sync.py <regenerated.json> <committed.json>

Exits 0 if files are equivalent after stripping embeddings; 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def strip_embeddings(obj: object) -> object:
    if isinstance(obj, dict):
        return {k: strip_embeddings(v) for k, v in obj.items() if k != "embedding"}
    if isinstance(obj, list):
        return [strip_embeddings(i) for i in obj]
    return obj


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: check_grammar_sync.py <regenerated.json> <committed.json>", file=sys.stderr)
        sys.exit(1)

    regen_path = Path(sys.argv[1])
    committed_path = Path(sys.argv[2])

    regen = strip_embeddings(json.loads(regen_path.read_text(encoding="utf-8")))
    committed = strip_embeddings(json.loads(committed_path.read_text(encoding="utf-8")))

    if regen != committed:
        print(
            f"check_grammar_sync: {committed_path.name} is out of sync with source "
            "(non-embedding content differs). Run: make bar-grammar-update",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"check_grammar_sync: OK ({committed_path.name})")


if __name__ == "__main__":
    main()
