import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - Talon runtime fallback
    bootstrap = None
else:  # pragma: no cover - import side-effects only
    bootstrap()

if bootstrap is not None and not TYPE_CHECKING:

    class HistoryTelemetryInspectTests(unittest.TestCase):
        def test_inspect_outputs_guardrail_target(self) -> None:
            telemetry = {
                "guardrail_target": "request-history-guardrails-fast",
                "summary_path": "/tmp/history-validation-summary.json",
                "total_entries": 7,
                "gating_drop_total": 3,
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                telemetry_path = tmp_path / "history-validation-summary.telemetry.json"
                telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-telemetry-inspect.py",
                        str(telemetry_path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"history-telemetry-inspect failed: {result.stdout}\n{result.stderr}",
                )
                self.assertIn(
                    "guardrail_target: request-history-guardrails-fast",
                    result.stdout,
                )

        def test_summary_format_outputs_selected_fields(self) -> None:
            telemetry = {
                "guardrail_target": "request-history-guardrails-fast",
                "summary_path": "artifacts/telemetry/history-validation-summary.json",
                "total_entries": 9,
                "gating_drop_total": 4,
                "gating_drop_rate": 0.44,
                "streaming_status": "ok",
                "last_drop_message": "GPT: Request blocked; reason=in_flight",
                "streaming_last_drop_message": "none",
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                telemetry_path = tmp_path / "history-validation-summary.telemetry.json"
                telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-telemetry-inspect.py",
                        str(telemetry_path),
                        "--format",
                        "summary",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"history-telemetry-inspect summary failed: {result.stdout}\n{result.stderr}",
                )
                self.assertIn(
                    "summary: guardrail_target=request-history-guardrails-fast",
                    result.stdout,
                )
                self.assertIn("gating_drop_total=4", result.stdout)
                self.assertIn(
                    "summary_path=artifacts/telemetry/history-validation-summary.json",
                    result.stdout,
                )
                self.assertIn("total_entries=9", result.stdout)
                self.assertIn("streaming_status=ok", result.stdout)

        def test_reports_cli_recovery_fields(self) -> None:
            telemetry = {
                "guardrail_target": "request-history-guardrails-fast",
                "summary_path": "artifacts/telemetry/history-validation-summary.json",
                "total_entries": 4,
                "cli_delegation_enabled": True,
                "cli_recovery_code": "cli_recovered",
                "cli_recovery_details": "health probes restored",
                "cli_recovery_prompt": "CLI delegation restored after failure.",
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                telemetry_path = tmp_path / "history-validation-summary.telemetry.json"
                telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-telemetry-inspect.py",
                        str(telemetry_path),
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"history-telemetry-inspect failed: {result.stdout}\n{result.stderr}",
                )
                stdout = result.stdout
                self.assertIn("cli_delegation_enabled: True", stdout)
                self.assertIn("cli_recovery_code: cli_recovered", stdout)
                self.assertIn("cli_recovery_details: health probes restored", stdout)
                self.assertIn(
                    "cli_recovery_prompt: CLI delegation restored after failure.",
                    stdout,
                )

        def test_json_format_returns_machine_readable_payload(self) -> None:
            telemetry = {
                "guardrail_target": "request-history-guardrails-fast",
                "total_entries": 11,
                "gating_drop_total": 2,
                "gating_drop_rate": 0.18,
                "streaming_status": "ok",
                "last_drop_message": "none",
            }

            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_path = Path(tmpdir)
                telemetry_path = tmp_path / "history-validation-summary.telemetry.json"
                telemetry_path.write_text(json.dumps(telemetry), encoding="utf-8")

                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/tools/history-telemetry-inspect.py",
                        str(telemetry_path),
                        "--format",
                        "json",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"history-telemetry-inspect json failed: {result.stdout}\n{result.stderr}",
                )
                lines = [line for line in result.stdout.splitlines() if line.strip()]
                self.assertEqual(
                    len(lines), 1, msg=f"unexpected json output: {result.stdout}"
                )
                payload = json.loads(lines[0])
                self.assertEqual(payload["telemetry"], str(telemetry_path))
                self.assertEqual(
                    payload["guardrail_target"], "request-history-guardrails-fast"
                )
                self.assertEqual(payload["gating_drop_total"], 2)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    unittest.main()
