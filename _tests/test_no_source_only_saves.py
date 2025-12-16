import unittest
from pathlib import Path


class NoSourceOnlySavesTests(unittest.TestCase):
    def test_no_history_save_source_surfaces_outside_adrs(self) -> None:
        """Guardrail: prevent reintroducing the deprecated source-only history command."""

        root = Path(__file__).resolve().parents[1]
        banned_tokens = [
            "history save source",
            "model source save",
            "save source to file",
        ]
        matches: dict[str, list[str]] = {}
        for path in root.rglob("*"):
            if path.is_dir():
                continue
            rel = path.relative_to(root)
            rel_str = str(rel)
            # Allow ADRs to record historical context and skip generated/cache/tmp artefacts.
            if rel_str.startswith(("docs/adr", "tmp/", "tmp\\", "__pycache__", ".git", ".pytest_cache")):
                continue
            if rel.name.endswith((".pyc", ".pyo")):
                continue
            if rel == Path(__file__).relative_to(root):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for token in banned_tokens:
                if token in text:
                    matches.setdefault(token, []).append(rel_str)
        self.assertFalse(
            matches,
            f"Found deprecated source-only save strings outside ADRs: {matches}",
        )
