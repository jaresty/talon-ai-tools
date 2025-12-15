import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GitignoreTalonListsTests(unittest.TestCase):
        def test_gitignore_masks_generated_talon_lists(self) -> None:
            """Guardrail: generated axis/static prompt Talon lists should remain untracked."""

            repo_root = Path(__file__).resolve().parents[1]
            gitignore = repo_root / ".gitignore"
            content = gitignore.read_text(encoding="utf-8")
            self.assertIn(
                "GPT/lists/*.talon-list",
                content,
                "Expected .gitignore to ignore generated axis/static prompt Talon lists.",
            )

else:

    class GitignoreTalonListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
