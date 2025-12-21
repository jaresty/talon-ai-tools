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
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            self.assertTrue(lines, "make output unexpectedly empty")
            self.assertIn(
                "Streaming gating summary: status=unknown; total=0; counts=none; sources=none; last=n/a; last_source=n/a; last_message=none",
                result.stdout,
            )
            self.assertIn(
                "Streaming gating summary (json):",
                result.stdout,
            )
            self.assertIn("- Last gating drop: none", result.stdout)
            self.assertIn("- Streaming last drop: none", result.stdout)
            self.assertTrue(
                summary_path.exists(),
                "request-history-guardrails did not produce history-validation-summary.json",
            )
            with summary_path.open("r", encoding="utf-8") as handle:
                stats = json.load(handle)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)
            self.assertIn("streaming_gating_summary", stats)

            streaming_summary_path = summary_path.with_name(
                "history-validation-summary.streaming.json"
            )
            self.assertTrue(
                streaming_summary_path.exists(),
                "Streaming JSON summary was not produced",
            )
            with streaming_summary_path.open("r", encoding="utf-8") as handle:
                streaming_data = json.load(handle)
            self.assertEqual(
                streaming_data.get("streaming_gating_summary"),
                {
                    "counts": {},
                    "counts_sorted": [],
                    "sources": {},
                    "sources_sorted": [],
                    "last": {},
                    "last_source": {},
                    "total": 0,
                    "status": "unknown",
                    "last_message": "",
                    "last_code": "",
                },
            )

            telemetry_path = summary_path.with_name(
                "history-validation-summary.telemetry.json"
            )
            self.assertTrue(
                telemetry_path.exists(),
                "Telemetry export was not produced",
            )
            telemetry_payload = json.loads(telemetry_path.read_text(encoding="utf-8"))
            self.assertEqual(telemetry_payload.get("total_entries"), 0)
            self.assertEqual(telemetry_payload.get("gating_drop_total"), 0)
            self.assertIn("generated_at", telemetry_payload)
            self.assertEqual(telemetry_payload.get("top_gating_reasons"), [])
            self.assertEqual(telemetry_payload.get("top_gating_sources"), [])
            self.assertEqual(telemetry_payload.get("streaming_status"), "unknown")
            self.assertEqual(telemetry_payload.get("last_drop_message"), "none")
            self.assertIsNone(telemetry_payload.get("last_drop_code"))

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
            lines = [line for line in result.stdout.splitlines() if line.strip()]
            self.assertTrue(lines, "make output unexpectedly empty")
            self.assertIn(
                "Streaming gating summary: status=unknown; total=0; counts=none; sources=none; last=n/a; last_source=n/a; last_message=none",
                result.stdout,
            )
            self.assertIn(
                "Streaming gating summary (json):",
                result.stdout,
            )
            self.assertIn("- Last gating drop: none", result.stdout)
            self.assertIn("- Streaming last drop: none", result.stdout)
            self.assertTrue(
                summary_path.exists(),
                "request-history-guardrails-fast did not produce history-validation-summary.json",
            )
            with summary_path.open("r", encoding="utf-8") as handle:
                stats = json.load(handle)
            self.assertIn("total_entries", stats)
            self.assertIn("entries_missing_directional", stats)
            self.assertIn("streaming_gating_summary", stats)

            streaming_summary_path = summary_path.with_name(
                "history-validation-summary.streaming.json"
            )
            self.assertTrue(
                streaming_summary_path.exists(),
                "Streaming JSON summary was not produced (fast target)",
            )
            with streaming_summary_path.open("r", encoding="utf-8") as handle:
                streaming_data = json.load(handle)
            self.assertEqual(
                streaming_data.get("streaming_gating_summary"),
                {
                    "counts": {},
                    "counts_sorted": [],
                    "sources": {},
                    "sources_sorted": [],
                    "last": {},
                    "last_source": {},
                    "total": 0,
                    "status": "unknown",
                    "last_message": "",
                    "last_code": "",
                },
            )

            telemetry_path = summary_path.with_name(
                "history-validation-summary.telemetry.json"
            )
            self.assertTrue(
                telemetry_path.exists(),
                "Telemetry export was not produced (fast target)",
            )
            telemetry_payload = json.loads(telemetry_path.read_text(encoding="utf-8"))
            self.assertEqual(telemetry_payload.get("total_entries"), 0)
            self.assertEqual(telemetry_payload.get("gating_drop_total"), 0)
            self.assertIn("generated_at", telemetry_payload)
            self.assertEqual(telemetry_payload.get("top_gating_reasons"), [])
            self.assertEqual(telemetry_payload.get("top_gating_sources"), [])
            self.assertEqual(telemetry_payload.get("streaming_status"), "unknown")
            self.assertEqual(telemetry_payload.get("last_drop_message"), "none")
            self.assertIsNone(telemetry_payload.get("last_drop_code"))

        def test_make_history_guardrail_checklist_outputs_helper(self) -> None:
            """Guardrail: checklist target should surface the manual telemetry commands."""

            repo_root = Path(__file__).resolve().parents[1]
            result = subprocess.run(
                ["make", "history-guardrail-checklist"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.fail(
                    "make history-guardrail-checklist failed:\n"
                    f"exit: {result.returncode}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
                )

            output = result.stdout
            self.assertIn("History guardrail checklist", output)
            self.assertIn(
                "python3 scripts/tools/history-axis-validate.py --summary-path",
                output,
            )
            self.assertIn(
                "scripts/tools/run_guardrails_ci.sh request-history-guardrails",
                output,
            )
            self.assertIn("make request-history-guardrails", output)


else:
    if not TYPE_CHECKING:

        class MakeRequestHistoryGuardrailsTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass
