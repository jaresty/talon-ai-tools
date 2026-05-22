#!/usr/bin/env python3
"""Add embedding vectors to prompt-grammar.json for hybrid BM25+embedding search.

Uses all-MiniLM-L6-v2 (384-dim, ~90MB download on first run, cached thereafter).
Reads build/prompt-grammar.json, writes embedding field onto every token metadata
dict, then overwrites the file and its mirrors.

Usage:
    .venv/bin/python3 scripts/embed_tokens.py
    .venv/bin/python3 scripts/embed_tokens.py --grammar path/to/grammar.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_GRAMMAR = Path(__file__).resolve().parents[1] / "build" / "prompt-grammar.json"
MIRRORS = [
    Path(__file__).resolve().parents[1] / "internal" / "barcli" / "embed" / "prompt-grammar.json",
    Path(__file__).resolve().parents[1] / "cmd" / "bar" / "testdata" / "grammar.json",
    Path(__file__).resolve().parents[1] / "web" / "static" / "prompt-grammar.json",
]


def _token_text(
    meta: dict[str, Any],
    *,
    axis_desc: str = "",
    label: str = "",
    routing_concept: str = "",
) -> str:
    parts: list[str] = []
    if axis_desc:
        prefix = axis_desc
        if label:
            prefix += f" | {label}"
        parts.append(prefix + ":")
    elif label:
        parts.append(f"{label}:")
    if meta.get("definition"):
        parts.append(meta["definition"])
    if meta.get("heuristics"):
        parts.extend(meta["heuristics"])
    if meta.get("distinctions"):
        parts.extend(d.get("token", "") + " " + d.get("note", "") for d in meta["distinctions"])
    if routing_concept:
        parts.append(routing_concept)
    return " ".join(p for p in parts if p).strip() or "token"


def _all_metas(grammar: dict[str, Any]) -> list[tuple[dict[str, Any], str, str, str]]:
    """Return (meta, axis_desc, label, routing_concept) for every token."""
    axis_descs: dict[str, str] = grammar.get("axes", {}).get("axis_descriptions", {})
    persona_desc = "Communication style — who speaks, for whom, and in what tone."
    task_desc = "What the response does — the primary action to perform."
    entries: list[tuple[dict[str, Any], str, str, str]] = []

    axes_meta = grammar.get("axes", {}).get("metadata", {})
    axes_labels = grammar.get("axes", {}).get("labels", {})
    for axis, tokens in axes_meta.items():
        desc = axis_descs.get(axis, "")
        for token, meta in tokens.items():
            label = axes_labels.get(axis, {}).get(token, "")
            rc = meta.get("routing_concept", "")
            entries.append((meta, desc, label, rc))

    static_meta = grammar.get("static", {}).get("metadata", {})
    static_labels = grammar.get("static", {}).get("labels", {})
    for token, meta in static_meta.items():
        label = static_labels.get(token, "")
        rc = meta.get("routing_concept", "")
        entries.append((meta, task_desc, label, rc))

    persona_meta = grammar.get("persona", {}).get("metadata", {})
    persona_labels = grammar.get("persona", {}).get("labels", {})
    for axis, tokens in persona_meta.items():
        for token, meta in tokens.items():
            label = persona_labels.get(axis, {}).get(token, "") if isinstance(persona_labels.get(axis), dict) else ""
            rc = meta.get("routing_concept", "")
            entries.append((meta, persona_desc, label, rc))

    return entries


def embed_grammar(grammar_path: Path) -> None:
    from sentence_transformers import SentenceTransformer

    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    entries = _all_metas(grammar)
    texts = [
        _token_text(m, axis_desc=ad, label=lb, routing_concept=rc)
        for m, ad, lb, rc in entries
    ]

    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    print(f"Embedding {len(texts)} tokens...")
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    for (meta, _, _, _), vec in zip(entries, vectors):
        meta["embedding"] = [round(float(x), 6) for x in vec]

    data = json.dumps(grammar, ensure_ascii=False, indent=2)
    if not data.endswith("\n"):
        data += "\n"

    grammar_path.write_text(data, encoding="utf-8")
    print(f"Wrote {grammar_path}")

    for mirror in MIRRORS:
        if mirror != grammar_path and mirror.exists():
            mirror.write_text(data, encoding="utf-8")
            print(f"Mirrored to {mirror}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add embeddings to prompt-grammar.json")
    parser.add_argument("--grammar", type=Path, default=DEFAULT_GRAMMAR)
    args = parser.parse_args()
    embed_grammar(args.grammar)


if __name__ == "__main__":
    main()
