import json
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
            summary_path = (
                repo_root
                / "artifacts"
                / "history-axis-summaries"
                / "history-validation-summary.json"
            )
            if summary_path.exists():
                summary_path.unlink()
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
            self.assertTrue(
                summary_path.exists(),
                "request-history-guardrails did not produce history-validation-summary.json",
            )
            with summary_path.open("r", encoding="utf-8") as handle:
                stats = json.load(handle)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)

        def test_make_request_history_guardrails_fast_produces_summary(self) -> None:
            """Guardrail: request-history-guardrails-fast should export the validation summary."""

            repo_root = Path(__file__).resolve().parents[1]
            summary_path = (
                repo_root
                / "artifacts"
                / "history-axis-summaries"
                / "history-validation-summary.json"
            )
            if summary_path.exists():
                summary_path.unlink()
            result = subprocess.run(
                ["make", "request-history-guardrails-fast"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make request-history-guardrails-fast failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertTrue(
                summary_path.exists(),
                "request-history-guardrails-fast did not produce history-validation-summary.json",
            )
            with summary_path.open("r", encoding="utf-8") as handle:
                stats = json.load(handle)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)


else:
    if not TYPE_CHECKING:

        class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
