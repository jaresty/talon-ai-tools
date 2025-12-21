import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

if not TYPE_CHECKING:

    class HistoryGuardrailChecklistTests(unittest.TestCase):
        def setUp(self) -> None:
            self.repo_root = Path(__file__).resolve().parents[1]
            self.script = (
                self.repo_root / "scripts" / "tools" / "history-guardrail-checklist.py"
            )

        def test_plain_output_mentions_required_commands(self) -> None:
            result = subprocess.run(
                [sys.executable, str(self.script)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    "history-guardrail-checklist.py failed with code"
                    f" {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

            output = result.stdout
            self.assertIn(
                "make request-history-guardrails",
                output,
                "Checklist should remind operators to run the history guardrails target.",
            )
            self.assertIn(
                "scripts/tools/history-axis-validate.py --summary-path",
                output,
                "Checklist should include the telemetry summary archive command.",
            )
            self.assertIn(
                "scripts/tools/run_guardrails_ci.sh request-history-guardrails",
                output,
                "Checklist should reference the CI helper for parity runs.",
            )

        def test_json_output_is_structured(self) -> None:
            result = subprocess.run(
                [sys.executable, str(self.script), "--format", "json"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.repo_root),
            )
            if result.returncode != 0:
                self.fail(
                    "history-guardrail-checklist.py --format json failed with code"
                    f" {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

            payload = json.loads(result.stdout or "{}")
            self.assertEqual(payload.get("helper_version"), "helper:v20251221.0")
            steps = payload.get("steps")
            self.assertIsInstance(steps, list)
            self.assertGreaterEqual(len(steps or []), 3)
            commands = [
                step.get("command", "") for step in steps if isinstance(step, dict)
            ]
            self.assertTrue(
                any(
                    "history-axis-validate.py --summary-path" in command
                    for command in commands
                ),
                "Structured checklist should include the telemetry summary archive command.",
            )
            self.assertIn(
                "artifacts/history-axis-summaries/history-validation-summary.json",
                payload.get("artifact_path", ""),
            )

else:
    if not TYPE_CHECKING:

        class HistoryGuardrailChecklistTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
