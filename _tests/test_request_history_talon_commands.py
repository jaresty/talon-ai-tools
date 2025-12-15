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

    class RequestHistoryTalonCommandsTests(unittest.TestCase):
        def test_request_history_talon_includes_save_copy_open_show(self) -> None:
            """Guardrail: request-history Talon file lists save/copy/open/show commands."""

            root = Path(__file__).resolve().parents[1]
            talon_file = root / "GPT" / "request-history.talon"
            text = talon_file.read_text(encoding="utf-8")
            self.assertIn("history save source", text)
            self.assertIn("history copy last save", text)
            self.assertIn("history open last save", text)
            self.assertIn("history show last save", text)

else:
    if not TYPE_CHECKING:
        class RequestHistoryTalonCommandsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
