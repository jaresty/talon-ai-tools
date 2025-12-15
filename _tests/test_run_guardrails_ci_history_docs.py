import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class RunGuardrailsCIHistoryDocsTests(unittest.TestCase):
        def test_usage_mentions_request_history_guardrails(self) -> None:
            """Guardrail: CI helper usage should mention request-history guardrails."""

            repo_root = Path(__file__).resolve().parents[1]
            script = repo_root / "scripts" / "tools" / "run_guardrails_ci.sh"
            result = subprocess.run(
                ["/bin/bash", str(script), "--help"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh --help failed:\nexit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            output = result.stdout
            self.assertIn(
                "request-history guardrails",
                output,
                "Expected CI helper usage to mention request-history guardrails",
            )
            self.assertIn(
                "request-history-guardrails[-fast]",
                output,
                "Expected CI helper usage to mention the fast history guardrail target",
            )

else:
    if not TYPE_CHECKING:
        class RunGuardrailsCIHistoryDocsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
