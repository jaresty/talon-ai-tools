"""Tests for _token_text() field-prefix structure in scripts/embed_tokens.py.

Each field type (definition, heuristics, distinctions, routing_concept) must be
prefixed with its role label so the embedding vector encodes field role, not just
semantic content.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.embed_tokens import _token_text


def test_definition_is_prefixed():
    """D1: definition must be prefixed with 'Definition:'."""
    meta = {"definition": "some definition text"}
    result = _token_text(meta)
    assert "Definition: some definition text" in result, (
        "_token_text must prefix definition with 'Definition:'"
    )


def test_heuristics_are_prefixed():
    """D2: each heuristic must be prefixed with 'Use when:'."""
    meta = {"definition": "def", "heuristics": ["first heuristic", "second heuristic"]}
    result = _token_text(meta)
    assert "Use when: first heuristic" in result, (
        "_token_text must prefix each heuristic with 'Use when:'"
    )
    assert "Use when: second heuristic" in result, (
        "_token_text must prefix each heuristic with 'Use when:'"
    )


def test_distinctions_are_prefixed():
    """D3: each distinction must be prefixed with 'Contrast with <token>:'."""
    meta = {
        "definition": "def",
        "distinctions": [{"token": "other", "note": "the contrast note"}],
    }
    result = _token_text(meta)
    assert "Contrast with other: the contrast note" in result, (
        "_token_text must prefix each distinction with 'Contrast with <token>:'"
    )


def test_routing_concept_is_prefixed():
    """D4: routing_concept must be prefixed with 'Routing:'."""
    meta = {"definition": "def"}
    result = _token_text(meta, routing_concept="some routing concept")
    assert "Routing: some routing concept" in result, (
        "_token_text must prefix routing_concept with 'Routing:'"
    )
