import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class RunGuardrailsCITests(unittest.TestCase):
        def test_run_guardrails_ci_script(self) -> None:
            """Guardrail: CI helper script should run guardrails successfully."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
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
                ["/bin/bash", str(script), "axis-guardrails-ci"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn(
                "Axis catalog validation passed",
                result.stdout,
                "Expected guardrail script to run catalog validation",
            )
            self.assertIn(
                "Running guardrails target: axis-guardrails-ci", result.stdout
            )
            self.assertIn(
                "target axis-guardrails-ci does not require it",
                result.stdout,
                "Expected optional summary message for axis guardrails target",
            )
            self.assertIn(
                "History summary not required for target axis-guardrails-ci; no job summary entry created.",
                result.stdout,
            )

        def test_run_guardrails_ci_help(self) -> None:
            """Guardrail: CI helper script should expose help/usage."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            result = subprocess.run(
                ["/bin/bash", str(script), "--help"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh --help failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn("Usage: scripts/tools/run_guardrails_ci.sh", result.stdout)
            self.assertIn("catalog-only", result.stdout)
            self.assertIn("GUARDRAILS_TARGET", result.stdout)
            self.assertIn("axis-guardrails-ci", result.stdout)

        def test_run_guardrails_ci_env_override(self) -> None:
            """Guardrail: CI helper should honor GUARDRAILS_TARGET when no arg is provided."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            env = os.environ.copy()
            env["GUARDRAILS_TARGET"] = "axis-guardrails-ci"

            result = subprocess.run(
                ["/bin/bash", str(script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
                env=env,
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh with GUARDRAILS_TARGET failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn(
                "Axis catalog validation passed",
                result.stdout,
                "Expected guardrail script to run catalog validation via env target",
            )
            self.assertIn(
                "Running guardrails target: axis-guardrails-ci", result.stdout
            )

        def test_run_guardrails_ci_history_target_produces_summary(self) -> None:
            """Guardrail: history guardrail target should emit and persist the summary."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
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
                ["/bin/bash", str(script), "request-history-guardrails"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    f"run_guardrails_ci.sh request-history-guardrails failed with code {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )
            self.assertIn(
                "History validation summary (JSON):",
                result.stdout,
                "Expected CI helper to log the saved history summary",
            )
            self.assertTrue(
                summary_path.exists(),
                "run_guardrails_ci.sh did not write the history summary artifact",
            )
            with summary_path.open("r", encoding="utf-8") as handle:
                stats = json.load(handle)
            self.assertIn("gating_drop_counts", stats)
            self.assertIn(
                "History summary stats: total_entries=0 gating_drop_total=0",
                result.stdout,
            )
            self.assertIn(
                "History summary recorded at artifacts/history-axis-summaries/history-validation-summary.json; job summary will reference this file when running in GitHub Actions.",
                result.stdout,
            )

        def test_run_guardrails_ci_invalid_target(self) -> None:
            """Guardrail: CI helper should fail clearly on invalid targets."""

            script = (
                Path(__file__).resolve().parents[1]
                / "scripts"
                / "tools"
                / "run_guardrails_ci.sh"
            )
            result = subprocess.run(
                ["/bin/bash", str(script), "nonexistent-target"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(Path(__file__).resolve().parents[1]),
            )
            self.assertNotEqual(result.returncode, 0, "Expected invalid target to fail")
            self.assertIn(
                "Running guardrails target: nonexistent-target", result.stdout
            )
            # Make consistently reports missing targets; assert a hint is present.
            self.assertTrue(
                "No rule" in result.stderr or "unknown target" in result.stderr.lower(),
                f"Expected make to report missing target; stderr was:\n{result.stderr}",
            )

else:

    class RunGuardrailsCITests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass
