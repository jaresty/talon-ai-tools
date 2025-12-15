import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class GuardrailsOverlayTargetsTests(unittest.TestCase):
        def test_guardrails_targets_include_overlay_lifecycle(self) -> None:
            makefile = Path(__file__).resolve().parents[1] / "Makefile"
            text = makefile.read_text(encoding="utf-8")
            self.assertIn("guardrails: ci-guardrails overlay-guardrails overlay-lifecycle-guardrails", text)
            self.assertIn("ci-guardrails: axis-guardrails-ci overlay-guardrails overlay-lifecycle-guardrails", text)
