"""Tests for embedding vectors in the grammar JSON (ADR-XXXX hybrid search)."""
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

GRAMMAR_PATH = Path(__file__).resolve().parents[1] / "build" / "prompt-grammar.json"
EMBED_DIM = 384  # all-MiniLM-L6-v2


def _all_token_meta(grammar: dict) -> list[dict]:
    """Return every token metadata dict from axes, static tasks, and persona."""
    results = []
    for _axis, tokens in grammar.get("axes", {}).get("metadata", {}).items():
        results.extend(tokens.values())
    for _task, meta in grammar.get("static", {}).get("metadata", {}).items():
        results.append(meta)
    for _axis, tokens in grammar.get("persona", {}).get("metadata", {}).items():
        results.extend(tokens.values())
    return results


class TokenTextTests(unittest.TestCase):
    """Tests for _token_text() field composition."""

    def test_T1_token_text_prefixes_axis_description(self) -> None:
        """_token_text must prefix with axis_description so the model learns axis semantics."""
        from embed_tokens import _token_text  # noqa: PLC0415
        meta = {"definition": "Linear stage sequencing"}
        axis_desc = "Reasoning approach — how to think through the problem"
        text = _token_text(meta, axis_desc=axis_desc, label="flow", routing_concept="")
        self.assertTrue(
            text.startswith(axis_desc),
            f"_token_text must start with axis_description; got: {text[:80]}",
        )

    def test_T2_token_text_includes_routing_concept(self) -> None:
        """_token_text must include routing_concept when non-empty."""
        from embed_tokens import _token_text  # noqa: PLC0415
        meta = {"definition": "Linear stage sequencing"}
        rc = "sequence steps in a pipeline"
        text = _token_text(meta, axis_desc="", label="flow", routing_concept=rc)
        self.assertIn(rc, text, f"_token_text must include routing_concept; got: {text}")

    def test_T3_all_metas_yields_axis_desc(self) -> None:
        """_all_metas must yield (meta, axis_desc, label, routing_concept) tuples
        with non-empty axis_desc for axis tokens so _token_text gets category context."""
        from embed_tokens import _all_metas  # noqa: PLC0415
        grammar = json.loads(GRAMMAR_PATH.read_text())
        entries = _all_metas(grammar)
        self.assertGreater(len(entries), 0, "no entries returned")
        first = entries[0]
        self.assertIsInstance(first, tuple, f"_all_metas must return tuples, got {type(first)}")
        self.assertEqual(len(first), 4, f"each tuple must be (meta, axis_desc, label, routing_concept), got len={len(first)}")
        _, axis_desc, _, _ = first
        self.assertTrue(
            any(axis_desc for _, axis_desc, _, _ in entries),
            "_all_metas must populate axis_desc for at least one entry",
        )


class EmbedTokensTests(unittest.TestCase):
    def setUp(self) -> None:
        self.grammar = json.loads(GRAMMAR_PATH.read_text())
        self.metas = _all_token_meta(self.grammar)
        self.assertGreater(len(self.metas), 0, "no tokens found in grammar")

    def test_E1_every_token_has_embedding_field(self) -> None:
        """D1+D2: every token metadata dict has an 'embedding' key."""
        if self.metas and "embedding" not in self.metas[0]:
            self.skipTest("embeddings not present in grammar JSON (not generated in this environment)")
        missing = [
            str(i) for i, m in enumerate(self.metas) if "embedding" not in m
        ]
        self.assertEqual(
            missing,
            [],
            f"tokens missing 'embedding' field at indices: {missing[:5]}",
        )

    def test_E2_embedding_is_correct_dimension(self) -> None:
        """D1: each embedding vector has exactly EMBED_DIM floats."""
        wrong = [
            str(i)
            for i, m in enumerate(self.metas)
            if "embedding" in m and len(m["embedding"]) != EMBED_DIM
        ]
        self.assertEqual(
            wrong,
            [],
            f"tokens with wrong embedding dimension at indices: {wrong[:5]}",
        )

    def test_E3_embedding_self_cosine_near_one(self) -> None:
        """D2: cosine similarity of first token embedding with itself is ~1.0."""
        meta = next((m for m in self.metas if "embedding" in m), None)
        if meta is None:
            self.skipTest("no token with embedding found")
        v = meta["embedding"]
        dot = sum(x * x for x in v)
        norm = math.sqrt(dot)
        self.assertAlmostEqual(norm, 1.0, places=3, msg="embedding should be unit-normalised")
