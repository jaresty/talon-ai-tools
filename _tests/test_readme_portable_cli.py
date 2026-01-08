import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - Talon runtime fallback
    bootstrap = None
else:  # pragma: no cover - executed in test harness
    bootstrap()

README_PATH = Path(__file__).resolve().parents[1] / "readme.md"

if bootstrap is not None:

    class PortablePromptGrammarCLIDocs(unittest.TestCase):
        def test_readme_covers_portable_cli_quickstart(self) -> None:
            content = README_PATH.read_text(encoding="utf-8")
            self.assertIn("Portable prompt grammar CLI", content)

            expectations = (
                "python3 -m prompts.export --output build/prompt-grammar.json",
                "bar help tokens",
                "bar build todo focus steps fog --json",
                'echo "Fix onboarding" | bar build todo focus steps fog persona=facilitator intent=coach',
            )

            for snippet in expectations:
                with self.subTest(snippet=snippet):
                    self.assertIn(snippet, content)
else:
    if not TYPE_CHECKING:

        class PortablePromptGrammarCLIDocs(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
