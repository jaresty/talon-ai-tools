import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
        def test_make_request_history_guardrails_runs_clean(self) -> None:
            """Guardrail: request-history-guardrails target should run without errors."""

            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "request-history-guardrails"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make request-history-guardrails failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

else:
    if not TYPE_CHECKING:
        class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
