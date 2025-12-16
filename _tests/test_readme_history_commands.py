import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from pathlib import Path

    class ReadmeHistoryCommandsTests(unittest.TestCase):
        def test_readme_mentions_history_save_commands(self) -> None:
            """Guardrail: README should list history save/copy/open/show commands."""

            root = Path(__file__).resolve().parents[1]
            readme = root / "readme.md"
            text = readme.read_text(encoding="utf-8")
            self.assertIn("model history save exchange", text)
            self.assertIn("model history copy last save", text)
            self.assertIn("model history open last save", text)
            self.assertIn("model history show last save", text)

else:
    if not TYPE_CHECKING:
        class ReadmeHistoryCommandsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
