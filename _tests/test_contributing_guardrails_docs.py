import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class ContributingGuardrailsDocsTests(unittest.TestCase):
        def test_contributing_mentions_guardrail_targets(self) -> None:
            """Guardrail: CONTRIBUTING should surface guardrail targets and helper."""

            text = (Path(__file__).resolve().parents[1] / "CONTRIBUTING.md").read_text(encoding="utf-8")
            self.assertIn("axis-guardrails", text)
            self.assertIn("axis-catalog-validate", text)
            self.assertIn("axis-cheatsheet", text)
            self.assertIn("axis-guardrails-ci", text)
            self.assertIn("axis-guardrails-test", text)
            self.assertIn("ci-guardrails", text)
            self.assertIn("guardrails", text)
            self.assertIn("talon-lists", text)
            self.assertIn("talon-lists-check", text)
            self.assertIn("not tracked", text, "Expected CONTRIBUTING to state axis/static prompt Talon lists are untracked")
            self.assertIn("run_guardrails_ci.sh", text)
            self.assertIn("[--help|target]", text)
            self.assertIn("GUARDRAILS_TARGET", text)
            self.assertIn("axis-catalog-validate.py --lists-dir", text)
            self.assertIn("--skip-list-files", text)
            self.assertIn("--no-skip-list-files", text)

else:

    class ContributingGuardrailsDocsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
