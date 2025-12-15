import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class RunGuardrailsCIDefaultTargetTests(unittest.TestCase):
        def test_default_target_guardrails(self) -> None:
            """Guardrail: CI helper default target should be 'guardrails' when no arg/env is set."""

            script = (Path(__file__).resolve().parents[1] / "scripts" / "tools" / "run_guardrails_ci.sh").read_text(
                encoding="utf-8"
            )
            flat = script.replace("\n", " ")
            self.assertIn('TARGET="${1:-${GUARDRAILS_TARGET:-guardrails}}"', flat)

else:

    class RunGuardrailsCIDefaultTargetTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
