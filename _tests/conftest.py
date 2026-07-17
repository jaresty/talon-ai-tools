"""Skip tests that require local environment features not present in CI."""
import importlib.util
import json
from pathlib import Path

import pytest


def _grammar_has_embeddings() -> bool:
    grammar_path = Path(__file__).resolve().parents[1] / "build" / "prompt-grammar.json"
    try:
        grammar = json.loads(grammar_path.read_text())
        axes_meta = grammar.get("axes", {}).get("metadata", {})
        for tokens in axes_meta.values():
            for meta in tokens.values():
                return "embedding" in meta
    except Exception:
        pass
    return False


def pytest_runtest_setup(item):
    source = item.fspath.read_text(encoding="utf-8")
    # Skip tests that require the Talon runtime when talon is not importable.
    if importlib.util.find_spec("talon") is None:
        if "from talon import" in source or "import talon\n" in source:
            pytest.skip("talon runtime not available")
    # Skip embedding tests when embeddings are not present in the grammar JSON.
    if "embedding" in source and item.fspath.name == "test_embed_tokens.py":
        if not _grammar_has_embeddings():
            pytest.skip("embeddings not present in grammar JSON")
