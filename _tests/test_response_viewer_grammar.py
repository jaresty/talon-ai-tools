"""Guardrail: response-viewer and confirmation-gui Talon files expose
model-prefixed show/pass response commands (ADR-0057 D4/D5, ADR-0080 Workstream 1)."""

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

    class ResponseViewerGrammarTests(unittest.TestCase):
        def test_show_response_rule_in_viewer_file(self) -> None:
            """Guardrail: gpt-response-viewer.talon exposes 'model show response'
            mapped to model_response_canvas_open (ADR-0057 D4)."""
            root = Path(__file__).resolve().parents[1]
            talon_file = root / "GPT" / "gpt-response-viewer.talon"
            text = talon_file.read_text(encoding="utf-8")
            self.assertIn("show response", text)
            self.assertIn("model_response_canvas_open", text)

        def test_pass_response_rule_in_confirmation_gui_file(self) -> None:
            """Guardrail: gpt-confirmation-gui.talon exposes 'model pass response'
            mapped to confirmation_gui_paste (ADR-0057 D5)."""
            root = Path(__file__).resolve().parents[1]
            talon_file = root / "GPT" / "gpt-confirmation-gui.talon"
            text = talon_file.read_text(encoding="utf-8")
            self.assertIn("pass response", text)
            self.assertIn("confirmation_gui_paste", text)

else:
    if not TYPE_CHECKING:

        class ResponseViewerGrammarTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
